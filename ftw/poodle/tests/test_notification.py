from ftw.notification.email.interfaces import IEMailRepresentation
from ftw.notification.email.interfaces import ISubjectCreator
from ftw.poodle.interfaces import IPoodle
from ftw.poodle.testing import POODLE_VOTES_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView


class TestNotificationAdapters(MockTestCase):

    layer = POODLE_VOTES_ZCML_LAYER

    def test_subject_creator(self):
        poodle = self.providing_stub([IPoodle])
        request = self.stub_request()
        self.expect(poodle.REQUEST).result(request)

        mtool = self.stub()
        member = self.stub()
        self.mock_tool = self.mock_tool(mtool, 'portal_membership')
        self.expect(mtool.getAuthenticatedMember()).result(member)
        self.expect(member.getProperty('fullname')).result('Hugo Boss')

        self.replay()

        subject = ISubjectCreator(poodle)(poodle)
        self.assertEquals(
            subject, u'The User Hugo Boss has filled out your poodle')

    def test_email_representation(self):
        # poodle and request stuff
        poodle = self.providing_stub([IPoodle])
        request = self.stub_request()
        response = self.stub_response()
        self.expect(poodle.REQUEST).result(request)
        self.expect(poodle.absolute_url).result(
            'http://localhost:8080/platform/poodle-1')

        # portal state mocks
        portal_state = self.stub()
        self.mock_adapter(portal_state, IBrowserView,
            [Interface, Interface], name='plone_portal_state')
        self.expect(portal_state(poodle, request)).result(portal_state)
        portal = self.stub()
        self.expect(portal_state.portal_url).result(
            'http://localhost:8080/platform')
        self.expect(portal_state.portal).result(portal)
        self.expect(portal.__call__()).result(portal)
        self.expect(portal()).result(portal)
        self.expect(portal.Title()).result('My poodle portal')

        # member tool mocks
        mtool = self.stub()
        member = self.stub()
        self.mock_tool(mtool, 'portal_membership')
        self.expect(mtool.getAuthenticatedMember()).result(member)
        self.expect(member.getProperty('fullname')).result(None)
        self.expect(member.id).result('hugo.boss')

        prop_tool = self.stub()
        self.mock_utility(prop_tool, IPropertiesTool)

        self.replay()

        email = IEMailRepresentation(poodle)

        self.assertEquals(
            email.template(),'\n\n The user hugo.boss\n has entered his data into the meeting poll at\n http://localhost:8080/platform/poodle-1\n on the website My poodle portal\n at http://localhost:8080/platform\n\n\n')
