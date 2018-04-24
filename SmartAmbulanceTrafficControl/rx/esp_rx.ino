/* Program to read data from URL and
 * Transfer the data into Ardiuno
 *  
 *
 * Author : Lal Bosco lawrence
 * Date   : 20-04-2018
 */

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// 0 and 1 into y
//http://www.bpiot.dx.am/insert.php?x=12&y=1
//http://www.bpiot.dx.am/health/test.php

void setup () {
        /* Baud rate for serial */
	Serial.begin(115200);
        /* Initiate wifi connection */
	WiFi.begin("SSID", "PASSWORD");
	/* Validation of WiFi Connection */
	while (WiFi.status() != WL_CONNECTED)
	{
		delay(1000);
		Serial.print("Connecting..");
	}

	Serial.println("WIFI CONNECTED SUCESSFULLY...");
}

void loop()
{
	/*Check WiFi connection status */
	if (WiFi.status() == WL_CONNECTED)
	{
		HTTPClient http;  //Declare an object of class HTTPClient

		http.begin("http://www.bpiot.dx.am/health/test.php");  //Specify request destination
		int httpCode = http.GET();                             //Send the request
		//Check the returning code
		if (httpCode > 0) 
		{ 
			String payload = http.getString();   //Get the request response payload
			/* Parse the data */
			int t = payload[149];

			if(t==48)
				Serial.print("f"); //OFF the led
			else
				Serial.print("o"); //ON the led
		}
		http.end();   //Close connection
	}
	delay(3);    //Send a request every 30 seconds
}


