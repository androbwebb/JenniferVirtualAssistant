# -*- coding: utf-8-*-
import time
import math
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException


from lessons.base.plugin import JenniferResponsePlugin
from lessons.base.exceptions import JenniferUserWantsToCancelException


class JenniferFindMyIphonePlugin(JenniferResponsePlugin):

    PRIORITY = 50
    VERBOSE_NAME = "Find My Iphone"
    REQUIRES_NETWORK = True

    def can_respond(self, **kwargs):
        tags = kwargs.get('tags')
        one_verb = [
            ('find', 'VB'),
            ('finding', 'VBG'),
        ]
        one_of_these = [
            ('phone', 'NN'),
            ('iphone', 'NN')
        ]

        tags_dict = self.tags_dict_by_tag(tags)

        # There must only be one 'NN'
        can_repond = len(tags_dict.get('NN', [])) == 1
        # Need any the verbs in `one_verb` with correct context
        can_repond = can_repond and any([word in tags for word in one_verb])
        # Need at least one of the words in `one_of_these` with correct context
        can_repond = can_repond and any([word in tags for word in one_of_these])

        return can_repond

    def respond(self, **kwargs):
        client = kwargs.get('client')

        client.give_output_string(self, "Let's find that phone")

        try:
            api = PyiCloudService(self.settings['icloudEmail'], self.settings['icloudPassword'])
        except PyiCloudFailedLoginException:
            client.give_output_string(self, "Invalid iCloud Username & Password")
            return

        # All Devices
        devices = api.devices

        # Just the iPhones
        iphones = []

        # The one to ring
        phone_to_ring = None

        for device in devices:
            current = device.status()
            if "iPhone" in current['deviceDisplayName']:
                iphones.append(device)

        # No iphones
        if len(iphones) == 0:
            client.give_output_string(self, "No IPhones Found on your account")
            return

        # Many iphones
        elif len(iphones) > 1:
            client.give_output_string(self, "There are multiple iphones on your account.")
            try:
                for phone in iphones:
                    if client.confirm(self, "Did you mean the {type} named {name}?".format(type=phone.status()['deviceDisplayName'], name=phone.status()['name'])):
                        phone_to_ring = phone
                        break
            except JenniferUserWantsToCancelException():
                return

        # Just one
        elif len(iphones) == 1:
            phone_to_ring = iphones[0]

        if not phone_to_ring:
            client.give_output_string(self, "You didn't select an iPhone")
            return

        # This will attempt to update the status
        phone_to_ring.status()

        if phone_to_ring.status()['batteryLevel'] == 0:
            client.give_output_string(self, "Oh no! The phone is off!")
            location = phone_to_ring.location()
            if location and location[u'locationFinished']:
                timestamp = location['timeStamp'] / 1000
                current_timestamp = time.time()
                seconds_ago = round(abs(current_timestamp - timestamp))
                minutes = int(math.floor(seconds_ago % 60))
                hours = int(math.floor(seconds_ago / 60 / 60))

                time_ago_natural_parts = []
                if hours > 0:
                    time_ago_natural_parts.append("{} hours".format(hours))
                if minutes > 0:
                    time_ago_natural_parts.append("{} minutes".format(minutes))
                time_ago_natural = " and ".join(time_ago_natural_parts) + " ago"
                client.give_output_string(self, "It was last seen {}.".format(time_ago_natural))
            else:
                client.give_output_string(self, "I can't find a location for it.")

            return

        client.give_output_string(self, "Sending ring command to {} now".format(phone_to_ring.status()['deviceDisplayName']))
        phone_to_ring.play_sound()
        return

