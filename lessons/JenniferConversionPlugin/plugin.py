import inflect
import semantic.units

from lessons.base.plugin import JenniferResponsePlugin
from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment


class JenniferTimePlugin(JenniferResponsePlugin):

    PRIORITY = 200
    VERBOSE_NAME = "Convert Units"
    REQUIRES_NETWORK = False

    def can_respond(self, **kwargs):
        tags = kwargs.get('tags')
        plain_text = kwargs.get('plain_text')

        one_of_these = [
            ('convert', 'VB'),
            ('convert', 'NN')
        ]
        if any([x in one_of_these for x in tags]):

            # Extract units
            service = semantic.units.ConversionService()
            units = service.extractUnits(plain_text)

            # If we have two units, we're good
            if len(units) > 1:
                return True

        return False

    def respond(self, **kwargs):
        plain_text = kwargs.get('plain_text')
        client = kwargs.get('client')

        # Setup
        service = semantic.units.ConversionService()
        units = service.extractUnits(plain_text)
        i_engine = inflect.engine()
        first_unit_plural = i_engine.plural_noun(units[0], 10).replace('ss', 's')

        try:
            # Give the conversion
            return JenniferResponse(self, [
                JenniferTextResponseSegment(i_engine.number_to_words(service.convert(plain_text)))
            ])
        except TypeError:
            # If we've already done this before, return
            cont = kwargs.get('bail_if_exception', False)
            if cont:
                client.give_output_string(self, "Sorry I can't convert that")
                return

            # user didn't specify how many of the unit to convert
            client.give_output_string(self, "How many {}?".format(first_unit_plural))
            number = client.collect_input()

            # Sub out the input text
            actual_units = '{} {}'.format(number, units[0])
            plain_text = plain_text.replace(units[0], actual_units)

            # Call self, but with flag only allowing this to happen once
            return self.respond(client=client, plain_text=plain_text, bail_if_exception=True)
        except ValueError:
            # Failure
            client.give_output_string(self, "Sorry I can't convert {} to {}".format(units[0], units[1]))
            return
