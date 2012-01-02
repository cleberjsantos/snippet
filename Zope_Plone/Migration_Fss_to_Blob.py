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

import pdb
import os
import sys

log_file = os.path.join('.', 'log_%s%s' % (datetime.now().strftime('%Y%m%d%H%M%S') ,'.log'))
ploneid = 'PLONESITE ID HERE'
pt = ('News Item','Image','File')

def log2file(row):
    global log_file
    arq = open(log_file, 'a+')
    arq.write(row)
    arq.write('\n')
    arq.close()

def log(*args):
    aa = []
    for arg in args:
        print arg,
        aa.append(str(arg))
    print
    aa = ' '.join(aa)
    log2file(aa)

def do_debugger(type, value, tb):
    log(value.args)
    log('tb value:', value)
    log('TB:\n', tb)

    pdb.pm()

def main():
    global app

    attr_storage = AttributeStorage()
    fss_storage = FileSystemStorage()
    
    app = makerequest(app)
    
    _policy = PermissiveSecurityPolicy()
    _oldpolicy = setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

    global portal, ct
    
    portal = app[ploneid]
    setSite(portal)
    
    # Initialization
    log('Initialized at', datetime.now().isoformat())
    
    ct = getToolByName(portal, 'portal_catalog')
    fssfiles = ct.searchResults({'portal_type':pt})
    
    for fssfile in fssfiles:
        log('Migrating: [%s] %s in %s ... ' %(fssfile.Type,fssfile.id, fssfile.getPath()))
    
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
    
        # Cleaning the storage 
        fss_storage.unset(f_tp, obj)
    
        field.set(obj, content)
        field.setContentType(obj, mimetype)
        field.setFilename(obj,obj.id)
    
        log('Transaction commit and Data.fs synchronism.')
        transaction.commit()
        app._p_jar.sync()
    
    noSecurityManager()
    
    transaction.savepoint(1)
    log('Transaction commit and Data.fs synchronism.')
    transaction.commit()
    app._p_jar.sync()

    log('Completed at', datetime.now().isoformat())

if __name__ == '__main__':
    sys.excepthook = do_debugger
    main()
else:
    pdb.set_trace()
