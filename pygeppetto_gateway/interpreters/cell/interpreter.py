from pygeppetto_gateway.interpreters import core
from pygeppetto_gateway.interpreters.cell import templates


class CellInterpreter(core.BaseModelInterpreter):
    include_pattern = '<include href="(.*)"'
    target_pattern = '<cell id="(.*)" .*>'
    project_template = templates.PROJECT
    model_template = templates.MODEL
