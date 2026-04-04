import cherrypy
import google_auth_oauthlib.flow
from env import SERVER_ADDRESS, SCOPE, login_hint
import os, signal

class AlarmController(object):

    @cherrypy.expose
    def index(self):
        # HTML page with a single button
        return """
        <html>
            <head>
                <title>Alarm Control</title>
            </head>
            <body>
                <h1>Alarm Control</h1>
                <form method="post" action="/alarm/stop">
                    <button type="submit">Stop Alarm</button>
                </form>
            </body>
        </html>
        """  

    @cherrypy.expose
    def stop(self):
        pid_file = "/tmp/alarm.pid"
        message = ""

        if os.path.exists(pid_file):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())

                os.kill(pid, signal.SIGTERM)  # Gracefully stop the process
                message = f"Alarm process {pid} stopped."
                os.remove(pid_file)  # Clean up the PID file
            except ProcessLookupError:
                message = f"No process with PID {pid} found."
            except Exception as e:
                message = f"Error stopping alarm: {e}"
        else:
            message = "PID file not found. Alarm may not be running."

        print(message)  # Logs to console
        return f"""
        <html>
            <body>
                <h2>{message}</h2>
                <a href="/alarm">Go back</a>
            </body>
        </html>
        """


class CalendarWebServer(object):
    alarm = AlarmController()

    @cherrypy.expose
    def index(self):
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





if __name__ == "__main__":
    cherrypy.quickstart(CalendarWebServer())
