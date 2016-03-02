import unittest
import mock
from tests.testclient import JenniferTestClient
from tests.testbrain import JenniferTestBrain

from tests.mocks import mock_can_respond_true

from lessons.JenniferTimePlugin.plugin import JenniferTimePlugin
from lessons.JenniferFindMyIphonePlugin.plugin import JenniferFindMyIphonePlugin
from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment


class ClientTests(unittest.TestCase):

    def setUp(self):
        self.brain = JenniferTestBrain(always_allow_plugins=[JenniferFindMyIphonePlugin])

    def test_garbage_input(self):
        inputs = [
            "jashg asfsahf ashdf saf sd"
        ]
        client = JenniferTestClient(self.brain, inputs)

        self.assertEqual(len(client.output_list), 1)

        response = client.output_list[0]
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))
        self.assertEqual(response.to_text(), self.brain.UNSURE_TEXT)

    @mock.patch.object(JenniferTimePlugin, "PRIORITY", 0)
    @mock.patch.object(JenniferFindMyIphonePlugin, "PRIORITY", 0)
    @mock.patch.object(JenniferTimePlugin, "can_respond", mock_can_respond_true)
    @mock.patch.object(JenniferFindMyIphonePlugin, "can_respond", mock_can_respond_true)
    @mock.patch.object(JenniferTimePlugin, "respond")
    @mock.patch.object(JenniferFindMyIphonePlugin, "respond")
    def test_same_priority(self, iphone_respond_mock, time_respond_mock):
        inputs = [
            'what is the time',
            'no',
            'yes'
        ]
        client = JenniferTestClient(self.brain, inputs)

        # Should have said:
        #    Which lesson applies?
        #    Find my iPhone?
        #    Time?
        #    (time's response)
        self.assertEqual(len(client.output_list), 4)

        # Get first reponse, make sure it's "Which Lesson Applies?"
        response = client.output_list[0]
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)
        self.assertEqual(response.to_text(), self.brain.MULTIPLE_LESSONS_APPLY)

        # Combine both of the verbose names:
        verbose_names = [JenniferTimePlugin.VERBOSE_NAME, JenniferFindMyIphonePlugin.VERBOSE_NAME]
        for indx in range(1,2):
            response = client.output_list[indx]

            # Make sure it's a response with one text segment
            self.assertTrue(isinstance(response, JenniferResponse))
            self.assertEqual(len(response.segments), 1)

            # Make sure the segment has the verbose name
            self.assertTrue(response.to_text().replace('?', ''), verbose_names)

        # Make sure only one was called (Because they may have been presented to user in reverse order)
        self.assertTrue(iphone_respond_mock.called or time_respond_mock.called)
        self.assertFalse(iphone_respond_mock.called and time_respond_mock.called)

    @mock.patch.object(JenniferTimePlugin, "PRIORITY", 0)
    @mock.patch.object(JenniferFindMyIphonePlugin, "PRIORITY", 20)
    @mock.patch.object(JenniferTimePlugin, "can_respond", mock_can_respond_true)
    @mock.patch.object(JenniferFindMyIphonePlugin, "can_respond", mock_can_respond_true)
    @mock.patch.object(JenniferTimePlugin, "respond")
    @mock.patch.object(JenniferFindMyIphonePlugin, "respond")
    def test_multiple_can_respond(self, iphone_respond_mock, time_respond_mock):
        inputs = [
            'what is the time'
        ]
        client = JenniferTestClient(self.brain, inputs)

        # Should have just run the time, because it's higher priority
        self.assertEqual(len(client.output_list), 1)

        # Make sure only one was caled
        self.assertTrue(time_respond_mock.called)
        self.assertFalse(iphone_respond_mock.called)