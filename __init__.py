# -*- coding: utf-8 -*-
import json
import requests
from collections import OrderedDict
from naomi import plugin
from naomi import profile


# The speechhandler plugin represents something that Naomi does
# in response to a request from the user. This is often a spoken
# response, but can also be an action like turning on a light or
# sending an email. It is the functional equivalent of a skill on
# most other assistant platforms.
# For details about writing a speech handler, see:
# https://projectnaomi.com/dev/docs/developer/plugins/speechhandler_plugin.html
class SimpleHomeAssistant(plugin.SpeechHandlerPlugin):
    def __init__(self, *args, **kwargs):
        super(SimpleHomeAssistant, self).__init__(*args, **kwargs)
        self.api_token = profile.get(["SimpleHomeAssistant", "api_token"])
        self.url = profile.get(["SimpleHomeAssistant", "url"])

    def settings(self):
        _ = self.gettext
        return OrderedDict(
            [
                (
                    ("SimpleHomeAssistant", "api_token"), {
                        "title": _("HomeAssistant Long-Lived Access Token"),
                        "description": _("You can generate a long-lived access token in HomeAssistant at the bottom of your profile page.")
                    }
                ), (
                    ("SimpleHomeAssistant", "url"), {
                        "title": _("URL of your home assistant"),
                        "description": _("The URL of your home assistant is usually something like http://homeassistant.local:8123")
                    }
                )
            ]
        )

    # Intents describe how your plugin may be activated.
    # At the simplest level, just write all the things you think
    # someone might say if they wanted to activate your
    # plugin. Finally, supply a link to the handle method,
    # which Naomi will use when your intent is selected.
    def intents(self):
        return {
            'MyIntent': {
                'locale': {
                    'en-US': {
                        'keywords': {
                            'StateKeyword': [
                                'ON',
                                'OFF'
                            ]
                        },
                        'templates': [
                            'TURN THE LIGHT {StateKeyword}',
                            'TURN {StateKeyword} THE LIGHT'
                        ]
                    }
                },
                'action': self.handle
            }
        }

    # The handle method is where you pick up after Naomi has
    # identified your intent as the one the user was attempting
    # to activate.
    def handle(self, intent, mic):
        # The intent parameter is a structure with information about
        # the user request. intent['input'] will hold the transcription
        # of the user's request.
        to_state = intent['matches']['StateKeyword'][0]
        # The mic parameter is a microphone object that you can
        # use to respond to the user.
        api_url = "{}/api/services/light/turn_{}"

        # Control the light.
        api_response = requests.post(api_url.format(self.url, to_state.lower()), json={
            "entity_id": "light.gledopto_gl_b_007p_light"
        }, headers={
            "Authorization": f"Bearer {self.api_token}",
        })
        print(f"Turning the light {to_state}")
        print(f"Response: {api_response.text}")
        response = json.loads(api_response.text)
        mic.say(f"The light is {response[0]['state']}")
