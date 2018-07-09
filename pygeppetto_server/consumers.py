import json

from channels.generic.websocket import WebsocketConsumer

from pygeppetto_gateway import GeppettoServletManager


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


class GeppettoGatewayConsumer(WebsocketConsumer):

    """ Consumer for proxying queries to the real Geppetto server """

    def connect(self):
        self.accept()

    def receive(self, text_data, bytes_data=None):
        payload = json.loads(text_data)

        GS = GeppettoServletManager()
        print(GS.handle(_type=payload.get('type'), data=payload.get('data')))


    def disconnect(self, close_code):
        pass
