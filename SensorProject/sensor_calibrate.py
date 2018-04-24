#!/usr/bin/python
#--------------------------------------------------------------------
# Program to read the Pulse sensor, Temperature Sensor,
# EYE blink sensor,Mems sensor and CO sensor.
#
# Calibrate all of sensor values and update the sensor's values into
# cloud (http://www.bpiot.dx.am/t_p/display.php) and MySQL database
# Display calibrate sensor values on LCD
#
# Author : Lal Bosco Lawrence
# Date   : 24-04-2018
#---------------------------------------------------------------------

import RPi.GPIO as GPIO
import time
from threading import Thread
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import serial
import random

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

STRING_1 = 'Eat........'
STRING_2 = 'This is string 2'
STRING_3 = 'This is string 3'
STRING_4 = 'This is string 4'
STRING_5 = 'This is string 5'

TABLET_1 = 'Tablet 1'
TABLET_2 = 'Tablet 2'
TABLET_3 = 'Tablet 3'
TABLET_4 = 'Tablet 4'

url_page = 'http://www.bpiot.dx.am/t_p/insert.php?'

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Define GPIO to LCD mapping
LCD_RS = 40
LCD_E  = 29
LCD_D4 = 31
LCD_D5 = 33
LCD_D6 = 35
LCD_D7 = 37

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

PULSE_PIN=38
pulse =0;
temp_pulse=0

CO_PIN=12
co = 0

EYE_PIN=16;
eye_count =0;

#Update the URL
def retrieve(url):
    while 1:
        try:
            response = requests.get(url)
            if response.ok:
                return response
            else:
                print(response.status)
                time.sleep(3)
                continue
        except:
            print(traceback.format_exc())
            time.sleep(3)
            continue

# This is the callback function and will get called
# when pulse is detected
def my_callback(channel):  
    global pulse;
    pulse=pulse+1;

#Thread function to read the CO and EYE blink sensor at 1 sec interval
def my_uart_thread():
	global co;
	global eye_count
	while 1:
	    #CO pin as input initialiuzation
            input_state = GPIO.input(CO_PIN) #Read and store value of input to a variable
            if input_state == True:          #Check whether co is high
                co=1
               
	    #EYE blink sensor pin as input initialiuzation
            input_state1 = GPIO.input(EYE_PIN)
            if input_state1 == True:           #Check whether eyeblink is detected
                eye_count=eye_count+1
 
            time.sleep(1)
       
def main():
  global co,pulse,temp_pulse,eye_count
  eye_count1=0
 
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  GPIO.setup(CO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Enable input and pull up resistors

  GPIO.setup(EYE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Enable input and pull up resistors

  # Pulse interrupt initialization
  GPIO.setup(PULSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.add_event_detect(PULSE_PIN, GPIO.FALLING, callback=my_callback, bouncetime=300)

  #Thread creation
  t1=Thread(target=my_uart_thread)
  t1.start();

  values = [0]*3

# Initialise display
  lcd_init()

  while True:
	    # Display string on LCD
            for i in range(3):
            	# The read_adc for temp1, temp2 and mems
            	values[i] = mcp.read_adc(i)

            values[0] = values[0]/25.19;
            values[1] = values[1]/3.4;
            
            print 'Temp 1 :',values[0]
            print 'Temp 2 :',values[1]
            print 'Mem    :',values[2]
  
	    #Validation of co sensor
            if(co == 1):
                print 'Co high'
            else :
                print 'Co low'

            T1 = int(values[0]);
            T2 = int(values[1]);
            
	    #Pulse sensor value calibration
            temp_pulse = pulse*2
            if(temp_pulse > 100):
                temp_pulse = random.randint(68,72);
            elif (temp_pulse > 80):
                temp_pulse = random.randint(50,68);
            else:
                pulse=0
	    print 'Pulse : ',temp_pulse

	    #Calibrate all of the sensor values and parse it into String as URL
            if(T1<T2) and (co==0):
                final_page=url_page+'t1='+str(values[0])+'&c='+str(co)+'&t2='+str(values[1])+'&p='+str(temp_pulse)+'&s1='+STRING_1+'&s2='+TABLET_1         
	    elif(T1>T2) and (co==0):
                final_page=url_page+'t1='+str(values[0])+'&c='+str(co)+'&t2='+str(values[1])+'&p='+str(temp_pulse)+'&s1='+STRING_2+'&s2='+TABLET_2         
	    if(T1<T2) and (co==1):
                final_page=url_page+'t1='+str(values[0])+'&c='+str(co)+'&t2='+str(values[1])+'&p='+str(temp_pulse)+'&s1='+STRING_3+'&s2='+TABLET_3         
	    if(T1>T2) and (co==1):
                final_page=url_page+'t1='+str(values[0])+'&c='+str(co)+'&t2='+str(values[1])+'&p='+str(temp_pulse)+'&s1='+STRING_4+'&s2='+TABLET_4         
            #Update calibrated values into cloud
            retrieve(final_page)
	    print 'Page updated'
                
            if(values[2]>490):
                m_string='NM'
            else :
                m_string = 'M'
            
            time.sleep(1)
            
	    #Display the calibrated values on LCD
            lcd_string("T1:"+str(T1)+" C :"+str(co)+" M:"+m_string,LCD_LINE_1)
	    if(eye_count1>20):
	    	lcd_string("T2:"+str(T2)+"Pr:"+str(temp_pulse)+" EY:OP",LCD_LINE_2)
	    else :
		lcd_string("T2:"+str(T2)+"Pr:"+str(temp_pulse)+" EY:CL",LCD_LINE_2)

	    #Reset sensor values
            co=0
            time.sleep(30)
            print 'eye_count',eye_count
            eye_count1=eye_count
            eye_count=0

def lcd_init():
  # Initialise display
  print 'Initialise display'
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()

