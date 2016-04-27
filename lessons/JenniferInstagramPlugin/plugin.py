# -*- coding: utf-8-*-
import inflect

from lessons.base.plugin import JenniferResponsePlugin


class JenniferInstagramPlugin(JenniferResponsePlugin):

    PRIORITY = 50
    VERBOSE_NAME = "Instagram"
    REQUIRES_NETWORK = True

    def __init__(self, *args, **kwargs):
        self.pluralize_engine = inflect.engine()
        JenniferResponsePlugin.__init__(self, *args, **kwargs)

    def can_respond(self, **kwargs):
        """
        Test if it can respond
        :param kwargs:
        :return:
        """
        tags = kwargs.get('tags')
        one_verb = [
            ('find', 'VB'),
            ('read', 'VB'),
            ('check', 'VB'),
            ('check', 'NN'),
        ]
        one_of_these = [
            ('instagram', 'NN'),
            ('gram', 'NN')
        ]

        # Need any the verbs in `one_verb` with correct context
        can_repond = any([word in tags for word in one_verb])
        # Need at least one of the words in `one_of_these` with correct context
        can_repond = can_repond and any([word in tags for word in one_of_these])

        return can_repond

    def respond(self, **kwargs):
        """
        Respond to the user
        :param kwargs:
        :return:
        """
        plain_text = kwargs.get('plain_text')
        client = kwargs.get('client')
        client.give_output_string(self, "Checking instagram")
