# -*- coding: utf-8 -*-
# Install iw.fss products in your instance.
# Search and comment the code: <include package="iw.fss" file="atct.zcml" /> in $BUILDOUT/parts/instance/etc/*.zcml
# Run the script: ./bin/instance run migrator_fss_to_blob.py
#
# TODO:
#   - Add the migration code for migrate to Blob eg.:  self.restrictedTraverse('/@@blob-file-migration') or self.restrictedTraverse('/@@image-migration')
#
__author__ = """Cleber J Santos <cleber@simplesconsultoria.com.br>"""
__docformat__ = 'plaintext'

from cStringIO import StringIO
from Products.Archetypes.Storage import AttributeStorage
from iw.fss.FileSystemStorage import FileSystemStorage
from ZODB.blob import BlobStorage
import transaction
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from zope.app.component.hooks import setHooks, setSite
from AccessControl.SecurityManagement import noSecurityManager
from mimetypes import guess_type


attr_storage = AttributeStorage()
fss_storage = FileSystemStorage()

# Usado no Plone Site do Ciência Hoje
ploneid = 'PLONESITE ID HERE'
pt = ('News Item','Image','File')

app = makerequest(app)

_policy = PermissiveSecurityPolicy()
_oldpolicy = setSecurityPolicy(_policy)
newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

portal = app[ploneid]
setSite(portal)


print 'Iniciado as ',
print datetime.now().isoformat()

ct = getToolByName(portal, 'portal_catalog')
fssfiles = ct.searchResults({'portal_type':pt})

for fssfile in fssfiles:
    print 'Migrando: %s em %s ... ' %(fssfile.id, fssfile.getPath()),

    obj = portal.restrictedTraverse(fssfile.getPath())

    try:
        f_tp = 'image'
        field = obj.Schema()[f_tp]
    except KeyError, e:
        f_tp = 'file'
        field = obj.Schema()[f_tp]


    fieldstorage = field.storage

    try:
        mimetype = field.getContentType(obj)
    except:
        mimetype = obj.getContentType()

    content = StringIO(str(fss_storage.get(f_tp, obj)))

    # Limpando o storage
    fss_storage.unset(f_tp, obj)

    field.set(obj, content)
    field.setContentType(obj, mimetype)
    field.setFilename(obj,obj.id)

    print 'OK'

    print ''
    print 'Commit da transacao e sinconismo do Data.fs'
    transaction.commit()
    app._p_jar.sync()
    print ''

noSecurityManager()

transaction.savepoint(1)
print 'Commit da transacao e sinconismo do Data.fs'
transaction.commit()
app._p_jar.sync()

print 'Finalizado as ',
print datetime.now().isoformat()
