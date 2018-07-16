import json
import os
import logging
from string import Template

from django.conf import settings
from django.utils import timezone
from websocket import create_connection
import requests


LOGGER = logging.getLogger(__name__)


class GeppettoServletManager():

    """ Base class for communication with Java Geppetto server """

    DEFAULT_HOST = 'ws://localhost:8080'
    cookies = None

    def __init__(self) -> None:

        if hasattr(settings, 'GEPPETTO_SERVLET_URL'):
            self.host = settings.GEPPETTO_SERVLET_URL
        else:
            self.host = self.DEFAULT_HOST

        self._say_hello_geppetto()

    def _say_hello_geppetto(self) -> None:
        """_say_hello_geppetto

        Here we have to do a GET request to base Geppetto page, and then put
        session cookies into websocket connection, or it will not work.

        :rtype: None
        """

        http_response = requests.get(settings.GEPPETTO_BASE_URL)

        self.cookies = ";".join(["{}={}".format(x, y) for x, y in
            http_response.cookies.iteritems()])

    def _send(self, payload: dict) -> str:
        """_send

        sending data in payload to websocket

        :param payload:
        :type payload: dict
        :rtype: str
        """

        if self.cookies is None:
            raise Exception("You forgot to say hello to geppetto"
                    "(self._say_hello_geppetto())")

        ws = create_connection(self.host,
                cookie=self.cookies)

        ws.send(payload)
        result = ws.recv()
        ws.close()

        return result

    def handle(self, _type: str, data: dict) -> str:
        payload = json.dumps({
            'type': _type,
            'data': data
        })

        result = self._send(payload)

        return result


class GeppettoProjectBuilder():

    def __init__(self, nml_url: str, **options: dict) -> None:
        """__init__

        :param nml_url: required

        :param **options: not required

            built_xml_location: location where xmi model file will be saved
                after replacing all values
            built_project_location: location where project file will be saved
                after replacing all values
            downloaded_nml_location: location where nml file will be saved
                after downloading
            project_name: obviously a project name
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

        self._project_name = options.get('project_name',
                'defaultProject')

    def donwload_nml(self) -> str:
        """donwload_nml

        Downloads NML file from `self._nml_url`,
            saves it to `self._downloaded_nml_location`

        :return: path to nml
        :rtype: str
        """

        file_content = requests.get(self._nml_url).text

        with open(self._downloaded_nml_location, 'w') as nml:
            nml.write(file_content)

        return self._downloaded_nml_location

    def build_xmi(self) -> str:
        """build_xmi

        Builds xmi Geppetto model file from downloaded nml, saves to
        `self._built_xmi_location`

        :return: path to xmi
        :rtype: str
        """

        with open(self._built_xmi_location, 'w') as xt:
            xt.write(self.xmi_template.format(
                name=self._model_name,
                url=self._downloaded_nml_location
                ))

        return self._built_xmi_location

    def build_project(self) -> str:
        """build_project
        :returns: path to project file

        """

        self.donwload_nml()
        self.build_xmi()

        with open(self._built_project_location, 'w') as xt:
            xt.write(Template(self.project_template).substitute(
                    project_name=self._project_name,
                    date=timezone.now(),
                    url=self._built_xmi_location
                ))


        return self._built_project_location
