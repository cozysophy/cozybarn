#include <FastLED.h>
#include <ArduinoOTA.h>
#include <Arduino.h>
#include <WiFi.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>

//ESP32 runs two led strips, using OTA, and mqtt subscriber. The message gets
//transcribed into a string, which gets delegated to its right purpose. It subscribes to brightness and pattern, 
//and uses enum patterns to use switch cases for each pattern. Pubsubclient handles the mqtt, and 
//ota is...ota


// LED strip configuration
#define LED_TYPE WS2812B
#define DATA_PIN_1 9
#define DATA_PIN_2 10
#define DATA_PIN_3 11
#define DATA_PIN_4 47

#define NUM_LEDS_1 50
#define NUM_LEDS_2 300
#define NUM_LEDS_3 80 //speaker
#define NUM_LEDS_4 80 //speaker


//Create Pattern Library
//enum creates a list 0,1,2 etc. that you can call from strings
enum Pattern {
  PATTERN_OFF,
  PATTERN_RAINBOW,
  PATTERN_WHITE
};

//Variable that holds current pattern
//it comes from Pattern, and will only accept whatever is in the enum
Pattern currentPattern = PATTERN_RAINBOW;

//makes rainbow go brrrr
uint8_t oneMore = 0;

//Callback header that was needed before pubsubclient declaration
void mqttCallback(char* topic, byte* payload, unsigned int length);

// Network for PubSubClient
WiFiClient wifiClient;
PubSubClient client("10.42.0.1", 1883, mqttCallback, wifiClient); //client(IPaddress, port, callback function pointer, networkclient)
                                                                  //note: client is just a name variable, used for all the .stuff, if you change it
                                                                  //you have to change all of those, as well (ex. client.connected)





// Analog pins for potentiometers
const uint8_t BRIGHTNESS_POT_PIN = 34;
const uint8_t WHITE_BALANCE_POT_PIN = 35;

//Declare LED strips in FastLED struct
CRGB strip1[NUM_LEDS_1];
CRGB strip2[NUM_LEDS_2];
CRGB strip3[NUM_LEDS_3]; //speaker
CRGB strip4[NUM_LEDS_4]; //speaker


// ChatGPT garbge
//unsigned long lastUpdate = 0;


// Set Wifi Credentials
const char* ssid = "trannyfix";
const char* password = "transgender";

// PubSubClient reconnect sequence
void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("sophieMainLEDs")) {
      Serial.println("Sophie's mqtt connected!!");
      //subscriber topics
      client.subscribe("soph/main/brightness");  //***********SUBSCRIBER TOPICS**********************************
      client.subscribe("soph/main/pattern");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" booooo we will try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

// MQTT Callback: takes the byte message, and converts it into a string word so it can be understood now
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  //create variable incomingMessage to store message
  String incomingMessage = "";
  incomingMessage.reserve(length);
  

  // Convert incoming byte array to String
  for (unsigned int i=0;i<length;i++) {
    incomingMessage += (char)payload[i];
  }

  // Call LED Function to process topic/message string
  mainLights(topic, incomingMessage);
}




void setup() {

 //  currentPattern = PATTERN_RAINBOW; <-- for solving starting pattern issues, idk
  FastLED.addLeds<LED_TYPE, DATA_PIN_1, GRB>(strip1, NUM_LEDS_1);
  FastLED.addLeds<LED_TYPE, DATA_PIN_2, GRB>(strip2, NUM_LEDS_2);
  FastLED.addLeds<LED_TYPE, DATA_PIN_3, GRB>(strip3, NUM_LEDS_3);
  FastLED.addLeds<LED_TYPE, DATA_PIN_4, GRB>(strip4, NUM_LEDS_4);


soph_rainbow();    //set initial pattern that doesnt rely on mqtt connection, helps
                  //when the server isnt running and you just want some light
FastLED.setBrightness(60); //set initial brightness
  

  
  // delay for stability
  delay(500);


  //Begin Serial Monitoring
  Serial.begin(115200);
  Serial.println("Booting");
  // Connect to Wifi
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //Connect to wifi - defaults to Wifi Station Mode
  //Wait for Wifi to connect
  while (WiFi.waitForConnectResult() != WL_CONNECTED) {
    Serial.println("Connection Failed! Rebooting...");
    delay(5000);
    ESP.restart();
  }
  ArduinoOTA.setHostname("sophieMainpuss");
  ArduinoOTA.begin();  // Begin OTA
  Serial.println("Ready");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());


 
}

