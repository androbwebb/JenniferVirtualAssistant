import unittest
import datetime
from tests.testclient import JenniferTestClient
from tests.testbrain import JenniferTestBrain

from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment

from lessons.JenniferTimePlugin.plugin import JenniferTimePlugin


class JenniferTimePluginTests(unittest.TestCase):

    def setUp(self):
        self.brain = JenniferTestBrain()
        self.brain.disable_unsure_response()

    def test_time(self):
        inputs = [
            "what time is it?"
        ]
        client = JenniferTestClient(self.brain, inputs)
        client.run()

        self.assertEqual(len(client.output_list), 1)

        response = client.output_list[0]
        self.assertEqual(JenniferTimePlugin.__name__, response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))

        now = datetime.datetime.now()
        should_be_in = [now.strftime(code) for code in ['%M', '%p']]
        for time_str in should_be_in:
            self.assertIn(time_str, response.to_text())

    def test_date_today(self):
        inputs = [
            "what is the date?"
        ]
        client = JenniferTestClient(self.brain, inputs)
        client.run()

        self.assertEqual(len(client.output_list), 1)

        response = client.output_list[0]
        self.assertEqual(JenniferTimePlugin.__name__, response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))

        now = datetime.datetime.now()
        should_be_in = [now.strftime(code) for code in ['%A', '%B', '%d', '%Y']]
        for time_str in should_be_in:
            self.assertIn(time_str, response.to_text())

    def test_date_tomorrow(self):
        inputs = [
            "what is the date tomorrow?"
        ]
        client = JenniferTestClient(self.brain, inputs)
        client.run()

        self.assertEqual(len(client.output_list), 1)

        response = client.output_list[0]
        self.assertEqual(JenniferTimePlugin.__name__, response.response_creator)  # Make sure the time plugin responded
        self.assertTrue(isinstance(response, JenniferResponse))
        self.assertEqual(len(response.segments), 1)

        segment = response.segments[0]
        self.assertTrue(isinstance(segment, JenniferTextResponseSegment))

        now = datetime.datetime.now() + datetime.timedelta(days=1)
        should_be_in = [now.strftime(code) for code in ['%A', '%B', '%d', '%Y']]
        for time_str in should_be_in:
            self.assertIn(time_str, response.to_text())
