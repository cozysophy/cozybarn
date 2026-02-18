from paho.mqtt import client as mqtt
from flask import Flask, send_file, request, redirect, jsonify
import time
import subprocess
from dotenv import load_dotenv
from urllib.parse import urlencode
import requests
import os
import secrets
import base64
import threading
import json




load_dotenv() #loading the .env file for spotify authentication

#TODO: 

#Create route for playlist and playlist choosing 
#Create spotify api calls for playlist

#- DONE-create app routes for seperate webpage for camming lights
#  DONE     create buttons/update file locations
# -DONE-create app routes for main LED pattern, main LED brightness
#--DONE create html webpage for main LED button/create buttons
# DONE JUST TESTING BECAUSE GAAAAAAAAAAAAAAAAAAAWD
# DONE create spotify authenticaton routes
# DONE create spotify token and refresh token calls
# DONE create spotify backend api calls and routes for front end UI



#port gets set in the service not the py

#start the MQTT client and stay connected
client = mqtt.Client(client_id="soph")

while True: #this will try mqtt and wait and try again till it connects
    try:    #give this a try
        client.connect("10.42.0.1", 1883, 30)
        break #this breaks out of the infinite loop that while True: is doing and continues the sketch
    except Exception as e: #Exception is a parent group of errors, being set as variable e
        print("MQTT not ready yet:", e)
        time.sleep(2) #asking to wait 2 seconds, and then will loop again to while True:


#client.connect("10.42.0.1", 1883, 30) #(IP of broker, port of broker, keepAlive)

client.loop_start() #keeps network flowing
#not loop_forever because it blocks. It prevents anything else and stays 
#in MQTT forever


app = Flask(__name__)


			#API CALLS
@app.route("/api/main/pattern/rainbow", methods=['POST'])
def rainbowmain():
	client.publish("soph/main/pattern", "rainbow")
	return "ok"

@app.route("/api/mainbrightness/<valtwo>", methods=['POST']) #route variable feeds into function which gets into publish and sends message on correct topic
def brightnessmain(valtwo):
		client.publish("soph/main/brightness", valtwo)
		return "ok"
		
@app.route("/api/cam/brightness/<valone>", methods=['POST'])
def brightnesscam(valone):
		client.publish("soph/cam/brightness", valone)
		return "ok"
		
@app.route("/api/main/pattern/solidwhite", methods=['POST'])
def solidwhitemain():
	client.publish("soph/main/pattern", "solidwhite")
	return "ok"
	
@app.route("/api/pattern/rainbow", methods=['POST'])
def rainbow():
	client.publish("soph/pattern", "rainbow")
	return "ok"

@app.route("/api/pattern/off", methods=['POST'])
def off():
	client.publish("soph/pattern", "off")
	client.publish("soph/main/pattern", "off")
	return "ok"
	
@app.route("/api/pattern/solidwhite", methods=['POST'])
def solidwhite():
	client.publish("soph/pattern", "solidwhite")
	return "ok"
	
@app.route("/api/brightness/<val>", methods=['POST']) #brightness for main CAM light
def brightness(val):
		client.publish("soph/brightness", val)
		return "ok"
		
		#WEBPAGE ROUTING
            
		#note: Flask always needs a definition under app.route

@app.route("/")
def soph(name=None):
	return send_file("/home/sophie/sophcode/haha.html")
	
@app.route("/LEDcontrolpage")
def LEDcontrolpage():
	return send_file("/home/sophie/sophcode/LEDcontrolpage.html")

@app.route("/brightness")
def brightweb():
	return send_file("/home/sophie/sophcode/brightness.html")
		
@app.route("/mainbrightness")
def brightmain():
	return send_file("/home/sophie/sophcode/mainbrightness.html")

@app.route("/mainLEDcontrol")
def mainLEDcontrol():
	return send_file("/home/sophie/sophcode/mainLEDcontrol.html")

@app.route("/mainpattern")
def mainpattern():
	return send_file("/home/sophie/sophcode/mainpattern.html")
	
