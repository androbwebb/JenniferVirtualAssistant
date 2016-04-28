import unittest
import mock
from email.message import Message

from tests.mocks import test_get_gmail_accounts, mock_imap_get_first_text_block, mock_imap_get_unread_emails, \
    mock_imap_do_nothing, mock_imap_status, mock_imap_delete, mock_imap_mark_read
from tests.testclient import JenniferTestClient
from tests.testbrain import JenniferTestBrain

from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment

from lessons.JenniferGmailPlugin.plugin import JenniferGmailPlugin
from lessons.JenniferGmailPlugin.logic import GmailImapWrapper
from lessons.JenniferGmailPlugin.shared_settings import JenniferGmailSharedSettings


@mock.patch.object(GmailImapWrapper, '_get_status', mock_imap_status)
@mock.patch.object(GmailImapWrapper, 'login_and_select', mock_imap_do_nothing)
@mock.patch.object(GmailImapWrapper, 'logout_and_close', mock_imap_do_nothing)
@mock.patch.object(GmailImapWrapper, 'get_unread_emails', mock_imap_get_unread_emails)
@mock.patch.object(GmailImapWrapper, 'get_first_text_block', mock_imap_get_first_text_block)
@mock.patch.object(JenniferGmailSharedSettings, 'get_accounts', test_get_gmail_accounts())
class JenniferGmailPluginTests(unittest.TestCase):

    def setUp(self):
        self.brain = JenniferTestBrain(always_allow_plugins=[JenniferGmailPlugin])
        self.brain.disable_unsure_response()

    def test_counting(self):
        inputs = [
            "count unread emails"
        ]
        client = JenniferTestClient(self.brain, inputs)
        client.run()

        self.assertEqual(len(client.output_list), 2)

        response = client.output_list[0]
        self.assertEqual("JenniferGmailPlugin", response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))
        self.assertIn("checking", response.to_text().lower())

        response = client.output_list[1]
        self.assertEqual("JenniferGmailPlugin", response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))

        self.assertIn("you have 2 new emails", response.to_text().lower())

    @mock.patch.object(GmailImapWrapper, 'read_message')
    @mock.patch.object(GmailImapWrapper, 'delete_message')
    def test_check_email(self, delete_mock, read_mock):
        inputs = [
            "read my emails",
            "no", "no",  # Email 1
            "no", "no",  # Email 2
            "no", "no",  # Email 3
            "no", "no",  # Email 4
            "no", "no",  # Email 5
            "no", "no",  # Email 6
            "no", "no",  # Email 7
            "no", "no",  # Email 8
            "no", "no",  # Email 9
            "no", "no",  # Email 10
        ]
        client = JenniferTestClient(self.brain, inputs)
        client.run()

        self.assertGreaterEqual(len(client.output_list), 1)

        response = client.output_list[0]
        self.assertEqual("JenniferGmailPlugin", response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))
        self.assertIn("checking", response.to_text().lower())

        response = client.output_list[1]
        self.assertEqual("JenniferGmailPlugin", response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))

        self.assertIn("you have", response.to_text().lower())
        self.assertIn("email", response.to_text().lower())

        self.assertFalse(delete_mock.called)
        self.assertFalse(read_mock.called)

    @mock.patch.object(GmailImapWrapper, 'read_message')
    @mock.patch.object(GmailImapWrapper, 'delete_message')
    def test_delete_read_email(self, delete_mock, read_mock):
        inputs = [
            "read my emails",
            "yes", "no",  # Email 1
            "no", "yes",  # Email 2
            "no", "no",   # Email 3
            "no", "no",   # Email 4
            "no", "no",   # Email 5
            "no", "no",   # Email 6
            "no", "no",   # Email 7
            "no", "no",   # Email 8
            "no", "no",   # Email 9
            "no", "no",   # Email 10
        ]
        client = JenniferTestClient(self.brain, inputs)
        client.run()

        self.assertTrue(delete_mock.called)
        self.assertTrue(read_mock.called)