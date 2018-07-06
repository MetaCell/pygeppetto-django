from __future__ import print_function
import json

from channels.generic.websocket import WebsocketConsumer


class GeppettoConsumer(WebsocketConsumer):

    CLIENT_ID = {
            'text': {
                'type': 'client_id',
                'data': {
                    'clientID': 'Connection1'
                    }
                }
            }

    PRIVILEGES = {
            'text': {
                'type': 'user_privileges',
                'data': {
                    "user_privileges": {
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
                        }
                    }
                }
            }

    def connect(self):
        self.accept()
        self.send(json.dumps(self.CLIENT_ID))
        self.send(json.dumps(self.PRIVILEGES))

    def receive(self, text_data, bytes_data=None):
        payload = json.loads(text_data)

        if (payload['type'] == 'geppetto_version'):
            self.send(json.dumps({
                "text": {
                    "requestID": payload['requestID'],
                    "type": "geppetto_version",
                    "data": {
                        "geppetto_version": "0.3.7"
                        }
                    }
                }))

    def disconnect(self, close_code):
        print("SOCKET CLOSED")