@app.route("/camLEDcontrol")
def camLEDcontrol():
	return send_file("/home/sophie/sophcode/camLEDcontrol.html")
	
@app.route("/campattern")
def campattern():
	return send_file("/home/sophie/sophcode/campattern.html")

@app.route("/camlightchoose")
def camlightchoose():
    return send_file("/home/sophie/sophcode/camlightchoose.html")

@app.route("/camBacklightbrightness")
def camBacklightbrightness():
    return send_file("/home/sophie/sophcode/camBacklightbrightness.html")

@app.route("/spotify")
def spotifyWeb():
	return send_file("/home/sophie/sophcode/spotify.html")


        #SPOTIFY CONTROLS


@app.route("/spotify/now-playing") #route for converting spotify now-playing OBJECT into parsed JSON and sending to frontend
def now_playing_json():
    global token #call global token variable
    if not token:
        refresh_access_token()
    headers = { "Authorization" : "Bearer " + token }
    
    
    
    response = requests.get("https://api.spotify.com/v1/me/player", headers = headers) 
    print("SPOTIFY /me/player STATUS =", response.status_code)
    print("SPOTIFY /me/player BODY =", response.text[:500])
    stored_now_playing = response.json() #Parse response object into python dictionary and store
    if response.status_code == 204: #code spotify will throw if nothing playing
        return jsonify({
		     "song": "None",
            "album": "None",
            "artist": "None",
            "albumart" : "None"
        })
    
    if response.status_code == 200:
        item_object = stored_now_playing["item"] #'item' is the main branch which holds all the now-playing info
        artist = [a["name"] for a in item_object["artists"][:3]] #list max 3 artists
        album = item_object["album"]["name"]
        track = item_object["name"]
        albumart = item_object["album"]["images"][0]["url"] #pull the first image [0] which corresponds to the large image size on spotify
        return jsonify({ #parsing the selected values back into json to be returned to whoever calls this link
            "song": track,
            "album": album,
            "artist": artist,
            "albumart" : albumart
        })
    return jsonify({
    "error": "spotify api failed",
    "status": response.status_code,
    "body": response.text
    }), 500
        


@app.route("/api/spotify/play")
def spotifyPlay():
    global token #call global token variable

    headers = { "Authorization" : "Bearer " + token } #token authentication always needed for any Spotify API call
    response = requests.put("https://api.spotify.com/v1/me/player/play", headers=headers) 
    return jsonify({
    "status": response.status_code
    })

@app.route("/api/spotify/pause")
def spotifyPause():
    global token #call global token variable

    headers = { "Authorization" : "Bearer " + token }
    response = requests.put("https://api.spotify.com/v1/me/player/pause", headers=headers)
    return jsonify({
    "status": response.status_code
    })

@app.route("/api/spotify/rewind")
def spotifyRewind():
    global token #call global token variable

    headers = { "Authorization" : "Bearer " + token }
    response = requests.post("https://api.spotify.com/v1/me/player/previous", headers=headers)
    return jsonify({
    "status": response.status_code
    })

@app.route("/api/spotify/forward")
def spotifyForward():
    global token #call global token variable

    headers = { "Authorization" : "Bearer " + token }
    response = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)
    return jsonify({
    "status": response.status_code
    })

    
@app.route ("/api/spotify/restart")
def restartSpotify():
    subprocess.run(["systemctl", "--user", "restart", "spotifyd"])
    return "ok"


#SPOTIFY TOKEN AUTHENTICATION FLOW
#a series of app.routes and functions that all pertain to gaining access and authenticating spotify API's. This is done through
#redirecting to a login screen -> recieves code after login -> uses code to then post to recieve access token/refresh token ->
# refresh function runs to keep access token fresh, it expires every hour and must be refreshed.
#most of it is sending the right info through the Url in a parsed query string, and then taking recieved json info and using
#it for accesss to the spotify API





