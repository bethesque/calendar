# ePaper Calendar

Playing around with my new waveshare 12.48inch e-paper module(b), going to try and render a calendar

# WARNING

There's something a bit screwy around "burn in" I've read both that it occurs and also that it doesn't occur.  Try to avoid leaving the screen with stuff on it for more than a day, if you want it always on, do the clear thing at least daily so it jiggles all those pixels around.

# venv
Keep the python peas from touching the other python carrots

create a venv using:
```
python -m venv .venv
```

## windows
put powershell into venv mode using:
```
.\venv\Scripts\activate.ps1
```

## linux
put shell into venv mode using:
```
source ./venv/Scripts/activate
```

## mac
put shell into venv mode using:
```
source .venv/bin/activate
```

# Dependencies


## system
The thing requires a few system dependencies.  
This is really only relevant on the pi itself, which is running a debian thingy, so apt-get with:
```
TODO: add system dependencies
```

the 12.48 screen uses some rando's lgpio c library which I'm not super happy about
instructions here:
https://www.waveshare.com/wiki/12.48inch_e-Paper_Module_(B)#Install_Python_Library

## pip
python dependencies are managed in `requirements.txt`
when in venv mode install using:
```
pip install -r requirements.txt
```
TODO: add waveshare dependencies to requirements.txt

# Runtime

git clone or copy this repo to the rasberry pi.  I keep mine in /home/thetrav/calendar

install dependencies with:
```
pip install -r requirements.txt
```

## scheduling
Schedule the main screen update for hourly with:
`crontab -e`

```
# Force refresh on startup
@reboot cd /home/thetrav/calendar && /usr/bin/python /home/thetrav/calendar/main.py --force >> /home/thetrav/calendar/log.txt

# Lazy refresh once an hour if data has changed - fetch the data just before the hour in case there is an alarm
55 * * * * cd /home/thetrav/calendar && ./main.sh

# Force refresh once a minute if the token has been updated
* * * * * cd /home/thetrav/calendar && ./main-update-screen-if-token-updated.sh

# Stop the log file getting too big - at 2am on a Sunday, get rid of all but the last 500 lines
0 2 * * 0 [ -f /home/thetrav/calendar/log.txt ] && /usr/bin/tail -n 500 /home/thetrav/calendar/log.txt > /home/thetrav/calendar/log.tmp && /bin/mv /home/thetrav/calendar/log.tmp /home/thetrav/calendar/log.txt

# Check for alarms
*/5 * * * * cd /home/thetrav/calendar && /usr/bin/python check_for_alarms.py

```

## web server

I use nginx for https and python web server

```
sudo apt install nginx
```

Next I generated a self signed cert following the guide here:
https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-16-04

I hit enter for all params except common name, where I enter the rasberry pi's ipv4 address (I have the DHCP lease statically asigned by my router)


## Python app server

The server invokes a locally running cherryPi app which needs to be set up as service with:
```
sudo cp /home/thetrav/calendar/epcal.service /lib/systemd/system/epcal.service
```

Reload with:

```
sudo systemctl daemon-reload
```

Start service if it has stopped with

```
sudo systemctl restart epcal.service
```

View system logs using

```
journalctl -f
```

## Google Authentication

The app will require client_secret.json in the project root.  
You can download that file from google.
They have a tutorial here: https://developers.google.com/identity/protocols/oauth2/web-server
getting the API set up is part of the pre-requisites.

In order for it to work you need a public DNS entry (google doesn't trust ip's or local DNS names).
My solution was to set a subdomain to resolve to a private network IP which I've told my router to always assign to the calendar rasberry pi.

# Run without hardware

While developing I run things locally, main.py contains a local and hardware rendering function. Set `IS_LOCAL = True` in your env.py file and it will print the screen to an image file and open it locally.

I've also got a testData function for when I don't want to wait for a round trip from google or in case I want to test a hard-to-recreate data scenario.
