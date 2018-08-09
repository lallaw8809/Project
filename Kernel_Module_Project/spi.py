############################################################
# Program to read the ADC sensor and LED status
# update into URL
# Author : Lal Bosco Lawrence   
# Date   : 09-Feb-2018
###########################################################

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time
import traceback

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Software SPI configuration:
# Use this hardware connection for RPi3
# CLK  = 23
# MISO = 21
# MOSI = 19
# CS   = 24
#mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
led_status=0;
url_page = 'http://www.bpiot.dx.am/rpi/insert.php?'

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

mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Main program loop.
while True:
	# Read the adc 
	values = [0]*2
	#Read the channel 0
	values[0] = mcp.read_adc(0)
	print 'Temp : ',values[0]

	#Read the led status
	#open the file to get the led status
	file = open("status","r") 
	led_status = file.read();
	file.close()
	print 'led status : ',led_status

	#http://www.bpiot.dx.am/rpi/insert.php?d=0&a=9
	final_url = url_page + 'd='+str(led_status)+'&a='+str(values[0])
	print final_url
	retrieve(final_url)
	print 'Update is done '
	time.sleep(3);]

