from paho.mqtt import client as mqtt
from flask import Flask, send_file
import time
import subprocess


#TODO: 
#import time
#- -create app routes for seperate webpage for camming lights
#       create buttons/update file locations
# --create app routes for main LED pattern, main LED brightness
#-- create html webpage for main LED button/create buttons
# JUST TESTING BECAUSE GAAAAAAAAAAAAAAAAAAAWD


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



        #SPOTIFY CONTROLS

@app.route("/api/spotify/play")
def spotifyPlay():
    return subprocess.run(["playerctl", "play"])

@app.route("/api/spotify/pause")
def spotifyPause():
    return subprocess.run(["playerctl", "pause"])

@app.route("/api/spotify/rewind")
def spotifyRewind():
    return subprocess.run(["playerctl", "previous"])

@app.route("/api/spotify/forward")
def spotifyForward():
    return subprocess.run(["playerctl", "next"])

@app.route ("/api/spotify/songTitle")
def songTitle():
    return subprocess.run(["playerctl", "title"])

@app.route ("/api/spotify/artist")
def artist():
    return subprocess.run(["playerctl", "artist"])

@app.route ("/api/spotify/albumart")
def spoti():  

    #subprocess defined in the docu: https://docs.python.org/3/library/subprocess.html#replacing-bin-sh-shell-command-substitution
    #greps, then awk to get the column of url data, its column three in this case
    p1 = subprocess.Popen(["playerctl", "metadata"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(["grep", "artUrl"], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.Popen(["awk", "{print $3}"], text=True, stdin=p2.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()
    p2.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p3.communicate()[0]
    return output
    
@app.route ("/api/spotify/restart")
def restartSpotify():
    subprocess.run(["systemctl", "--user", "restart", "spotifyd"])
    return "ok"


if __name__ == "__main__":
	app.run(host="10.42.0.1", port=80)
