import json
from typing import Any

from .send import send_error_to_block_live_update


def json_decoder(data: Any, error_message: str = "") -> Any:
    try:
        return json.loads(data)
    except:
        if error_message:
            send_error_to_block_live_update(error_message)
        else:
            print("Wrong json")
