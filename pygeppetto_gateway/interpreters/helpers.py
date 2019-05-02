import os
import re
from enforce import runtime_validation

from pygeppetto_gateway.interpreters.core import InterpreterException

INTERPRETER_ASSOCIATION_MAP = {
    '.net.nml': 'pygeppetto_gateway.interpreters.net.NetInterpreter',
    '.cell.nml': 'pygeppetto_gateway.interpreters.cell.CellInterpreter',
    '.xml': 'pygeppetto_gateway.interpreters.lems.LEMSInterpreter',
    '.channel.nml': 'pygeppetto_gateway.interpreters.channel.ChannelInterpreter',  # noqa: E501
}


@runtime_validation
def interpreter_detector(url: str) -> str:
    extension_regexp = '(?P<format>\.\w+\.\w+|\.\w+)'
    search_result = re.search(extension_regexp, os.path.basename(url))

    if search_result is None:
        raise InterpreterException(f'Can\'t detect interpreter for url {url}')

    _format = search_result.groups('format')[0]

    interpreter_import_string = INTERPRETER_ASSOCIATION_MAP.get(
        _format, False
    )

    if interpreter_import_string:
        return interpreter_import_string

    raise InterpreterException(f'Can\'t detect interpreter for url {url}')
