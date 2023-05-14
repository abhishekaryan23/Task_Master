import streamlit.report_thread as ReportThread
from streamlit.server.server import Server

class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __getitem__(self, key):
        if isinstance(key, str):
            return getattr(self, key, None)
        else:
            raise ValueError(f"Key {key} is not a string.")

    def __setitem__(self, key, val):
        if isinstance(key, str):
            setattr(self, key, val)
        else:
            raise ValueError(f"Key {key} is not a string.")
            
    def __contains__(self, key):
        if isinstance(key, str):
            return hasattr(self, key)
        else:
            raise ValueError(f"Key {key} is not a string.")


def get_state(**kwargs):
    ctx = ReportThread.get_report_ctx().session_id
    session = Server.get_current()._get_session_info(ctx)

    if session is None:
        raise RuntimeError("Couldn't get your Streamlit session.")

    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = SessionState(**kwargs)

    return session._custom_session_state
