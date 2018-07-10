import json

from django.conf import settings
from websocket import create_connection
import requests



import logging
LOGGER = logging.getLogger(__name__)


class GeppettoServletManager():

    """ Base class for communication with Java Geppetto server """

    DEFAULT_HOST = 'ws://localhost:8080'
    cookies = None

    def __init__(self):

        if hasattr(settings, 'GEPPETTO_SERVLET_URL'):
            self.host = settings.GEPPETTO_SERVLET_URL
        else:
            self.host = self.DEFAULT_HOST

        self._say_hello_geppetto()

    def _say_hello_geppetto(self):
        http_response = requests.get(settings.GEPPETTO_BASE_URL)

        self.cookies = ";".join(["{}={}".format(x, y) for x, y in
            http_response.cookies.iteritems()])

    def _send(self, payload):

        if self.cookies is None:
            raise Exception("You forgot to say hello to geppetto"
                    "(self._say_hello_geppetto())")

        ws = create_connection(self.host,
                cookie=self.cookies)

        ws.send(payload)
        result = ws.recv()
        ws.close()

        return result

    def handle(self, _type, data):
        payload = json.dumps({
            'type': _type,
            'data': data
        })

        result = self._send(payload)

        try:
            return json.loads(result)
        except:
            return result


class GeppettoProjectBuilder():

    DEFAULT_FILE_PATH = '/tmp/model.nml'

    def __init__(self, nml_url):

        self._nml_url = nml_url

        self.load_file()

    def load_file(self):

        _file_content = requests.get(self._nml_url).text

        with open(self.DEFAULT_FILE_PATH) as f:
            f.write(_file_content)
