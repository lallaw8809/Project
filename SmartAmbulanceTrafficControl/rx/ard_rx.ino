/* Program to control the green and red led based on input
 * received from ESP device.
 * RX_RESP8266 module reads the updated values from URL which is
 * updated by TX_ESP8266 module based on RFID detection.
 *
 * Author : Lal Bosco lawrence
 * Date   : 20-04-2018
 */

#include <SoftwareSerial.h>

/* UART pin Initialization */
SoftwareSerial mySerial(10, 11); // RX, TX

/* LED Pin initialization */
int Red_led   = 7;
int Green_led = 8;

void setup()
{
	/* Open serial communications and wait for port to open:*/
	Serial.begin(115200);
	/* wait for serial port to connect. Needed for native USB port only */
	while (!Serial);

	/* LED pin initialization as output */
	pinMode(Green_led, OUTPUT);
	pinMode(Red_led, OUTPUT);

	/* ON the red led */
	digitalWrite(Red_led, HIGH);
}

void loop() 
{
	char ch;

	/* Validation of recive data */
	if (Serial.available())
	{
		/* Read the data */
		ch = Serial.read();
		Serial.println(ch);
		/* On the Green led
		* OFF the RED led
		*/
		if(ch=='o')
		{
			digitalWrite(Red_led, LOW);
			digitalWrite(Green_led, HIGH);
			delay(1000);
		}
		else
		{
			digitalWrite(Red_led, HIGH);  //ON the RED led
			digitalWrite(Green_led, LOW); //OFF the GREEN led
		}
	}
}
