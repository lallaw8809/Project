/* User space application to communicate with linux kernel module using ioctl
 * It pass the integer to the LKM and reads the response from LKM.
 * 
 * Author : Lal Bosco Lawrence   
 * Date   : 09-Aug-2018
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include<sys/ioctl.h>
#include <time.h>

#define DEVICE_NAME "/dev/led_button"

/* _IO, _IOW, _IOR, _IORW are helper macros to create a unique ioctl identifier and 
   add the required R/W needed features (direction).
   These can take the following params: magic number, the command id, and the data
   type that will be passed (if any)
*/
#define WR_VALUE _IOW('a','a',int32_t*)
#define RD_VALUE _IOR('a','b',int32_t*)

#include <time.h>

/* Function generate a ms delay */
void delay(int number_of_seconds)
{
	/* Converting time into milli_seconds */
	int milli_seconds = 1000 * number_of_seconds;
	/* Stroing start time */     
	clock_t start_time = clock();
	/* looping till required time is not acheived */
	while (clock() < start_time + milli_seconds);
}

int main()
{
        int fd,fd1,i=0;
        int32_t value, number;
	char result[1];

        printf("Opening Driver\n");
 	/* Open the device file to get the status of button */
 	fd = open(DEVICE_NAME, O_RDWR);
        if(fd < 0) {
                printf("Unable to open device file...\n");
                return 0;
        }

	/* Read the device file at every 30 sec 
	 * Update the status into status file
	 * */
	for(;;)
	{
        	printf("Reading Value from Driver\n");
		/* Read the status from device file */
        	ioctl(fd, RD_VALUE, (int32_t*) &value);
        	printf("Value is %d\n", value);
	
		fd1 = open("status",O_CREAT | O_RDWR, 0777);
		if(fd1 < 0){
			printf("Unable dto open the status file\n");
			exit(0);
		}
		/* covert int to string */
		sprintf(result, "%d", value);
		/* Update the status into status file */
		write(fd1,result,1);
		/* 3 s delay */
		delay(3000);
	
	}
        printf("Closing Driver\n");
        close(fd);
	close(fd1);
}

