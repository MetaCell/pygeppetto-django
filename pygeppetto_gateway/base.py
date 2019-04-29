import json
import logging
import os
import pathlib
import zlib

import requests
from pygeppetto_gateway.interpreters import core
from django.conf import settings
from enforce import runtime_validation
from websocket import create_connection

from pygeppetto_gateway import helpers

db_logger = logging.getLogger('db')


@runtime_validation
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

        db_logger.info(f"Servlet manager init with {self.host} GEPPETTO url")

        self._say_hello_geppetto()

    def _say_hello_geppetto(self) -> None:
        """_say_hello_geppetto

        Here we have to do a GET request to base Geppetto page, and then put
        session cookies into websocket connection, or it will not work.
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

        db_logger.info(
            f"Sending '{_type}' request to GEPPETTO. Payload {payload}"
        )

        self._send(payload)

    def read(self) -> str:
        result = self.ws.recv()

        if isinstance(result, bytes):
            result_bytes = bytearray(result)[1:]

            result = zlib.decompress(result_bytes, 15 + 32)

        return result


class GeppettoProjectBuilder():
    def __init__(
        self,
        interpreter: core.BaseModelInterpreter,
        score=None,
        model_file_url: str = None,
        **options: dict
    ) -> None:
        """__init__

        :**options: not required
            project_location: location where project file will be saved
                after replacing all values
            model_file_location: location where nml file will be saved
                after downloading
            watched_variables: list of variables, extracted from model
            timestep: timestep, as you see
            length: time model will be simulating
            project_name: obviously a project name
        """

        self.no_score = score is None

        if not self.no_score:
            self.score = score
        else:
            db_logger.info(
                f'Score is not presented, working with url {model_file_url}'
            )
        self.model_file_url = model_file_url if self.no_score else self.score.model_instance.url  # noqa: E501
        self.interpreter = interpreter(self.model_file_url)
        self.xmi_template = self.interpreter.get_model_template()
        self.project_template = self.interpreter.get_project_template()
        self.model_name = options.get('model_name', 'defaultModel')

        self.built_xmi_location = options.get(
            'xmi_location', '/tmp/model.xmi'
        )

        self.built_project_location = options.get(
            'project_location', '/tmp/project.json'
        )

        self.model_file_location = options.get(
            'model_file_location', '/tmp/nml_model.nml'
        )

        for _dir in [
            'built_xmi_location', 'built_project_location',
            'downloaded_nml_location'
        ]:
            self.create_dir_if_not_exists(getattr(self, _dir))

        self.base_project_files_host = getattr(
            settings, 'BASE_PROJECT_FILES_HOST',
            'http://localhost:8000/static/projects/'
        )

        if self.no_score:
            self.watched_variables = json.dumps(
                options.get('watched_variables', [])
            )
        else:
            self.watched_variables = json.dumps(
                self.score.model_instance.run_params.get(
                    'watchedVariables', []
                )
            )

        self.timestep = options.get('timestep', 0.00005)
        self.duration = options.get('duration', 0.3)
        self.project_name = options.get('project_name', 'defaultProject')

    def get_file_path_tail(self, path):
        base_dir = getattr(settings, 'BASE_DIR', None)

        if base_dir is None:
            raise Exception(
                'You should set BASE_DIR to project in settings.py'
            )

        base_project_files_dir = os.path.join(base_dir, 'static', 'projects')

        return path.replace(f'{base_project_files_dir}/', '')

    def create_dir_if_not_exists(self, path):
        dir_path = pathlib.Path(pathlib.Path(path).parents[0])

        if not dir_path.is_dir():
            dir_path.mkdir(parents=True, exist_ok=True)

    def build_url(self, path):
        return f'{self.base_project_files_host}{self.get_file_path_tail(path)}'

    def write_model_to_file(self) -> str:
        """write_model_to_file

        Writes model file from `self.model_file_url`,
            saves it to `self.downloaded_nml_location`
        """

        model_file_content = self.interpreter.get_model_file_content()

        db_logger.info(f"Writing {self.model_file_url}")

        with open(self.model_file_location, 'w') as model:
            model.write(model_file_content)

        file_name = os.path.basename(self.model_file_location)
        project_dir = self.model_file_location.replace(file_name, '')

        helpers.process_includes(self.model_file_url, project_dir)

        return self.model_file_location

    def build_xmi(self) -> str:
        """build_xmi

        Builds xmi Geppetto model file from downloaded nml, saves to
        `self._built_xmi_location`
        """

        with open(self.built_xmi_location, 'w') as xt:
            xt.write(
                self.xmi_template.format(
                    name=self.model_name,
                    target=self.interpreter.extract_target(),
                    url=self.build_url(self.model_file_location)
                )
            )

        return self.build_url(self.built_xmi_location)

    def build_project(self) -> str:
        """build_project
        :returns: path to project file

        """

        self.write_model_to_file()
        self.build_xmi()

        with open(self.built_project_location, 'w+') as project:
            project.write(
                self.project_template.format(
                    project_name=self.project_name,
                    instance=self.interpreter.get_instance(),
                    target=self.interpreter.get_target(),
                    watched_variables=self.watched_variables,
                    url=self.build_url(self.built_xmi_location),
                    score_id="NULL" if self.no_score else self.score.pk
                )
            )

        return self.build_url(self.built_project_location)
