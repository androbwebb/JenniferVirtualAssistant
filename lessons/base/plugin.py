import Queue
import os
import atexit
import inspect
from getpass import getpass
from apscheduler.schedulers.background import BackgroundScheduler
from abc import abstractmethod, abstractproperty
from lessons.base.decorators import intent
import logging
logging.basicConfig()


class JenniferPluginBase(object):
    """
    Provides a base for any type of plugin
    """
    def __init__(self, brain, settings=None, profile=None):
        self.brain = brain
        self.settings = settings
        self.profile = profile

    def set_settings(self, settings):
        self.settings = settings
        return self

    def set_profile(self, profile):
        self.profile = profile
        return self

    @abstractproperty
    def REQUIRES_NETWORK(self):
        return True

    @property
    def settings_name(self):
        return os.path.basename(os.path.dirname(inspect.getfile(self.__class__)))

    @staticmethod
    def initialize_settings(settings_template_dict):
        """
        Should use the commandline to get all the info needed for settings and return as a dict
        :return: return the new settings dict to be saved
        """

        for key, val in settings_template_dict.iteritems():
            # Ignore enabled
            if key == 'enabled':
                continue

            print "Please provide a {}".format(key)
            if val != "password":
                new_value = raw_input("> ")
            else:
                new_value = getpass("> ")

            if isinstance(val, bool):
                settings_template_dict[key] = new_value.lower() == 'true'
            if isinstance(val, (str, unicode)):
                settings_template_dict[key] = unicode(new_value)
            if isinstance(val, int):
                settings_template_dict[key] = int(new_value)
            if isinstance(val, float):
                settings_template_dict[key] = float(new_value)
            if isinstance(val, dict):
                settings_template_dict[key] = JenniferPluginBase.initialize_settings(val)

        return settings_template_dict


class JenniferResponsePlugin(JenniferPluginBase):
    """
    A plugin that will partake in text conversation
    """

    # Higher = less priority
    PRIORITY = 0

    @abstractproperty
    def VERBOSE_NAME(self):
        return self.__class__.__name__

    @abstractmethod
    def can_respond(self, **kwargs):
        """
        Should be considered a `quick` call, to see if this plugin can/should be responsible for responding.
        Use either the nltk tags or text searching.
        :param settings: relevant settings
        :param tags: nltk tags (all lowercase)
        :param text_input: text (all lowercase)
        :return: Boolean
        """
        pass

    @abstractmethod
    def respond(self, **kwargs):
        """
        Will only be called if self.can_respond() returned True.
        :param settings: relevant settings
        :param tags: nltk tags
        :param plain_text: text
        :return: JenniferResponse. The correct response to the input
        """
        pass

    @staticmethod
    def tags_dict_by_tag(tags):
        reorganized = {}
        for tag in tags:
            key = tag[1]
            reorganized.setdefault(key, []).append(tag)
        return reorganized

    def _intent_dictionary(self, tags, plain_text):
        """
        Scans all of the methods decorated with @intent, evaluates them and returns a dict.
        The keys have '_is_intent' stripped off.
        :param tags:
        :param plain_text:
        :return:
        """
        def methods_with_decorator(cls, decorator):
            """
                Returns all methods in CLS with DECORATOR as the
                outermost decorator.

                DECORATOR must be a "registering decorator"; one
                can make any decorator "registering" via the
                makeRegisteringDecorator function.
            """
            for maybeDecorated in cls.__dict__.values():
                if hasattr(maybeDecorated, 'decorator'):
                    if maybeDecorated.decorator == decorator:
                        yield maybeDecorated

        return_dict = {}
        for func in methods_with_decorator(self.__class__, intent):
            func_name = func.__name__
            intent_name = func.__name__.replace('_is_intent_', '')
            return_dict[intent_name] = getattr(self, func_name)(tags, plain_text)

        return return_dict


class JenniferNotificationPlugin(JenniferPluginBase):
    """
    A plugin that will check for updates and provide notification queues.
    """

    # How often to run (default = 1hr)
    RUN_EVERY_N_SECONDS = 60 * 60

    def __init__(self, brain, settings=None, profile=None):
        JenniferPluginBase.__init__(self, brain, profile, settings)
        self.queue = Queue.PriorityQueue()
        self.create_scheduled_job()

    @abstractmethod
    def run(self):
        pass

    @abstractproperty
    def PRIORITY(self):
        # Higher = less priority
        return 1

    def create_scheduled_job(self):
        sheduler = BackgroundScheduler(timezone="UTC", daemon=True)
        sheduler.start()
        sheduler.add_job(self.run, trigger='interval', seconds=self.RUN_EVERY_N_SECONDS)
        atexit.register(lambda: sheduler.shutdown(wait=False))

    def insert_into_queue(self, data, priority=None):
        if not priority:
            priority = self.PRIORITY
        notification = (priority, data)
        self.queue.put(notification)
