import logging
import cherrypy
import google_auth_oauthlib.flow
from ecal.env import SERVER_ADDRESS, SCOPE, login_hint
from ecal.log_config import setup_logging_for_http_server
from pathlib import Path

setup_logging_for_http_server()

logger = logging.getLogger(__name__)


class CalendarWebServer(object):
    @cherrypy.expose
    def index(self):
        return "<ul><li><a href='login'>Login</a></li><li><a href='refresh'>Refresh</a></li></ul>"

    @cherrypy.expose
    def login(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            "client_secret.json",
            scopes=[SCOPE],
            state="alwaysTheSame",
        )
        flow.redirect_uri = f"{SERVER_ADDRESS}/auth"

        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state="alwaysTheSame",
            login_hint=login_hint,
            prompt="consent",
        )

        raise cherrypy.HTTPRedirect(authorization_url)

    @cherrypy.expose
    def auth(self, code=None, state=None, error=None, **kwargs):
        if state != "alwaysTheSame":
            return f"Something is up with your state: {state}"
        if error:
            return f"Something went wrong! {error}"
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            "client_secret.json",
            scopes=[SCOPE],
            state=state,
        )
        flow.redirect_uri = f"{SERVER_ADDRESS}/auth"
        flow.fetch_token(code=code)

        with open("token.json", "w") as text_file:
            print(flow.credentials.to_json(), file=text_file)

        return "Welcome back. The calendar screen should update within a few minutes."

    @cherrypy.expose
    def refresh(self):
        Path("token.json").touch()
        return "Screen should update within a few minutes. <a href='/'>Back</a>"

if __name__ == "__main__":
    if Path("server.conf").is_file():
        logger.info("Loading config file from server.conf")
        cherrypy.config.update("server.conf")
    cherrypy.quickstart(CalendarWebServer())
