# GEPPETTO SERVLET MESSAGES

class Servlet:

    LOAD_PROJECT_FROM_URL = 'load_project_from_url'

# GATEWAY MESSAGES

class Income:

    SCIDASH_LOAD_MODEL = 'scidash_load_model'


class Outcome:

    ERROR = 'error'
    CONNECTION_CLOSED = 'connection_closed'
    GEPPETTO_RESPONSE_RECEIVED = 'geppetto_response_received'


# ERRORS


class PygeppettoDjangoError():
    code = None
    message = None

    def __init__(self):
        return {
                'code': self.code,
                'message': self.message
                }


class UknownActionError(PygeppettoDjangoError):
    code = 400
    message = 'UKNOWN_ACTION'


class ActionNotFoundError(PygeppettoDjangoError):
    code = 404
    message = 'ACTION_NOT_FOUND'
