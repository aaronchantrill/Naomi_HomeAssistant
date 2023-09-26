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
        self.light = {}
        for light in profile.get(["SimpleHomeAssistant", "light"]):
            self.light[light['name']] = light['id']

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
                ), (
                    ("SimpleHomeAssistant", "light"), {
                        "type": "array",
                        "each": [
                            (
                                ("id",), {
                                    "title": _("ID of your light"),
                                    "description": _("The ID of your light from HomeAssistant")
                                }
                            ),
                            (
                                ("name",), {
                                    "title": _("Name of your light"),
                                    "description": _("The name you would like to use to refer to your light.")
                                }
                            )
                        ]
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
                            'LightNameKeyword': self.light.keys(),
                            'StateKeyword': [
                                'ON',
                                'OFF'
                            ]
                        },
                        'templates': [
                            'TURN THE LIGHT {StateKeyword}',
                            'TURN THE {LightNameKeyword} {StateKeyword}',
                            'TURN {StateKeyword} THE LIGHT',
                            'TURN {StateKeyword} THE {LightNameKeyword}'
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
        if 'StateKeyword' in intent['matches']:
            if(len(intent['matches']['StateKeyword']) > 0):
                to_state = intent['matches']['StateKeyword'][0]
        # If there is only one light, select it
        which_light = None
        if(len(self.light) == 1):
            which_light = list(self.light.keys())[0]
        if 'LightNameKeyword' in intent['matches']:
            if(len(intent['matches']['LightNameKeyword']) > 0):
                which_light = intent['matches']['LightNameKeyword'][0]
        if which_light:
            light_id = self.light[which_light]
        # The mic parameter is a microphone object that you can
        # use to respond to the user.
        api_url = "{}/api/services/light/turn_{}"

        # Control the light.
        try:
            api_response = requests.post(api_url.format(self.url, to_state.lower()), json={
                "entity_id": light_id
            }, headers={
                "Authorization": f"Bearer {self.api_token}",
            })
            print(f"Turning the {which_light} {to_state}")
            print(f"Response: {api_response.text}")
            response = json.loads(api_response.text)
            mic.say(f"The {which_light} is {response[0]['state']}")
        except requests.exceptions.ConnectionError:
            mic.say(f"Sorry, I could not connect to the Home Assistant server at {self.url}")
