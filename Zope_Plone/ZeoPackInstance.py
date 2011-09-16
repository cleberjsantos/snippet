# -*- coding: utf-8 -*-
# Warn: This code run only Zeo is installed.
#
# Run code: ./bin/instance run initpack.py

__author__ = """Cleber J Santos <cleber@simplesconsultoria.com.br>"""
__docformat__ = 'plaintext'


import logging
import transaction
from os import path, environ
from Testing.makerequest import makerequest

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy
from Products.CMFCore.tests.base.security import OmnipotentUser
from zope.app.component.hooks import setHooks, setSite
from AccessControl.SecurityManagement import noSecurityManager

import socket
from datetime import datetime
from ZEO.ClientStorage import ClientStorage

app = makerequest(app)
_policy = PermissiveSecurityPolicy()
_oldpolicy = setSecurityPolicy(_policy)
newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

# Path instance log 
logpath = '%s/%s/pack.log' %(str(path.join(environ.get('INSTANCE_HOME',''), 'var').split('/parts')[0]),'var/log/')

# Host, Port and days for Pack
host = 'IP OR HOST'
port = PORT NUMBER
addr = host, int(port)
wait = True
days = 7

# Log initialize
logger = logging.getLogger('Instance Pack')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(logpath)
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


cs = ClientStorage(addr,storage='1',wait=wait,read_only=True,username=None,password=None,realm=None)
logger.info('Pack initialize \n ---------------------------------')

cs.pack(wait=wait, days=int(days))

noSecurityManager()

transaction.savepoint(1)
transaction.commit()
app._p_jar.sync()

logger.info('Pack finally \n ---------------------------------')
