import Queue
import mpd

from abc import abstractmethod, abstractproperty
from lessons.base.exceptions import JenniferUserWantsToCancelException
from lessons.base.responses import JenniferTextResponseSegment, JenniferResponse, JenniferResponseAbstractSegment


class JenniferClientBase(object):
    POSITIVE_RESPONSES = ['yes', 'ya', 'yea', 'yup', 'affirmative', 'sure']
    NEGATIVE_RESPONSES = ['no', 'na', 'nope', 'negative']
    CANCELED_RESPONSES = ["cancel", "nevermind", "quit", "stop", "bail"]

    @abstractproperty
    def ALLOWED_RESPONSE_TYPES(self):
        pass

    @abstractmethod
    def give_output(self, response):
        pass

    def give_output_string(self, creator, text):
        if isinstance(text, (str, unicode)):
            response_obj = JenniferResponse(creator, [JenniferTextResponseSegment(text)])
        elif issubclass(text.__class__, JenniferResponseAbstractSegment):
            response_obj = JenniferResponse(creator, [text])
        else:
            raise Exception("client.give_output_string must receive a string/unicode or instance of JenniferResponseAbstractSegment")
        return self.give_output(response_obj)


class JenniferClientSupportsResponders(JenniferClientBase):

    def __init__(self, brain):
        self.run_forever = 1
        self.brain = brain
        self.run()

    @abstractmethod
    def collect_input(self):
        pass

    def run(self):
        self.regain_control()
        while self.run_forever:
            text = self.collect_input()

            # There's some input, give up control & call brain
            self.give_up_control()

            response = self.call_brain(text)
            if response:
                self.give_output(response)

            # Lesson is done running, you have control back
            self.regain_control()

    def call_brain(self, text_input):
        response_collection = self.brain.take_input(text_input, self)
        if isinstance(response_collection, JenniferResponse):
            response_collection.filter_responses(self.ALLOWED_RESPONSE_TYPES)
        return response_collection

    def confirm(self, creator, text, additional_positive_responses=None, additional_negative_responses=None, additional_canceled_responses=None):
        """
        A blocking confirmation dialog.
        :param text: text to present user
        :param additional_positive_responses: In a situation where you ask "Do you want to open this website?",
                                              you would send ['open'] as an addition word that is a confirmation
        :param additional_negative_responses:
        :param additional_canceled_responses:
        :return:
        """
        # Set to default empty list
        additional_positive_responses = additional_positive_responses or []
        additional_negative_responses = additional_negative_responses or []
        additional_canceled_responses = additional_canceled_responses or []

        self.give_output_string(creator, text)
        while 1:
            inp = self.collect_input()
            if inp in self.POSITIVE_RESPONSES + additional_positive_responses:
                return True
            if inp in self.NEGATIVE_RESPONSES + additional_negative_responses:
                return False
            if inp in self.CANCELED_RESPONSES + additional_canceled_responses:
                raise JenniferUserWantsToCancelException(inp)

    @abstractmethod
    def regain_control(self):
        """
        Called when Jennifer goes back into passive mode.
        For terminal clients perhaps display a different prompt, and for audible clients, give a beep
        """
        pass

    @abstractmethod
    def give_up_control(self):
        """
        Called when Jennifer goes back into passive mode.
        For terminal clients perhaps display a different prompt, and for audible clients, give a beep
        """
        pass


class JenniferClientSupportsNotification(JenniferClientBase):

    def __init__(self, brain):
        self.notifications = Queue.PriorityQueue()
        self.brain = brain
        self.brain.register_notification_client(self)

    @abstractmethod
    def give_output(self, response):
        pass

    def put_notification(self, data):
        self.notifications.put(data)
        self.new_notification()

    def new_notification(self):
        """Called whenever a new notification has been pushed into the queue"""
        while not self.notifications.empty():
            self.give_output_string("notification", self.notifications.get()[1])


class JenniferClientSupportsMusic(object):
    """ A client that supports mpd streaming from mopidy"""

    def __init__(self, brain, server="127.0.0.1", port=6600):
        self.brain = brain
        self.server = server
        self.port = port
        self._initialize_mpd()

    def _initialize_mpd(self):
        self.mpd = mpd.MPDClient()
        self.mpd.idletimeout = None
        self.mpd.timeout = None
        self.mpd.connect(self.server, self.port)

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def prev_track(self):
        pass

    def next_track(self):
        pass

    def volume(self):
        pass