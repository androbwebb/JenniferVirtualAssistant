import os
import pyglet
from ioclients.terminal import JenniferTerminalClient
from lessons.base.responses import ALL_RESPONSE_TYPES


class JenniferTerminalWithSoundClient(JenniferTerminalClient):

    ALLOWED_RESPONSE_TYPES = JenniferTerminalClient.ALLOWED_RESPONSE_TYPES

    @property
    def _on_beep_file(self):
        return os.path.join(os.path.dirname(__file__), '..', 'assets', 'beep_short_on.wav')

    @property
    def _off_beep_file(self):
        return os.path.join(os.path.dirname(__file__), '..', 'assets', 'beep_short_off.wav')

    @property
    def _notification_beep_file(self):
        return os.path.join(os.path.dirname(__file__), '..', 'assets', 'chime_bell_ding.wav')

    @staticmethod
    def play_sound(sound_file):
        if os.path.isfile(sound_file):
            music = pyglet.media.load(sound_file)
            music.play()

    def regain_control(self):
        JenniferTerminalClient.regain_control(self)
        self.play_sound(self._on_beep_file)

    def give_up_control(self):
        JenniferTerminalClient.give_up_control(self)
        self.play_sound(self._off_beep_file)

    def give_output(self, response_obj):
        JenniferTerminalClient.give_output(self, response_obj)
        response = response_obj.to_text()
        os.system('say "{}"'.format(response))

    def new_notification(self):
        """Called whenever a new notification has been pushed into the queue"""
        self.play_sound(self._notification_beep_file)
        JenniferTerminalClient.new_notification(self)

