import logging
import re
import typing as t
from functools import lru_cache

import requests
from enforce import runtime_validation

logger = logging.getLogger('db')


class InterpreterException(Exception):
    pass


@runtime_validation
class BaseModelInterpreter():
    """ Base class for all interpreters """

    include_pattern: str = None
    target_pattern: str = None
    project_template: str = None
    model_template: str = None

    def __init__(self, model_file_url: str, watched_variables: t.List[str]):

        self.model_file_url = model_file_url
        self.watched_variables = watched_variables

        self.model_file_content = self.__get_model_content(self.model_file_url)

    @lru_cache(maxsize=64)
    def __get_model_content(self, url: str) -> str:
        model_request = requests.get(self.model_file_url)

        if model_request.status_code != 404:
            self.model_file_content = model_request.text
        else:
            raise InterpreterException(
                f'Model not found by url {self.model_file_url}'
            )

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
        raise NotImplementedError(
            "Interpreter should implement extract_instance method"
        )
