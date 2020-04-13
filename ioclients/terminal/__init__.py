from ioclients import JenniferClientSupportsResponders, JenniferClientSupportsNotification
from lessons.base.responses import JenniferTextResponseSegment, JenniferImageReponseSegment, \
    JenniferLinkResponseSegement


class JenniferTerminalClient(JenniferClientSupportsNotification, JenniferClientSupportsResponders):

    ALLOWED_RESPONSE_TYPES = [JenniferTextResponseSegment, JenniferLinkResponseSegement]

    def __init__(self, brain):
        self.prompt = '> '
        # Must call JenniferNotificationClientBase.init before JenniferClientBase.init
        #   because JenniferClientBase.init is blocking
        JenniferClientSupportsNotification.__init__(self, brain)
        JenniferClientSupportsResponders.__init__(self, brain)

    def collect_input(self):
        return input(self.prompt)

    def give_output(self, response_obj):
        response = response_obj.to_text()
        print(f'JENNIFER: {response}')

    def regain_control(self):
        self.prompt = '> '

    def give_up_control(self):
        self.prompt = '>>> '