void loop() {

  ArduinoOTA.handle(); // OTA command neeed in loop

  if (!client.connected()) { //PubSubClient reconnect
    reconnect();
  }

  client.loop(); //PubSubClient loop


  switch (currentPattern) {  //Choose the LED pattern
    case PATTERN_OFF:
      fill_solid(strip1, NUM_LEDS_1,CRGB::Black);
      fill_solid(strip2, NUM_LEDS_2,CRGB::Black);
      fill_solid(strip3, NUM_LEDS_3,CRGB::Black);
      fill_solid(strip4, NUM_LEDS_4,CRGB::Black);

  /*if you wanted to do an array:
  
  CRGB* strips[] = { strip1, strip2, strip3, strip4 };
uint16_t lengths[] = { NUM_LEDS_1, NUM_LEDS_2, NUM_LEDS_3, NUM_LEDS_4 };

for (int i = 0; i < 4; i++) {
  fill_solid(strips[i], lengths[i], CRGB::Black);
}

*/

      break;

    case PATTERN_RAINBOW:
      soph_rainbow();
      break;

    case PATTERN_WHITE:
      whiteLEDstate();
      break;

  }

  FastLED.show();  //push the led pattern and light LED's
  
}




// *******MQTT Brightness/Pattern Topic Function ***********

//note: const means read-only, String& means dont make a copy to use, just read the original, otherwise it would make a whole copy for this func to use
void mainLights(const String& topic, const String& incomingMessage){ 
  if(topic=="soph/main/brightness"){
    int brightness = incomingMessage.toInt(); //changes string number into actual number (value)
                                              // ex. "43" vs 43
    FastLED.setBrightness(brightness);     //change the brightness to new value
  }

  else if (topic=="soph/main/pattern"){    //Pattern Mqtt selection
    if (incomingMessage=="rainbow"){     
      currentPattern = PATTERN_RAINBOW;
    }
    else if (incomingMessage=="solidwhite"){ 
      currentPattern = PATTERN_WHITE;
    }
    else if (incomingMessage=="off"){
      currentPattern = PATTERN_OFF;
    }
    }
  else {Serial.println("oops topic/message didn't work in the led function");}
}


void whiteLEDstate(){
  //int brightnessRaw = analogRead(BRIGHTNESS_POT_PIN);
 // int balanceRaw = analogRead(WHITE_BALANCE_POT_PIN);

  //uint8_t brightness = map(brightnessRaw, 0, 4095, 0, 255);
  //uint8_t whiteBalance = map(balanceRaw, 0, 4095, 110, 220);

  // Shift white between warm (more red) and cool (more blue).
  uint8_t red = 255;
  uint8_t green = 220;
  uint8_t blue = 200;

  CRGB whiteColor = CRGB(red, green, blue);

  for (int i = 0; i < NUM_LEDS_1; i++) {
    strip1[i] = whiteColor;}

      for (int i = 0; i < NUM_LEDS_2; i++) {
    strip2[i] = whiteColor;}

      for (int i = 0; i < NUM_LEDS_3; i++) {
    strip3[i] = whiteColor;}

      for (int i = 0; i < NUM_LEDS_4; i++) {
    strip4[i] = whiteColor;}
  }

unsigned long lastUpdate = 0;
const unsigned long rainbowDelay = 50; // higher = slower

void soph_rainbow() {     //Rainbow Pattern

  if (millis() - lastUpdate < rainbowDelay) return;
  lastUpdate = millis();

    fill_rainbow(strip1,NUM_LEDS_1,oneMore,10);
    fill_rainbow(strip2,NUM_LEDS_2,oneMore,10);
    fill_rainbow(strip3,NUM_LEDS_3,oneMore,10);
    fill_rainbow(strip4,NUM_LEDS_4,oneMore,10);
  oneMore++; 
}


