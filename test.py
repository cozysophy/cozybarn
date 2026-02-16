
from dotenv import load_dotenv
from flask import Flask, request, redirect
from urllib.parse import urlencode
import requests
import os
import secrets
import base64

load_dotenv()

token = None
client_id = os.getenv("CLIENT_ID") #cliend id /client secret stored in .env file
client_secret = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://10.42.0.1:80/callback';
SCOPE = 'user-read-private user-read-email';
STATE = secrets.token_urlsafe(16) #generate 16 random code
auth_string = client_id + ":" + client_secret
auth_bytes = auth_string.encode("utf-8") #encoding into bytes
auth_base64 = str(base64.b64encode(auth_bytes), "utf-8") 


@app.route("/callback")
def callback():
    global token 

    code = request.args.get("code") 
    state = request.args.get("state")
    headers =  {
	 'Content-Type': 'application/x-www-form-urlencoded',
	 'Authorization':'Basic ' + auth_base64
	   }
    data = {
		"code": code,
		"redirect_uri": REDIRECT_URI,
		"grant_type": 'authorization_code'
	}


   
    r = requests.post('https://accounts.spotify.com/api/token', data=data, headers=headers) 

    response_json = r.json() #this creates a python dictionary from the json file that gets returned from spotify
    token = response_json["access_token"] # get the string from the python dictionary we just created and store access token under global variable 'token'
    refresh_token = response_json["refresh_token"]

    refresh_object = open("refresh_token.txt", "w") #open file to store refresh_token, 'w' is write, it will delete/overwrite whats in there
    refresh_object.write(refresh_token) #write refresh token to file
    refresh_object.close() #close the writing file portion

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
    query_string = urlencode(payload)
    return redirect('https://accounts.spotify.com/authorize?' + query_string)



@app.route("/spotify/refresh")
def refresh_token():
    global token
    rTobject = open("refresh_token.txt", "r")
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
    
    refresh_token_response_object = requests.post("https://accounts.spotify/.com/api/token", data=params, headers=headers)
    if refresh_token_response_object.status_code == 200:
       refresh_json = refresh_token_response_object.json()
       token = refresh_json["access_token"]
       return "refreshed"
    
