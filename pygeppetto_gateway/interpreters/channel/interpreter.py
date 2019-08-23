from pygeppetto_gateway.interpreters import core
from pygeppetto_gateway.interpreters.channel import templates


class ChannelInterpreter(core.BaseModelInterpreter):
    include_pattern = '<include href="(.*)"'
    target_pattern = '<ionChannel id="([\w_\-\d]*)" .*>'
    project_template = templates.PROJECT
    model_template = templates.MODEL
