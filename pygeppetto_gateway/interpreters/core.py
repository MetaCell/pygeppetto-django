import logging
import os
import re
import typing as t
from functools import lru_cache

import requests
from django.conf import settings
from enforce import runtime_validation

from pygeppetto_gateway.interpreters.helpers import (
    NeuroMLDbExtractor, URLProcessor, InterpreterException
)

logger = logging.getLogger('db')


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


@runtime_validation
class BaseModelInterpreter():
    """ Base class for all interpreters """

    include_pattern: str = None
    target_pattern: str = None
    project_template: str = None
    model_template: str = None

    def __init__(self, model_file_url: t.Union[str, dict]):
        self.model_file_url = model_file_url
        if isinstance(self.model_file_url, dict):
            self.model_file_content = self.__get_model_content(
                hashabledict(self.model_file_url)
            )
        else:
            self.model_file_content = self.__get_model_content(
                self.model_file_url
            )

    # @lru_cache(maxsize=8)
    def __get_model_content(self, url: t.Union[str, hashabledict]) -> str:
        if isinstance(url, dict):
            processor = URLProcessor(url.get('api'))
        else:
            processor = URLProcessor(url)

        url = processor.get_file_url()

        if not isinstance(url, dict):
            if not os.path.isfile(url):
                model_request = requests.get(self.model_file_url)

                if model_request.status_code == 404:
                    raise InterpreterException(
                        f'Model not found by url {self.model_file_url}'
                    )

                return model_request.text
            else:
                with open(url, 'r') as f:
                    return f.read()
        else:
            extractor = NeuroMLDbExtractor(
                url, processor.model_id, settings.DOWNLOADED_MODEL_DIR
            )

            with open(extractor.model_path, 'r') as f:
                result = f.read()

            return result

    def extract_target(self) -> str:
        logger.info(f'Extracting target for {self.model_file_url}')

        result = re.search(self.target_pattern, self.model_file_content)

        if result is not None:
            return result.group(1)
        else:
            raise InterpreterException(
                f'Can\'t found target for model {self.model_file_url}'
            )

    def extract_includes(self) -> t.List[str]:
        result = re.findall(self.include_pattern, self.model_file_content)

        includes = [path for path in result]

        return includes

    def get_model_file_content(self) -> str:
        return self.model_file_content

    def get_project_template(self) -> str:
        return self.project_template

    def get_model_template(self) -> str:
        return self.model_template

    def extract_instance(self) -> str:
        return self.extract_target()
