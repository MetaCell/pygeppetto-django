import json
import logging
import os
import pathlib
import re
from string import Template

import requests
from django.conf import settings
from websocket import create_connection

from pygeppetto_gateway import helpers

LOGGER = logging.getLogger(__name__)


class GeppettoServletManager():
    """ Base class for communication with Java Geppetto server """

    DEFAULT_HOST = 'ws://localhost:8080'

    cookies = None
    ws = None

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

        self.cookies = ";".join(
            [
                "{}={}".format(x, y)
                for x, y in http_response.cookies.iteritems()
            ]
        )

    def _send(self, payload: dict) -> str:
        """_send

        sending data in payload to websocket

        :param payload:
        :type payload: dict
        :rtype: str
        """

        if self.cookies is None:
            raise Exception(
                "You forgot to say hello to geppetto"
                "(self._say_hello_geppetto())"
            )

        self.ws = create_connection(self.host, cookie=self.cookies)

        self.ws.send(payload)

    def handle(self, _type: str, data: dict, request_id="pg-request"):
        payload = json.dumps(
            {
                'requestID': request_id,
                'type': _type,
                'data': data
            }
        )

        self._send(payload)

    def read(self) -> str:
        result = self.ws.recv()

        return result


class GeppettoProjectBuilder():
    def __init__(self, score=None, model_url=None, **options: dict) -> None:
        """__init__

        :param model_url: url or :param score: ScoreInstance required

        :param **options: not required
            project_location: location where project file will be saved
                after replacing all values
            nml_location: location where nml file will be saved
                after downloading
            watched_variables: list of variables, extracted from model
            timestep: timestep, as you see
            length: I don't know what is this to be honest
            project_name: obviously a project name
        """
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self._no_score = score is None

        if not self._no_score:
            self._score = score

        self._target = ""

        self._nml_url = model_url if self._no_score else self._score.model_instance.url  # noqa: E501

        self._extract_format()

        if self._model_format == 'net':
            xmi_template_path = os.path.join(
                current_dir, 'templates/model_template.xmi'
            )
        else:
            xmi_template_path = os.path.join(
                current_dir, 'templates/model_template_cell.xmi'
            )

        project_template_path = os.path.join(
            current_dir, 'templates/project_template.json'
        )

        with open(xmi_template_path, 'r') as t:
            self.xmi_template = t.read()

        with open(project_template_path, 'r') as t:
            self.project_template = t.read()

        self._model_name = options.get('model_name', 'defaultModel')

        self._built_xmi_location = options.get(
            'xmi_location', '/tmp/model.xmi'
        )

        self._built_project_location = options.get(
            'project_location', '/tmp/project.json'
        )

        self._downloaded_nml_location = options.get(
            'nml_location', '/tmp/nml_model.nml'
        )

        for _dir in [
            '_built_xmi_location', '_built_project_location',
            '_downloaded_nml_location'
        ]:
            self._create_dir_if_not_exists(getattr(self, _dir))

        self._base_project_files_host = getattr(
            settings, 'BASE_PROJECT_FILES_HOST',
            'http://localhost:8000/static/projects/'
        )

        if self._no_score:
            self._watched_variables = options.get(
                'watched_variables', []
            )
        else:
            self._watched_variables = json.dumps(
                self._score.model_instance.run_params.get('stateVariables', [])
            )

        self._timestep = options.get('timestep', 0.00005)

        self.duration = options.get('duration', 0.3)

        self._project_name = options.get('project_name', 'defaultProject')

    def _get_file_path_tail(self, path):
        base_dir = getattr(settings, 'BASE_DIR', None)

        if base_dir is None:
            raise Exception(
                'You should set BASE_DIR to project in settings.py'
            )

        base_project_files_dir = os.path.join(base_dir, 'static', 'projects')

        return path.replace('{}/'.format(base_project_files_dir), '')

    def _create_dir_if_not_exists(self, path):
        dir_path = pathlib.Path(pathlib.Path(path).parents[0])

        if not dir_path.is_dir():
            dir_path.mkdir(parents=True, exist_ok=True)

    def build_url(self, path):
        return '{}{}'.format(
            self._base_project_files_host, self._get_file_path_tail(path)
        )

    def donwload_nml(self) -> str:
        """donwload_nml

        Downloads NML file from `self._nml_url`,
            saves it to `self._downloaded_nml_location`

        :return: path to nml
        :rtype: str
        """

        self._nml_file_content = requests.get(self._nml_url).text

        with open(self._downloaded_nml_location, 'w') as nml:
            nml.write(self._nml_file_content)

        file_name = os.path.basename(self._downloaded_nml_location)
        project_dir = self._downloaded_nml_location.replace(file_name, '')

        helpers.process_includes(self._nml_url, project_dir)
        self._extract_target()

        return self._downloaded_nml_location

    def _extract_format(self):
        file_name = os.path.basename(self._nml_url)
        self._model_format = file_name.split(".")[-2]

    def _extract_target(self):
        if self._model_format == 'net':
            result = re.search(
                '<network id="(\w*)\"', self._nml_file_content
            )
        else:
            result = re.search(
                '<Target component="(\w*)\"', self._nml_file_content
            )

        if result is not None:
            self._target = result.group(1)

    def build_xmi(self) -> str:
        """build_xmi

        Builds xmi Geppetto model file from downloaded nml, saves to
        `self._built_xmi_location`

        :return: path to xmi
        :rtype: str
        """

        with open(self._built_xmi_location, 'w') as xt:
            xt.write(
                self.xmi_template.format(
                    name=self._model_name,
                    target=self._target,
                    url=self.build_url(self._downloaded_nml_location)
                )
            )

        return self.build_url(self._built_xmi_location)

    def build_project(self) -> str:
        """build_project
        :returns: path to project file

        """

        self.donwload_nml()
        self.build_xmi()

        with open(self._built_project_location, 'w+') as project:
            project.write(
                Template(self.project_template).substitute(
                    project_name=self._project_name,
                    instance=self._model_name,
                    target=self._target,
                    watched_variables=self._watched_variables,
                    url=self.build_url(self._built_xmi_location),
                    score_id="NULL" if self._no_score else self._score.pk
                )
            )

        return self.build_url(self._built_project_location)