token = None     #starting the global 'token' variable
client_id = os.getenv("CLIENT_ID") #cliend id /client secret stored in .env file
client_secret = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://127.0.0.1:80/callback'; #where spotify sends you after login
SCOPE = "user-read-playback-state user-modify-playback-state user-read-private user-read-email"
STATE = secrets.token_urlsafe(16) #generate 16 random code
auth_string = client_id + ":" + client_secret #string to be encoded 
auth_bytes = auth_string.encode("utf-8") #encoding string into bytes
auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")  #encoding bytes into base64, needed for URL query parsing


@app.route("/callback")
def callback():
    global token #call global token variable

    code = request.args.get("code") #request.arg.get() will take the URL query string and parse into usable string
    state = request.args.get("state")
    headers =  {
	 'Content-Type': 'application/x-www-form-urlencoded', #all in the spotify documentation
	 'Authorization':'Basic ' + auth_base64 #heres that encoded base64 encoded clientid:clientsecret
	   }
    data = {
		"code": code,
		"redirect_uri": REDIRECT_URI,
		"grant_type": 'authorization_code'
	}


   
    r = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers) #post to url address to get response object
    #variable r now contains the response object that spotify sent back, which contains all the info for tokens etc. 
    response_json = r.json() #this creates a python dictionary from the json file that gets returned from spotify
    token = response_json["access_token"] # get the string from the python dictionary we just created and store access token under global variable 'token'
    refresh_token = response_json["refresh_token"]

    refresh_object = open("refresh_token.txt", "w") #open file to store refresh_token, 'w' is write, it will delete/overwrite whats in there
    refresh_object.write(refresh_token) #write refresh token to file
    refresh_object.close() #close the writing file portion

    start_refresh_thread_once() #start the refreshing thread daemon now that the refresh token is secured (only needs to happen once)

    return "tokens stored"




@app.route("/spotify/login")
def get_token():
    payload = {
        'client_id':client_id,
        'response_type':'code',
        'redirect_uri':REDIRECT_URI,
        'scope': SCOPE,
        'state': STATE
        }
    query_string = urlencode(payload) #encodes the payload into a query string for URL
    return redirect('https://accounts.spotify.com/authorize?' + query_string) #redirects user to LOGIN screen on spotify with attached query string


# DOCUMENTATION: https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens
@app.route("/spotify/refresh")
def refresh_route():
       refresh_access_token()
       return "refreshed"



def refresh_access_token():
    global token #calling global token variable
    rTobject = open("refresh_token.txt", "r") #reading the saved file "refresh_token.txt" that we saved earlier
    stored_refresh_token = rTobject.read().strip()
    rTobject.close()
    params = {
        'grant_type' : 'refresh_token',
        'refresh_token' : stored_refresh_token
    }
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Authorization' : 'Basic ' + auth_base64
    }

    refresh_token_response_object = requests.post("https://accounts.spotify.com/api/token", data=params, headers=headers)
    if refresh_token_response_object.status_code == 200: 
       
        refresh_json = refresh_token_response_object.json() #make python dictionary out of json response object

        if ("access_token" in refresh_json)== True: #if the key 'access_token' exists:
            token = refresh_json["access_token"] #change global variable 'token' to the new access token
            print("Access token refreshed.")

        else: 
            print("Refresh token not included")
    else:
        print("Refresh failed:", refresh_token_response_object.status_code, refresh_token_response_object.text)
       
def token_refresh_loop(): #calls the refresh token fucntion every 50 minutes to keep seamless playback possible
    while True:
        time.sleep(50 * 60)  # 50 minutes
        refresh_access_token()

refresh_thread_started = False #this value resets every reboot/fresh run


def start_refresh_thread_once(): #makes sure the thread service daemon is only running once
    global refresh_thread_started 
    if refresh_thread_started == True: 
        return
    refresh_thread_started = True #once value is true, it will run start the thread once, and now only 'return' when called
    threading.Thread(target=token_refresh_loop, daemon=True).start() #this creates a thread that calls refresh loop in the background


if os.path.exists("refresh_token.txt"): #check to see if refresh_token.txt file has been created/stored
    start_refresh_thread_once()  #start the daemon service

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
