from pygeppetto_gateway.interpreters import core
from pygeppetto_gateway.interpreters.net import templates


class NetInterpreter(core.BaseModelInterpreter):
    include_pattern = '<include href="(.*)"'
    target_pattern = '<target id="(.*)"'
    project_template = templates.PROJECT
    model_template = templates.MODEL

