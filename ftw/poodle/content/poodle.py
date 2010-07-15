from zope.interface import implements
from zope import schema, component

from Products.Archetypes import atapi

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import base

from Products.ATContentTypes.content import schemata
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from ftw.poodle import poodleMessageFactory as _
from ftw.poodle.interfaces import IPoodle, IPoodleVotes
from ftw.poodle.config import PROJECTNAME

PoodleSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.LinesField(
        name='users',
        vocabulary_factory="ftw.poodle.users",
        enforceVocabulary=True,
        widget=atapi.InAndOutWidget
        (
            label=_(u'ftwpoodle_label_users', default=u'Users'),
            actb_expand_onfocus=1,
        ),
        required=1,
        multivalued=1
    ),

    DataGridField(
        name='dates',
        allow_empty_rows = False,
        widget=DataGridWidget(
            auto_insert = True,  
            columns= {"date": Column(_(u"ftwpoodle_desc_date", default="Date (TT. MM. JJJJ)")), "duration": Column(_(u"ftwpoodle_desc_duration", default="Time / Duration"))},
            label=_(u'ftwpoodle_label_dates', default=u'Dates'),
        ),
        columns= ("date", "duration")
    ),
))

schemata.finalizeATCTSchema(PoodleSchema, moveDiscussion=False)


class Poodle(base.ATCTContent):
    """ A 'doodle'-like content type that helps finding a date for a meeting """
    implements(IPoodle)
    
    security = ClassSecurityInfo()
    
    portal_type = "Meeting poll"
    schema = PoodleSchema


    security.declarePrivate("getDatesHash")
    def getDatesHash(self):
        return [str(hash('%s%s' % (a['date'],a['duration']))) for a in self.getDates()]

    security.declarePrivate("getPoodleData")
    def getPoodleData(self):
        if IPoodle.providedBy(self):
            return IPoodleVotes(self).getPoodleData()
        return {}
    
    def get_poodle_votes(self):
        if IPoodle.providedBy(self):
            return IPoodleVotes(self)
    
    security.declarePrivate("setPoodleData")
    def setPoodleData(self, data):
        if IPoodle.providedBy(self):
            IPoodleVotes(self).setPoodleData(data)

    security.declarePrivate("updatePoodleData")        
    def updatePoodleData(self):
        votes = self.get_poodle_votes()
        votes.updateDates()
        votes.updateUsers()
        self.updateSharing()
        
    security.declarePrivate("updateSharing")
    def updateSharing(self):
        """ 
        Allow the selected Users to view the object
        """
        users = self.getUsers()
        wanted_roles = [u'Reader',]
        for user in users:
            self.manage_setLocalRoles(user, wanted_roles)
        self.reindexObjectSecurity()
        # XXX: remove users?

    
    security.declarePrivate("saveUserData")
    def saveUserData(self, userid, dates):
        votes = self.get_poodle_votes()
        poodledata = votes.getPoodleData()
        if userid in poodledata['users'].keys():
            for date in poodledata["dates"]:
                poodledata['users'][userid][date] = bool(date in dates)


            
        
atapi.registerType(Poodle, PROJECTNAME)
