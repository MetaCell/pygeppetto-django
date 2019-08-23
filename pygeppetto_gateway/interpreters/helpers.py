import json
import logging
import os
import re
import typing as t
import zipfile

import requests
from enforce import runtime_validation

db_logger = logging.getLogger()


class InterpreterException(Exception):
    pass


INTERPRETER_ASSOCIATION_MAP = {
    '.net.nml': 'pygeppetto_gateway.interpreters.net.NetInterpreter',
    '.cell.nml': 'pygeppetto_gateway.interpreters.cell.CellInterpreter',
    '.xml': 'pygeppetto_gateway.interpreters.lems.LEMSInterpreter',
    '.channel.nml': 'pygeppetto_gateway.interpreters.channel.ChannelInterpreter',  # noqa: E501
}


@runtime_validation
def interpreter_detector(url: str) -> str:
    extension_regexp = '(?P<format>\.\w+\.\w+|\.\w+)$'

    search_result = re.search(extension_regexp, url)

    if search_result is None:
        raise InterpreterException(f'Can\'t detect interpreter for url {url}')

    _format = search_result.groups('format')[0]

    interpreter_import_string = INTERPRETER_ASSOCIATION_MAP.get(_format, False)

    if interpreter_import_string:
        return interpreter_import_string

    raise InterpreterException(f'Can\'t detect interpreter for url {url}')


class URLProcessorException(Exception):
    pass


@runtime_validation
class URLProcessor():

    GITHUB_BLOB = 'github'
    GITHUB_RAW = 'githubusercontent'
    NEUROML_DB = 'neuroml-db'

    def __init__(self, url: str) -> None:
        self.url = url

        self.type = self.detect_type()
        self.model_id = None

        db_logger.info(f'URL Processor got {self.type} url')

    def detect_type(self) -> str:
        if self.GITHUB_RAW not in self.url and self.GITHUB_BLOB in self.url:
            return self.GITHUB_BLOB

        if self.NEUROML_DB in self.url:
            return self.NEUROML_DB

        return self.GITHUB_RAW

    def get_file_url(self) -> t.Union[str, dict]:
        if self.type == self.GITHUB_RAW:
            return self.url

        if self.type == self.GITHUB_BLOB:
            return self.convert_github()

        if self.type == self.NEUROML_DB:
            return self.convert_neuromldb()

    def convert_github(self) -> str:
        result = self.url

        result = result.replace("blob/", "")
        result = result.replace("github.com", "raw.githubusercontent.com")

        return result

    def convert_neuromldb(self) -> dict:
        regexp = 'model_id=(\w*)|model\?id=(\w*)$'

        result = re.search(regexp, self.url)

        if result is not None:
            self.model_id = list(
                filter(lambda x: x is not None, result.groups())
            )[0]
        else:
            raise URLProcessorException(
                f'Can\'t found model id for url {self.url}'
            )

        return {
            'api': f'https://neuroml-db.org/api/model?id={self.model_id}',
            'zip': f'https://neuroml-db.org/GetModelZip?modelID={self.model_id}&version=NeuroML'
        }


class NeuroMLDbExtractorException(Exception):
    pass


@runtime_validation
class NeuroMLDbExtractor():
    def __init__(
        self, info: t.Dict[str, str], model_id: str, extract_path: str
    ) -> None:
        self.info = info
        self.model_id = model_id
        self.extract_path = extract_path

        if not os.path.isdir(self.extract_path):
            raise NeuroMLDbExtractorException('Extract path should be a dir')

        self.model_path = None
        self.model_folder_path = None
        self.model_zip_path = None
        self.root_file = None
        self.url = None

        self.download()
        self.extract()

    def download(self):
        model_info = requests.get(self.info.get('api'))

        if model_info.status_code != 200:
            raise NeuroMLDbExtractorException(
                f'Can\'t get model_info for url {self.info.get("api")}'
            )
        else:
            model_info = json.loads(model_info.text)

        self.root_file = model_info.get('model', {}).get('File_Name', None)

        if self.root_file is None:
            raise NeuroMLDbExtractorException(
                f'Can\'t get model_info for url {self.info.get("api")}'
            )

        zip_url = self.info.get('zip')

        self.model_zip_path = os.path.join(
            self.extract_path, f'{self.model_id}.zip'
        )

        response = requests.get(zip_url, allow_redirects=True)

        if response.status_code == 404:
            raise NeuroMLDbExtractorException(
                f'Model zip not found with id {self.model_id}'
            )

        with open(self.model_zip_path, 'wb') as f:
            f.write(response.content)

        self.model_path = self.model_folder_path = os.path.join(
            self.extract_path, f'{self.model_id}'
        )

    def extract(self):
        zip_ref = zipfile.ZipFile(self.model_zip_path, 'r')
        zip_ref.extractall(self.model_path)
        zip_ref.close()

        self.model_path = os.path.join(self.model_path, self.root_file)
