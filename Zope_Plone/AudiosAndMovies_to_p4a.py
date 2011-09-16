import re
import transaction
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy
from Products.CMFCore.tests.base.security import PermissiveSecurityPolicy, OmnipotentUser
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import setSite
from mimetypes import guess_type
from zope.interface import directlyProvides, directlyProvidedBy

from p4a.video.interfaces import IVideo,IVideoDataAccessor, IMediaActivator, IMediaPlayer, IPossibleVideo, IVideoEnhanced
from p4a.subtyper.interfaces import ISubtyped
from p4a.audio.interfaces import IAudio, IMediaPlayer, IAudioDataAccessor, IPossibleAudio, IAudioEnhanced


class MediasP4aMigration:
    ploneid = 'PLONEID'

    def __init__(self):
        """
        """
        app = makerequest(app)
        _policy = PermissiveSecurityPolicy()
        _oldpolicy = setSecurityPolicy(_policy)

        self.site = app[ploneid]
        setSite(self.site)
        newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))

        self.catalog = getToolByName(site, 'portal_catalog')
        self.searchfiles = self.catalog.searchResults(portal_type='File')

    def moviep4amigration(self):
       """Converting movies to p4a"""
    
       # File extensions don't interfaces apply {'wav':'xwav', 'mid':'midi','rm':'vnd.rn-realaudio','wma':'x-ms-wma'}
       regex = re.compile("\.(mov|avi|wmv)")
    
       moviefiles = [i.getObject() for i in self.searchfiles if guess_type(i.getPath())[0].startswith('video')]
    
       for movies in moviefiles:
          try:
             if regex.search(movies.getId()):
                movies.restrictedTraverse('@@video-config.html').media_activated = True
                IVideo(movies)._load_video_metadata()
          except AttributeError:
             pass
    
       noSecurityManager()
       transaction.savepoint(1)
       transaction.commit()
       app._p_jar.sync()

    
    def audiop4amigration(self):
       """Converting Audios to p4a"""

       regex = re.compile("\.(mp3)")
       audiofiles = [i.getObject() for i in self.searchfiles if guess_type(i.getPath())[0].startswith('audio')]
    
       for audios in audiofiles:
          try:
             if regex.search(audios.getId()):
                audios.restrictedTraverse('@@media-config.html').media_activated = True
                IAudio(audios)._load_audio_metadata()
          except AttributeError:
             pass
    
       noSecurityManager()
       transaction.savepoint(1)
       transaction.commit()
       app._p_jar.sync()
    
    
    def removeinterfaces(obj,ifaces):
       """Remover interface"""
       
       # Eg.
       # from p4a.audio.interfaces import IAudio, IMediaPlayer, IAudioDataAccessor, IPossibleAudio, IAudioEnhanced
       # audiofiles = [i.getObject() for i in self.searchfiles if guess_type(i.getPath())[0].startswith('audio')]
       # for audios in audiofiles:
       #    removeinterfaces(audios,'IAudioEnhanced'):
     
       for itf in ifaces:
          # directlyProvides(objeto,directlyProvidedBy(objeto)-IAudioEnhanced)
          directlyProvides(obj,directlyProvidedBy(obj)-itf)
    
       noSecurityManager()
       transaction.savepoint(1)
       transaction.commit()
       app._p_jar.sync()
