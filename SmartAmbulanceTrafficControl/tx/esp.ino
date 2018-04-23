/*
	Program to insert the sesnor data into MySQL database.

	Date   : 23-04-2018
	Author : Lal Bosco Lawrence
*/

#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

void setup()
{
	/* opens serial port, sets data rate to 9600 bps */
	Serial.begin(9600);  
	/* WiFi connection */
	WiFi.begin("SSID", "PASSWORD");

	/* Wait for the WiFI connection completion */
	while (WiFi.status() != WL_CONNECTED)
	{
		delay(500);
		Serial.println("Waiting for connection");
	}
	Serial.println("WiFi Connected Successfully");
}

void loop()
{
	/* Validation of WiFi Connection */
	if(WiFi.status()== WL_CONNECTED)
	{   
		/* Check the status of string received */
		if (Serial.available() > 0)
		{
			Serial.println("String is received...");
			String str = Serial.readString();

			/* Declare object of class HTTPClient */
			HTTPClient http;
			/* Post the received URL */
			http.begin(str);
			http.POST("Message from ESP8266");
			http.end();
			Serial.println("Posted");

			Serial.println(str);
			Serial.println(str.length());
			delay(200);
		}
	}
	else
	{
		Serial.println("Error in WiFi connection");
	}
}

