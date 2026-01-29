from paho.mqtt import client as mqtt
from flask import Flask, send_file

#TODO: 
#- -create app routes for seperate webpage for camming lights
#       create buttons/update file locations
# --create app routes for main LED pattern, main LED brightness
#-- create html webpage for main LED button/create buttons



#port gets set in the service not the py

#start the MQTT client and stay connected
client = mqtt.Client(client_id="soph")
client.connect("10.42.0.1", 1883, 30) #(IP of broker, port of broker, keepAlive)
client.loop_start() #keeps network flowing
#not loop_forever because it blocks. It prevents anything else and stays 
#in MQTT forever


app = Flask(__name__)

@app.route("/")
def soph(name=None):
	return send_file("/home/sophie/sophcode/haha.html")
	
@app.route("/api/pattern/rainbow", methods=['POST'])
def rainbow():
	client.publish("soph/pattern", "rainbow")
	return "ok"

@app.route("/api/pattern/off", methods=['POST'])
def off():
	client.publish("soph/pattern", "off")
	return "ok"
	
@app.route("/api/pattern/solidwhite", methods=['POST'])
def solidwhite():
	client.publish("soph/pattern", "solidwhite")
	return "ok"
	
@app.route("/api/brightness/<val>", methods=['POST'])
def brightness(val):
		client.publish("soph/brightness", val)
		return "ok"

@app.route("/brightness")
def brightweb():
		return send_file("/home/sophie/sophcode/brightness.html")
	
	
if __name__ == "__main__":
	app.run(host="10.42.0.1", port=800)


#mqttc.loop_forever(retry_first_connection=False)
