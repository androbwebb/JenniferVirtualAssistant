import json
import os
from mock import patch

from tests.mocks import test_get_gmail_accounts, mock_imap_status, mock_imap_do_nothing, mock_imap_get_unread_emails, \
    mock_imap_get_first_text_block

from server.brain import JenniferBrain
from lessons.JenniferGmailPlugin.logic import GmailImapWrapper
from lessons.JenniferGmailPlugin.shared_settings import JenniferGmailSharedSettings


class JenniferTestBrain(JenniferBrain):

    def __init__(self, allow_network_plugins=False, always_allow_plugins=None):
        with patch.object(JenniferGmailSharedSettings, 'get_accounts', test_get_gmail_accounts([])):
            JenniferBrain.__init__(self, allow_network_plugins, always_allow_plugins)

    def _initialize_paths(self):
        """Create the paths needed"""
        self.base_path = os.path.join(os.path.dirname(__file__), '..')
        self.profile_file = os.path.join(self.base_path, 'profile.json')
        self.lessons_path = os.path.join(self.base_path, '..', 'lessons')

        # Delete the test profile.
        try:
            os.remove(self.profile_file)
        except OSError:
            pass

    def _add_lesson_to_settings_and_write(self, lesson):
        """Loads a lesson's settings_template, runs an initialization function if available, and copies into DB"""
        lesson_settings_name = lesson.settings_name
        with open(self._settings_template_path_for_lesson(lesson)) as template:
            try:
                # Try to load initial template
                settings_template_dict = json.loads(template.read(), strict=False)
                # Push to DB & save
                self.database['settings'][lesson_settings_name] = settings_template_dict
                self._save_profile_to_file()
            except ValueError:
                exit("{} has an invalid settings_template.json".format(lesson_settings_name))

    def _init_profile(self):
        self.database = {
            "profile": {
                "firstName": "Andrew",
                "lastName": "Webb",
                "location": {
                    "city": "Boston",
                    "region": "Massachusetts",
                    "zip": "02135"
                }
            },
            "settings": {
                "notifications": {
                    "quiet_hours": []
                }
            }
        }

    def disable_unsure_response(self):
        def respond_no_unsure(respond_to, tags, client, text_input):
            return respond_to.respond(tags=tags,
                                      client=client,
                                      brain=self,
                                      plain_text=text_input)

        self.respond_or_unsure = respond_no_unsure
