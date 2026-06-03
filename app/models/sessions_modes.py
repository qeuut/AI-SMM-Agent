from enum import Enum


class SessionModes(Enum):
    DEFAULT = ""
    SET_SESSION_ID = "set_session_id"
    GET_SESSION_ID = "get_session_id"