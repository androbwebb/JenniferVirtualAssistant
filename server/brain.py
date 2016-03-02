import os
import json
import atexit
import nltk
import pkgutil
import Queue
import random
import logging
from pytz import common_timezones, timezone
from apscheduler.schedulers.background import BackgroundScheduler

from nltk.tag.perceptron import PerceptronTagger

from lessons.base.plugin import JenniferResponsePlugin, JenniferNotificationPlugin
from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment

logging.basicConfig()


class JenniferBrain(object):

    UNSURE_TEXT = "Sorry, I can't help with that"
    MULTIPLE_LESSONS_APPLY = 'Which one of my lessons applies here?'

    def __init__(self, allow_network_plugins=False, always_allow_plugins=None):
        self._initialize_paths()

        # Lessons + Settings
        self.allow_network_plugins = allow_network_plugins
        self.always_allow_plugins = always_allow_plugins or []
        self.responders = []
        self.notifiers = []
        self.notification_queue = Queue.PriorityQueue()
        self._load_profile_and_settings()

        # Requires self.database & self.settings
        self._load_lessons()

        # Just to save time later
        self.nltktagger = PerceptronTagger()
        self.tagset = None

        # Notifications
        self.notification_clients = []
        self._initialize_background_tasks()

    def _initialize_paths(self):
        """Create the paths needed"""
        self.base_path = os.path.join(os.path.dirname(__file__), '..')
        self.profile_file = os.path.join(self.base_path, 'profile.json')
        self.lessons_path = os.path.join(self.base_path, 'lessons')

    def _load_lessons(self):
        """
        Search the lessons/ package for lessons & store them in sorted order by priority
        :return:
        """
        pkgs = [n for _, n, _ in pkgutil.iter_modules(['lessons']) if n != 'base']
        for name in pkgs:
            exec 'import lessons.' + name + '.plugin'

        responders = [cls(self).set_profile(self.database['profile']) for cls in JenniferResponsePlugin.__subclasses__() if self._is_lesson_allowed(cls)]
        self.notifiers = [cls(self).set_profile(self.database['profile']) for cls in JenniferNotificationPlugin.__subclasses__() if self._is_lesson_allowed(cls)]

        for r in (responders + self.notifiers):
            r.set_settings(self._get_settings_for_lesson(r))

        self.responders = sorted(responders, key=lambda l: l.PRIORITY)

    def _is_lesson_allowed(self, lesson_cls):
        if lesson_cls in self.always_allow_plugins:
            return True
        if lesson_cls.REQUIRES_NETWORK and not self.allow_network_plugins:
            return False
        return True

    def _load_profile_and_settings(self):
        """
        Load the profile
        :return:
        """
        try:
            with open(self.profile_file, 'r+') as profile_file:
                data = json.loads(profile_file.read(), strict=False)
                self.database = data
                if 'profile' in self.database and 'settings' in self.database:
                    profile_file.close()
                    return
        except (IOError, ValueError):
            self.database = {}
            self._init_profile()
            self._save_profile_to_file()

    def _get_settings_for_lesson(self, lesson, lesson_name=None):
        """
        Get the settings dict for the lesson
        (Must be called from a lesson)
        :return:
        """
        if not lesson_name:
            lesson_name = unicode(lesson.settings_name)

        try:
            return self.database['settings'][lesson_name]
        except KeyError:
            if self._test_if_settings_template_exists(lesson):
                print "--------{} SETTINGS--------".format(lesson_name)
                self._add_lesson_to_settings_and_write(lesson)
                return self._get_settings_for_lesson(lesson)
            return {}

    def _settings_template_path_for_lesson(self, lesson):
        """Gets a settings_template for a given lesson"""
        lesson_settings_name = lesson.settings_name
        return os.path.join(self.lessons_path, lesson_settings_name, 'settings_template.json')

    def _test_if_settings_template_exists(self, lesson):
        """Returns if a settings_template for a given lesson"""
        return os.path.isfile(self._settings_template_path_for_lesson(lesson))

    def _add_lesson_to_settings_and_write(self, lesson):
        """Loads a lesson's settings_template, runs an initialization function if available, and copies into DB"""
        lesson_settings_name = lesson.settings_name
        with open(self._settings_template_path_for_lesson(lesson)) as template:
            try:
                # Try to load initial template
                settings_template_dict = json.loads(template.read(), strict=False)
                settings_template_dict = lesson.initialize_settings(settings_template_dict)

                # Push to DB & save
                self.database['settings'][lesson_settings_name] = settings_template_dict
                self._save_profile_to_file()
            except ValueError:
                exit("{} has an invalid settings_template.json".format(lesson_settings_name))

    def _save_profile_to_file(self):
        """Writes to profile.json"""
        with open(self.profile_file, "w+") as f:
            plain_text = json.dumps(self.database, indent=4, sort_keys=True)
            f.write(plain_text)
            f.close()

    def _init_profile(self):
        """Should be run if profile.json doesn't exist"""
        fields = [
            ('first name', 'firstName'),
            ('last name', 'lastName'),
        ]
        location_fields = [
            ('city', 'city', 'New York City'),
            ('region', 'region', 'NY'),
            ('country', 'country', 'US'),
            ('zip', 'zip'),
        ]

        if 'profile' not in self.database:
            for field in fields:
                self.database.update({'profile': {'location':{}}})
                print "What is your {}?".format(field[0])
                self.database['profile'][field[1]] = raw_input("> ")

            self.database['profile']['location'] = {}
            for field in location_fields:
                txt = "What is your {}?".format(field[0])

                if len(location_fields) >= 3:
                    txt += " example: ({})".format(field[2])

                print txt
                self.database['profile']['location'][field[1]] = raw_input("> ")

            while True:
                print "What is your timezone? example: ({})".format(random.choice(common_timezones))
                tz = raw_input('> ')
                if timezone(tz):
                    self.database['profile']['location']['timezone'] = tz
                    break
                else:
                    print "Invalid timezone"

        if 'settings' not in self.database:
            self.database.update({'settings': {'notifications': {'quiet_hours': []}}})

    def _get_profile(self):
        """Get the user's profile"""
        return self.database['profile']

    def take_input(self, text_input, client):
        """
        Search all lessons for lessons that can respond
        :param text_input:
        :return:
        """
        text_input = text_input.lower()
        tokens = nltk.word_tokenize(text_input)
        tags = nltk.tag._pos_tag(tokens, self.tagset, self.nltktagger)

        # TODO: extrap this out to a custom stopwords
        try:
            tags.remove(('please', 'NN'))  # It's common to say 'please' when asking Jennifer something
        except:
            pass

        # Find the lessons that can answer
        respond_to = None
        matching_lessons = [lesson for lesson in self.responders if lesson.can_respond(tags=tags,
                                                                                       client=client,
                                                                                       brain=self,
                                                                                       plain_text=text_input)]

        # No answer
        if len(matching_lessons) == 0:
            self.respond_or_unsure(None, tags, client, text_input)

        # Only one module can respond
        elif len(matching_lessons) == 1:
            respond_to = matching_lessons[0]

        # Multiple lessons can response
        else:
            priority_counts = {}
            for lesson in matching_lessons:
                key = lesson.PRIORITY
                priority_counts.setdefault(key, []).append(lesson)

            # Now we have something like {999: [TimePlugin(), LowPriorityTimePlugin()], 0: [ImportantTimePlugin()]}
            min_priority = min(priority_counts.keys())

            if len(priority_counts[min_priority]) == 1:
                respond_to = priority_counts[min_priority][0]
            else:
                client.give_output_string("brain", self.MULTIPLE_LESSONS_APPLY)
                for lesson in priority_counts[min_priority]:
                    if client.confirm("brain", lesson.VERBOSE_NAME + "?"):
                        # TODO: would be nice to remember this decision.. that's v3.0 though.
                        respond_to = lesson
                        break

        return self.respond_or_unsure(respond_to, tags, client, text_input)

    def respond_or_unsure(self, respond_to, tags, client, text_input):
        try:
            return respond_to.respond(tags=tags,
                                      client=client,
                                      brain=self,
                                      plain_text=text_input)
        except Exception as e:
            return JenniferResponse(self, [
                JenniferTextResponseSegment(self.UNSURE_TEXT)
            ])

    def _initialize_background_tasks(self):
        self.scheduler = BackgroundScheduler(timezone="UTC", daemon=True)
        self.scheduler.start()
        self.scheduler.add_job(self._collect_notifications_from_notifiers, 'interval', seconds=10)
        self.scheduler.add_job(self.push_notifications_to_clients, 'interval', seconds=2)
        atexit.register(lambda: self.scheduler.shutdown(wait=False))

    def _collect_notifications_from_notifiers(self):
        for notification_provider in self.notifiers:
            while not notification_provider.queue.empty():
                self.notification_queue.put(notification_provider.queue.get())

    def register_notification_client(self, client):
        self.notification_clients.append(client)

    def push_notifications_to_clients(self):
        while not self.notification_queue.empty():
            notification = self.notification_queue.get()
            for client in self.notification_clients:
                client.give_output_string("brain", notification[1])
