import json
import os
import logging

from django.conf import settings
from websocket import create_connection
import requests


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
        except Exception:
            return result


class GeppettoProjectBuilder():

    def __init__(self, nml_url, **options):
        """__init__

        :param nml_url:
        :param **options:
            built_xml_location: location where xmi model file will be saved
                after replacing all values
            built_project_location: location where project file will be saved
                after replacing all values
            downloaded_nml_location: location where nml file will be saved
                after downloading
        """

        current_dir = os.path.dirname(os.path.realpath(__file__))

        self._nml_url = nml_url
        self._nml_file = None

        xmi_template_path = os.path.join(current_dir,
                'templates/model_template.xmi')
        project_template_path = os.path.join(current_dir,
                'templates/project_template.json')

        with open(xmi_template_path, 'r') as t:
            self.xmi_template = t.read()

        with open(project_template_path, 'r') as t:
            self.project_template = t.read()

        self._model_name = options.get('model_name', 'defaultModel')

        self._built_xmi_location = options.get('built_xmi_location',
                '/tmp/model.xmi')

        self._built_project_location = options.get('built_project_location',
                '/tmp/project.json')

        self._downloaded_nml_location = options.get('downloaded_nml_location',
                '/tmp/nml_model.nml')


        def donwload_nml(self):
            """
            Downloads NML file from `self._nml_url`,
                saves it to `self._downloaded_nml_location`

            :returns: path of nml file (str)
            """

            file_content = requests.get(self._nml_url).text

            with open(self._downloaded_nml_location, 'w') as nml:
                nml.write(file_content)

            return self._downloaded_nml_location

        def build_xmi(self):
            """
            Builds xmi Geppetto model file from downloaded nml, saves to
            `self._built_xmi_location`

            :returns: path to xmi file (str)
            """

            with open(self._built_xmi_location, 'w') as xt:
                xt.write(self.xmi_template.format(
                    name=self._model_name,
                    url=self._downloaded_nml_location
                    ))

            return self._built_xmi_location
