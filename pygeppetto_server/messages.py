# GEPPETTO SERVLET MESSAGES


class Servlet:

    LOAD_PROJECT_FROM_URL = 'load_project_from_url'
    RUN_EXPERIMENT = 'run_experiment'
    CLIENT_ID = 'client_id'
    PING = 'ping'


class ServletResponse:

    PROJECT_LOADED = 'project_loaded'
    GEPPETTO_MODEL_LOADED = 'geppetto_model_loaded'
    EXPERIMENT_LOADED = 'experiment_loaded'

    ERROR_RUNNING_EXPERIMENT = 'error_running_experiment'
    GENERIC_ERROR = 'generic_error'
    ERROR_LOADING_PROJECT = 'error_loading_project'


# GATEWAY MESSAGES


class Income:

    LOAD_MODEL = 'load_model'


class Outcome:

    ERROR = 'error'
    CONNECTION_CLOSED = 'connection_closed'
    GEPPETTO_RESPONSE_RECEIVED = 'geppetto_response_received'


# ERRORS


class PygeppettoDjangoError():
    code = None
    message = None

    def __init__(self):
        return {'code': self.code, 'message': self.message}


class UknownActionError(PygeppettoDjangoError):
    code = 400
    message = 'UKNOWN_ACTION'


class ActionNotFoundError(PygeppettoDjangoError):
    code = 404
    message = 'ACTION_NOT_FOUND'
