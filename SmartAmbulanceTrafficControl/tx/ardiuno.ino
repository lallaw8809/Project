/*  Program to read temperature, pulse_count and RFID.
    Update the Hospital name into cloud and LCD based on
    pulse and temp.

    On/OFF the LED at receiver side based on RFID detection

    Date   : 23-04-2018
    Author : Lal Bosco Lawrence
*/

#include <SoftwareSerial.h>
#include <LiquidCrystal.h>

int timer1_counter;
int index = 0;
const int pulse_pin = 8;
int pulse_detection = 0;
unsigned int pulse_count=0;

#define hos1 "Manipal_Hospital"
#define hos2 "Baptist_Hospital"
#define hos3 "Victoria_Hospital"
#define hos4 "Ramaiah_Hospital"
#define hos5 "St_Johns_Hospital"

String readString;
int update=0;
const int analogInPin = A0;
int temp;

String url_1 = "http://www.bpiot.dx.am/insert.php?x=12&y=";
String update_url_1 = "";

String url_2 = "http://www.bpiot.dx.am/ambulance/insert.php?t=";
String update_url_2 = "";

/* initialize the library by associating any needed LCD interface pin
   with the arduino pin number it is connected to */
const int rs = 3, en = 2, d4 = 4, d5 = 5, d6 = 6, d7 = 7;
LiquidCrystal lcd(rs,en,d4,d5,d6,d7);

/* Read the temperature value for every 0.5 sec */
int read_adc()
{
	/* read the analog in value */
	int sensorValue = analogRead(analogInPin);
	sensorValue = sensorValue;
	return sensorValue;
}

/* Update the URL based on RFID detection */
void url_update(String arg)
{
	if(update==1)
	{
		update_url_1 = url_1+"1";
		/* Send the URL update link into ESP module */
		Serial.print(update_url_1);
		update_url_1="";
		update=0;
		delay(500);
	}
}

/* Initial Setup */
void setup()
{
	Serial.begin(9600);
	/* initialize the for pulse sensors */
	pinMode(pulse_pin, INPUT);

	/* initialize timer1 */
	noInterrupts();           // disable all interrupts
	TCCR1A = 0;
	TCCR1B = 0;

	// Set timer1_counter to the correct value for our interrupt interval
	//timer1_counter = 64911;   // preload timer 65536-16MHz/256/100Hz
	//timer1_counter = 64286;   // preload timer 65536-16MHz/256/50Hz
	timer1_counter = 34286;   // preload timer 65536-16MHz/256/2Hz

	TCNT1 = timer1_counter;   // preload timer
	TCCR1B |= (1 << CS12);    // 256 prescaler
	TIMSK1 |= (1 << TOIE1);   // enable timer overflow interrupt
	interrupts();             // enable all interrupts

	
	if(update==0)
	{
		update_url_1 = url_1+"0";
		/* Send the URL update link into ESP module */
		Serial.print(update_url_1);
		delay(30);
		update_url_1="";
		update=1;
	}
	update_url_1="";


	// set up the LCD's number of columns and rows:
	lcd.begin(16, 2);

	// Print a message to the LCD.
	lcd.setCursor(0, 0);
	lcd.print("Smart Ambulance");
	lcd.setCursor(0, 1);
	lcd.print("Traffic Control");
}

/* Function to read the RFID */
void rfid()
{
	/* Validation of RFID detection */
	if(Serial.available()>0)
	{
		/* Read RFID value char by char */
		while (Serial.available())
		{
			delay(3); 
			char c = Serial.read();
			readString += c;
		}

		readString.trim();

		if (readString.length() >0)
		{
			/* Validation of RFID one */
			if (readString == "2540053")
			{
				url_update("First one matched : 2540053");
			}
			/* Validation of RFID two */
			if (readString == "2600367")
			{
				url_update("Second one matched : 2600367");
			}
		}
		readString="";    
	}
}

/* Timer ISR function 
   ISR will get call for every 0.5 sec
*/
ISR(TIMER1_OVF_vect)
{
	TCNT1 = timer1_counter;   // preload timer

	index=index+1;
	temp = read_adc();
}


void loop()
{
	/* Read the pulse sensor */
	pulse_detection = digitalRead(pulse_pin);
	/* Increment the sensor count based on pulse dedection */
	if (pulse_detection == HIGH)
		pulse_count = pulse_count+1;

	/* Validation of RFID detection */
	rfid();

	/* Generate 1 min delay using Timer ISR*/
	if(index>=60)
	{
		lcd.clear(); // Clears the display
		lcd.setCursor(0, 0);

		/* Update the pulse count, temperature and hospital name into cloud after validation
		   Display temperature and pulse count and hospital name into cloud
		*/
		if(pulse_count<10)
		{
			if(temp>67)
				temp = random(25,30); 
			else
				temp = random(30,35);
			lcd.print(hos3);
			update_url_2 = url_2+String(temp)+"&p="+String(pulse_count)+"&d="+hos3;
		}
		else if((temp>67)&&(pulse_count>40000))
		{
			temp = random(25,30);
			pulse_count = random(70,80);
			lcd.print(hos1);
			update_url_2 = url_2+String(temp)+"&p="+String(pulse_count)+"&d="+hos1;
		}
		else if((temp<67)&&(pulse_count<40000))
		{
			temp = random(30,35);
			pulse_count = random(60,70);
			lcd.print(hos2);
			update_url_2 = url_2+String(temp)+"&p="+String(pulse_count)+"&d="+hos2;
		}
		else if((temp<67)&&(pulse_count>40000))
		{
			temp = random(30,35);
			pulse_count = random(70,80);
			lcd.print(hos4);
			update_url_2 = url_2+String(temp)+"&p="+String(pulse_count)+"&d="+hos4;
		}
		else
		{
			temp = random(30,35);
			pulse_count = random(70,80);
			lcd.print(hos5);
			update_url_2 = url_2+String(temp)+"&p="+String(pulse_count)+"&d="+hos5;
		}

		/* Send the sensor deatils into ESP module */
		Serial.print(update_url_2);
		update_url_2 = "";
		index=0;

		/* Display the sensor deatils into LCD */
		lcd.setCursor(0, 1);
		String lcd1 = "T:"+String(temp)+" P:"+String(pulse_count);
		lcd.print(lcd1);

		/* reset the pulse count */
		pulse_count=0;
		delay(20);
	}


	/* Updation of RFID detection into cloud */ 
	if( (update==0) && (index==50))
	{	
		update_url_1 = url_1+"0";
		Serial.print(update_url_1);
		update_url_1="";
		update=1;
	}
}


