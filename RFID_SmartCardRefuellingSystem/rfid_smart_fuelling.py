#!/usr/bin/python
#--------------------------------------
#Raspberry Pi based RFID Smart Card
#Refuelling System
#
#Author : Lal Bosco Lawrence
#Date   : 28-April-2018
#--------------------------------------

#import
import RPi.GPIO as GPIO
import serial
import time

############# LCD pin ##############################
# Define GPIO to LCD mapping
LCD_RS = 37
LCD_E  = 35
LCD_D4 = 40
LCD_D5 = 38
LCD_D6 = 36
LCD_D7 = 32

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005
#################################################

######### Keypad Initialization ################
MATRIX = [ [ 1 , 2,  3 , 'A'],
           [ 4 , 5,  6 , 'B'],
           [ 7 , 8,  9 , 'C'],
           ['*', 0, '#', 'D']
         ]

ROW =   [7 ,11,13,15]  #keypad_pin (0-3)
COL =   [12,16,18,22]  #keypad_pin (4-7)
password_store='1234'
#################################################

######### Keypad Initialization ################
BUTTON_PIN1 = 31      # Switch pin1
BUTTON_PIN2 = 33      # Switch pin2
LED_PIN     = 29 # GPIO pin Number
#################################################

def main():
  # Main program block  
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)       # Use BCM GPIO numbers

  #LCD initialization
  lcd_pin_init()

  #Button and led initialization
  button_led_init()

  #Keypad initialization
  keypad_init()

  # Display project name on LCD
  lcd_display("   Refuelling ","     System ",1);
  lcd_display("     Please "  ,"  Swip the card ",2)

  #Uart configuration with baud rate
  port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)

  while 1:
    input_state1 = GPIO.input(BUTTON_PIN1) #Read button 1
    input_state2 = GPIO.input(BUTTON_PIN2) #Read button 2
    if input_state2 == True:
	lcd_display("Unauthenticated "," Please retry ",2)

    if input_state1 == False: 
      lcd_display("     Face "," Not detected",0)
    
    if input_state1 == True:     #Check whether button is pressed
      print 'Enter here'
      lcd_display(" Athenticated ","Show your face ",3)

      while(True):
            rcv = port.read(1) #Receive the data from UART
            if(rcv == ''):
		time.sleep(0.1);
	    elif(rcv != 'A'):
		lcd_display("Invalid ","Entry",2)
	    elif(rcv == 'A'):
		    validate_passd_amt_qty()
		    break;

def validate_passd_amt_qty():
    lcd_display("   Please ","Enter password ",0)
    keypad = read_keypad(4) #Read the keypad
    password = ''.join(str(e) for e in keypad) #convert into string
    if(password == password_store):
	print 'password matched'
        lcd_display("Password Matched","A:amt B:qty",0)
	keypad = read_keypad(1) #Read the keypad
	#For amount validation
	if(keypad[0]=='A'):
		lcd_display("Please","Enter Ammount",0)
		keypad = read_keypad(4) #Read the keypad
		password = ''.join(str(e) for e in keypad)  #convert into string
		lcd_display("Fuel ","Dispensing",0)
		x=int(password)/70
		control_led(x)

	#For quntity validation
	elif (keypad[0]=='B'):
		lcd_display("Please","Enter Quantity",0)
		keypad = read_keypad(4) #Read the keypad
		password = ''.join(str(e) for e in keypad)  #convert into string
		x=int(password);
		control_led(x)

	else:
		lcd_display("Invalid","Input",3)
    else:
	print 'Password mismatched'
	lcd_display("Incorrect Password ","Please retry",3)

def control_led(delay):
	lcd_display("Fuel ","Dispensing",0)
	GPIO.output(LED_PIN,True)  # Turn ON GPIO pin 7
        time.sleep(delay);
	GPIO.output(LED_PIN,False)  # Turn ON GPIO pin 7
        lcd_display("Transaction ","Completed",2)

#Read the keypad at infinite loop
def read_keypad(value):
	password=[0,0,0,0];	
	index =0;

	while 1:
		if(index==value):
			index=0
			break;

		for j in range (4):
			GPIO.output(COL[j],0)

			for i in range(4):
				if GPIO.input (ROW[i]) == 0:
					print MATRIX[i][j]
					password[index]=MATRIX[i][j]
					index=index+1;
					time.sleep(0.5)

					while (GPIO.input(ROW[i]) == 0):
						pass

			GPIO.output(COL[j],1)
	return password

def keypad_init():
	#Row pin initialization as output
	for j in range(4):
		GPIO.setup(COL[j], GPIO.OUT)
		GPIO.output(COL[j], 1)

	#Column polumnin initialization as input
	for i in range (4):
		GPIO.setup(ROW[i], GPIO.IN, pull_up_down = GPIO.PUD_UP)

def lcd_display(str1,str2,delay):
  lcd_string(str1,LCD_LINE_1)
  lcd_string(str2,LCD_LINE_2)
  time.sleep(delay)

def button_led_init():
  GPIO.setup(BUTTON_PIN1, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Enable input and pull up resistors
  GPIO.setup(BUTTON_PIN2, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Enable input and pull up resistors
  GPIO.setup(LED_PIN, GPIO.OUT) # Setup GPIO Pin 7 to Output
    
def lcd_pin_init():
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  lcd_init()

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
