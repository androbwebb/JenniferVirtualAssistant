import inflect
import datetime
import semantic.dates

from lessons.base.plugin import JenniferResponsePlugin
from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment


class JenniferTimePlugin(JenniferResponsePlugin):

    PRIORITY = 999
    VERBOSE_NAME = "Tell the time"
    REQUIRES_NETWORK = False

    @classmethod
    def is_asking_for_time(cls, tags):
        """Tests if asking for time"""
        need_these = [
            ('what', 'WP'),  # what as a 'WH-pronoun'
            ('time', 'NN'),  # time as a noun
        ]

        return all([x in tags for x in need_these])

    @classmethod
    def is_asking_for_date(cls, tags):
        """Tests if asking for date"""
        need_these = [
            ('what', 'WP'),  # what as a 'WH-pronoun'
        ]
        answer = all([x in tags for x in need_these])

        any_of_these = [
            ('day', 'NN'),
            ('date', 'NN'),
        ]
        answer = answer and any([x in tags for x in any_of_these])

        return answer

    def can_respond(self, **kwargs):
        tags = kwargs.get('tags')
        return JenniferTimePlugin.is_asking_for_time(tags) or JenniferTimePlugin.is_asking_for_date(tags)

    def respond(self, **kwargs):
        tags = kwargs.get('tags')
        plain_text = kwargs.get('plain_text')

        the_time = datetime.datetime.now()

        if JenniferTimePlugin.is_asking_for_time(tags):
            hour = the_time.strftime('%I').lstrip('0')
            return JenniferResponse(self, [
                JenniferTextResponseSegment(the_time.strftime('{}:%M %p'.format(hour)))
            ])
        elif JenniferTimePlugin.is_asking_for_date(tags):
            # Could be asking "what was the date _____", "what is the date", "what is the date _____", let's parse
            possible_dates = semantic.dates.extractDates(plain_text)

            def time_format(dt_obj):
                inflect_eng = inflect.engine()
                date_format = '%A, %B {}, %Y'.format(inflect_eng.ordinal(dt_obj.strftime('%d')))
                return dt_obj.strftime(date_format)

            # Asking for date today
            if not possible_dates:
                response = 'Today\'s date is {}'.format(time_format(the_time))
            else:
                # See if they specified a day?
                the_time = possible_dates[0]
                response = "{}".format(time_format(the_time))

            return JenniferResponse(self, [
                JenniferTextResponseSegment(response)
            ])
