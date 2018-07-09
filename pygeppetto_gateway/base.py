import json

from django.conf import settings
from websocket import create_connection
import requests

import logging
LOGGER = logging.getLogger(__name__)


class GeppettoServletManager():

    """ Base class for communication with Java Geppetto server """

    DEFAULT_HOST = 'ws://localhost:8080'

    def __init__(self):

        if hasattr(settings, 'GEPPETTO_SERVLET_HOST'):
            self.host = settings.GEPPETTO_SERVLET_HOST
        else:
            self.host = self.DEFAULT_HOST

    def _send(self, payload):
        ws = create_connection(self.host)
        ws.send(payload)
        result = ws.recv()
        ws.close()

        return result

    def handle(self, _type, data):
        payload = json.dumps({
            'type': _type,
            'data': data
        })

        return json.loads(self._send(payload))


class GeppettoProjectBuilder():

    DEFAULT_FILE_PATH = '/tmp/model.nml'

    def __init__(self, nml_url):

        self._nml_url = nml_url

        self.load_file()

    def load_file(self):

        _file_content = requests.get(self._nml_url).text

        with open(self.DEFAULT_FILE_PATH) as f:
            f.write(_file_content)
