import json
import os

from channels.generic.websocket import WebsocketConsumer
from django.conf import settings as s

from pygeppetto_gateway.base import GeppettoProjectBuilder, \
        GeppettoServletManager

import pygeppetto_server.messages as messages


class GeppettoGatewayConsumer(WebsocketConsumer):

    """ Consumer for proxying queries to the real Geppetto server """

    def connect(self):
        self.accept()

    def receive(self, text_data, bytes_data=None):
        payload = json.loads(text_data)

        action_type = payload.get('type', None)

        if action_type is None:
            self.send(text_data=json.dumps({
                'type': messages.Outcome.ERROR,
                'data': messages.UknownActionError()
                }))
            return

        if not hasattr(self, action_type):
            self.send(json.dumps({
                'type': messages.Outcome.ERROR,
                'data': messages.ActionNotFoundError()
                }))
            return

        result = getattr(self, action_type)(**payload.get('data', {}))

        self.send(json.dumps(result))

    def disconnect(self, close_code):
        self.send(json.dumps({
            'type': messages.Outcome.CONNECTION_CLOSED,
            'data': 'Bye, stranger!'
            }))

    # ACTIONS

    def scidash_run_experiment(self, experiment_id) -> None:
        servlet_manager = GeppettoServletManager()

        servlet_manager.handle(
                _type=messages.Servlet.RUN_EXPERIMENT,
                data=experiment_id
                )

        #FIXME: should not repeat the same part from scidash_load_model
        while not response_finished:
            result = servlet_manager.read()

            if result is not '':
                response_list.append(json.loads(result))
            else:
                response_finished = True

        return {
                'type': messages.Outcome.GEPPETTO_RESPONSE_RECEIVED,
                'data': response_list
                }

    def scidash_load_model(self, url: str) -> None:
        """scidash_load_model

        Action for loading model to Geppetto

        :param url: Url to model file
        :type url: str
        :rtype: None
        """
        project_builder = GeppettoProjectBuilder(url,
                built_project_location=os.path.join(
                    s.PYGEPPETTO_BUILDER_PROJECT_ROOT,
                    'project.json'
                    ),
                built_xmi_location=os.path.join(
                    s.PYGEPPETTO_BUILDER_PROJECT_ROOT,
                    'model.xmi'
                    ),
                downloaded_nml_location=os.path.join(
                    s.PYGEPPETTO_BUILDER_PROJECT_ROOT,
                    'nml_model.nml'
                    ),
                project_name="TestProjectName"
                )
        path_to_project = project_builder.build_project()
        servlet_manager = GeppettoServletManager()

        servlet_manager.handle(
                _type=messages.Servlet.LOAD_PROJECT_FROM_URL,
                data=path_to_project
                )

        response_finished = False
        response_list = []

        while not response_finished:
            result = servlet_manager.read()

            if result is not '':
                response_list.append(json.loads(result))
            else:
                response_finished = True

        return {
                'type': messages.Outcome.GEPPETTO_RESPONSE_RECEIVED,
                'data': response_list
                }

class GeppettoConsumer(WebsocketConsumer):

    CLIENT_ID = {
        'type': 'client_id',
        'data': json.dumps({
            'clientID': 'Connection1'
        })
    }

    PRIVILEGES = {
        'type': 'user_privileges',
        'data': json.dumps({
            "user_privileges": json.dumps({
                "userName": "Python User",
                "loggedIn": True,
                "hasPersistence": False,
                "privileges": [
                    "READ_PROJECT",
                    "DOWNLOAD",
                    "DROPBOX_INTEGRATION",
                    "RUN_EXPERIMENT",
                    "WRITE_PROJECT"
                ]
            })
        })
    }

    def connect(self):
        self.accept()
        self.send(text_data=json.dumps(self.CLIENT_ID))
        self.send(text_data=json.dumps(self.PRIVILEGES))

    def receive(self, text_data, bytes_data=None):
        payload = json.loads(text_data)

        if (payload['type'] == 'geppetto_version'):
            self.send(text_data=json.dumps({
                    "requestID": payload['requestID'],
                    "type": "geppetto_version",
                    "data": json.dumps({
                        "geppetto_version": "0.3.7"
                        })
                }))

    def disconnect(self, close_code):
        self.send(text_data=json.dumps({
            'type': 'socket_closed',
            'data': close_code
        }))
