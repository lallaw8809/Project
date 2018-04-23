/* Program to refresh URL.
 * Date   : 23-04-2018
 * Author : Lal Bosco Lawrence
 */

#include <ESP8266WiFi.h>

const char* host = "35.167.121.118";//Ip address

byte byteRead;

const int sleepTimeS = 1*10; // Set sleep time in seconds for the deep sleep cycle

void setup()
{
	/* Initialize the serial with baudrate */
	Serial.begin(9600);
	delay(100);

	WiFi.begin("SSID", "PASSWORD");

	while (WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		Serial.print(".");
	}

	Serial.println("WiFi connected");
	Serial.println("IP address: ");
	Serial.println(WiFi.localIP()); // This is your NodeMCU IP address. Could be handy for other projects
}

void loop()
{
	/* You can get rid of this or decrease it */
	delay(500);

	Serial.print("connecting to ");
	Serial.println(host);

	/* Use WiFiClient class to create TCP connections */
	WiFiClient client;
	const int httpPort = 80;
	/* Validation connecting to the IP address */
	if (!client.connect(host, httpPort))
	{
		Serial.println("connection failed");
		return;
	}
	
	/* To Refresh the URL */
	client.println("POST TYPE_YOUR_URL_HERE");

	Serial.println("closing connection");
}

//Reference
//https://www.hackster.io/leoribg/using-nodemcu-board-to-send-data-to-devicehub-iot-platform-dccc3f
