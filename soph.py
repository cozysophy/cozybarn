from paho.mqtt import client as mqtt
from flask import Flask, send_file

#TODO: 
#- -create app routes for seperate webpage for camming lights
#       create buttons/update file locations
# --create app routes for main LED pattern, main LED brightness
#-- create html webpage for main LED button/create buttons
# JUST TESTING BECAUSE GAAAAAAAAAAAAAAAAAAAWD


#port gets set in the service not the py

#start the MQTT client and stay connected
client = mqtt.Client(client_id="soph")
client.connect("10.42.0.1", 1883, 30) #(IP of broker, port of broker, keepAlive)
client.loop_start() #keeps network flowing
#not loop_forever because it blocks. It prevents anything else and stays 
#in MQTT forever


app = Flask(__name__)


			#API CALLS
@app.route("/api/main/pattern/rainbow", methods=['POST'])
def rainbowmain():
	client.publish("soph/main/pattern", "rainbow")
	return "ok"

@app.route("/api/mainbrightness/<valtwo>", methods=['POST'])
def brightnessmain(valtwo):
		client.publish("soph/main/brightness", valtwo)
		return "ok"
		
@app.route("/api/main/pattern/solidwhite", methods=['POST'])
def solidwhitemain():
	client.publish("soph/pattern", "solidwhite")
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
	
@app.route("/api/brightness/<val>", methods=['POST'])
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
	
	
if __name__ == "__main__":
	app.run(host="10.42.0.1", port=800)
