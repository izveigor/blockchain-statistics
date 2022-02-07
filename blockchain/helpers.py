import json
from .errors import ErrorHandler


def json_decoder(data, error_message=''):
    try:
        return json.loads(data)
    except:
        if error_message:
            ErrorHandler.send_error_to_block_live_update(
                error_message
            )
        else:
            print('Wrong json')