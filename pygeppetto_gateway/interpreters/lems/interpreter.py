from pygeppetto_gateway.interpreters import core
from pygeppetto_gateway.interpreters.lems import templates


class LEMSInterpreter(core.BaseModelInterpreter):
    include_pattern = '<Include file="(.*)"'
    target_pattern = 'target="(.*)">'
    project_template = templates.PROJECT
    model_template = templates.MODEL
