from ioclients import JenniferClientSupportsResponders
from lessons.base.responses import JenniferTextResponseSegment, JenniferImageReponseSegment, \
    JenniferLinkResponseSegement


class JenniferTestClient(JenniferClientSupportsResponders):

    ALLOWED_RESPONSE_TYPES = [JenniferTextResponseSegment, JenniferImageReponseSegment, JenniferLinkResponseSegement]

    def __init__(self, brain, input_list, debug=False):
        """
        All input will be taken from `input_list`
        All output will be saved to output_list
        """
        assert isinstance(input_list, list)
        self.input_list = input_list
        self.output_list = []
        self.debug = debug
        JenniferClientSupportsResponders.__init__(self, brain)

    # Overriding some required methods (test client is a special case
    def collect_input(self):
        try:
            popped = self.input_list.pop(0)
            if self.debug:
                print(f'INPUT: {popped}')
            return popped
        except IndexError:
            raise Exception(f'Prompted for input: \"{self.output_list[-1].to_text()}\", but no input found')

    def give_output(self, response_obj):
        if self.debug:
            print(f'OUTPUT: {response_obj.to_text()}')
        self.output_list.append(response_obj)

    def run(self):
        while len(self.input_list):
            text = self.collect_input()
            response = self.call_brain(text)
            if response:
                self.give_output(response)
