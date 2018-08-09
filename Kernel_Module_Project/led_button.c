/* Linux kernel module for LED and button
 * Using ioctl, user space application can read the status of the LED
 * and updates into URL
 * 
 * Author : Lal Bosco Lawrence   
 * Date   : 09-Feb-2018
 */
 
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/gpio.h>                 // Required for the GPIO functions
#include <linux/interrupt.h>            // Required for the IRQ code
#include <linux/delay.h>
#include <linux/version.h>
#include <linux/types.h>
#include <linux/kdev_t.h>
#include <linux/fs.h>       //File system structure
#include <linux/uaccess.h>  //Required for the copy to user function
#include <linux/ioctl.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("LAL BOSCO");
MODULE_DESCRIPTION("A Button/LED test driver for the RPI3");
MODULE_VERSION("0.1");

#define PROJECT_TAG "LED_BUTTON_TEST : "
/* _IO, _IOW, _IOR, _IORW are helper macros to create a unique ioctl identifier and 
   add the required R/W needed features (direction).
   These can take the following params: magic number, the command id, and the data
   type that will be passed (if any)
*/
#define WR_VALUE _IOW('a','a',int32_t*)
#define RD_VALUE _IOR('a','b',int32_t*)

#define DEVICE_NAME "led_button"
 
/* Pin numbers are mapped based on BCM */
static unsigned int gpioLED   = 14; 
static unsigned int gpioButton = 4; 
static unsigned int irqNumber;
static unsigned int numberPresses = 0;
int button_status;
int majorNumber;

/* Button IRQ handler */
static irq_handler_t  button_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs);
static int reg_chracter_drive(void);
static int     char_dev_open(struct inode *, struct file *);
static int     char_dev_release(struct inode *, struct file *);

#if (LINUX_VERSION_CODE < KERNEL_VERSION(2,6,35))
static int my_ioctl(struct inode *i, struct file *f, unsigned int cmd, unsigned long arg)
#else
static long my_ioctl(struct file *f, unsigned int cmd, unsigned long arg)
#endif
{
	switch(cmd)
	{
		/* MACRO to identify write */
		case WR_VALUE:
			copy_from_user(&button_status ,(int32_t*) arg, sizeof(button_status));
			printk(KERN_INFO "Value received from user space = %d\n", button_status);
			break;
		/* MACRO to identify read */
		case RD_VALUE:
			printk(KERN_INFO "Value send to user space = %d\n", button_status);
			copy_to_user((int32_t*) arg, &button_status, sizeof(button_status));
			button_status=0;
			gpio_set_value(gpioLED, false);
			break;
	}

	return 0;
}

static struct file_operations fops =
{
	.open    = char_dev_open,
	.release = char_dev_release,
	
#if (LINUX_VERSION_CODE < KERNEL_VERSION(2,6,35))
	.ioctl = my_ioctl
#else
	.unlocked_ioctl = my_ioctl
#endif
};
 
/** @brief The LKM initialization function
 *  Initalization of LED and button 
 *  Button initialization is based on IRQ
 *  @return returns 0 if successful
 */
static int __init led_button_init(void)
{
	int result = 0;
	printk(KERN_INFO "%s Initializing the LED \n",PROJECT_TAG);

	/* Register the character driver */
	if(reg_chracter_drive()<0)
		return -1;

	/* Is the GPIO a valid GPIO number (e.g., the BBB has 4x32 but not all available) */
	if (!gpio_is_valid(gpioLED))
	{
		printk(KERN_INFO "%s invalid LED GPIO\n",PROJECT_TAG);
		return -ENODEV;
	}
	/* LED configuration and initialzation as output */
	gpio_request(gpioLED, "sysfs");          // gpioLED is hardcoded to 14, request it
	gpio_direction_output(gpioLED, false);   // Set the gpio to be in output mode and off
	gpio_set_value(gpioLED, false);          // OFF the led         

	/* Button initailzation */
	gpio_request(gpioButton, "sysfs");       // Set up the gpioButton
	gpio_direction_input(gpioButton);        // Set the button GPIO to be an input
	gpio_set_debounce(gpioButton, 200);      // Debounce the button with a delay of 200ms
	gpio_export(gpioButton, false);

	printk(KERN_INFO "The button state is currently: %d\n", gpio_get_value(gpioButton));

	/* Get the Button IRQ number */
	irqNumber = gpio_to_irq(gpioButton);
	printk(KERN_INFO "GPIO_TEST: The button is mapped to IRQ: %d\n", irqNumber);

	/* IRQ registration */
	result = request_irq(irqNumber,                         // The interrupt number requested
			    (irq_handler_t)  button_irq_handler, // The pointer to the handler function below
			     IRQF_TRIGGER_RISING,               // Interrupt on rising edge (button press, not release)
	                     "button_gpio_handler",             // Used in /proc/interrupts to identify the owner
	                     NULL);                             // The *dev_id for shared interrupt lines, NULL is okay

	printk(KERN_INFO "LED_BUTTON_TEST: The interrupt request result is: %d\n", result);

	return result;
}
 
/* The LKM cleanup function */
static void __exit led_button_exit(void)
{
	printk(KERN_INFO "%s The button state is currently: %d\n",PROJECT_TAG, gpio_get_value(gpioButton));
	printk(KERN_INFO "%s The button was pressed %d times\n", PROJECT_TAG, numberPresses);

	/* Unregister the driver with a major number */
	unregister_chrdev(majorNumber, DEVICE_NAME);

	gpio_set_value(gpioLED, 0);              // Turn the LED off, makes it clear the device was unloaded

	free_irq(irqNumber, NULL);               // Free the IRQ number, no *dev_id required in this case
	gpio_unexport(gpioButton);               // Unexport the Button GPIO
	gpio_free(gpioLED);                      // Free the LED GPIO
	gpio_free(gpioButton);                   // Free the Button GPIO

	printk(KERN_INFO "%s Goodbye from the LKM!\n",PROJECT_TAG);
}
 
/** @brief The GPIO IRQ Handler function
 *  return returns IRQ_HANDLED if successful
 */
static irq_handler_t  button_irq_handler(unsigned int irq, void *dev_id, struct pt_regs *regs)
{
	numberPresses++; 
	button_status=1;
	printk("Number of time the button is pressed : %d\n",numberPresses);
	/* On the LED*/
	gpio_set_value(gpioLED, true);

	return (irq_handler_t) IRQ_HANDLED;      // Announce that the IRQ has been handled correctly
}

static int reg_chracter_drive(void)
{
	/* Register the char driver 
	 * Dynamically allocate a major number for the device
	 * Major device number or 0 for dynamic allocation 
	 */
	majorNumber = register_chrdev(0, DEVICE_NAME, &fops);
	if (majorNumber<0){
		printk(KERN_ALERT "Failed to register the driver with a major number\n");
		return majorNumber;
	}
	printk(KERN_INFO "Successfully register the [%s] driver with major number %d\n" \
					,DEVICE_NAME, majorNumber);
	printk(KERN_INFO "Create a device node...\n");
	printk(KERN_INFO "----------------------------------------------------\n");
	printk(KERN_INFO "sudo mknod /dev/%s c %d 0\n",DEVICE_NAME, majorNumber);
	printk(KERN_INFO "-----------------------------------------------------\n");

	return majorNumber;
}

static int char_dev_open(struct inode *inodep, struct file *fp){
	printk(KERN_INFO "Device has been opened\n");
	return 0;
}

static int char_dev_release(struct inode *inodep, struct file *fp){
	printk(KERN_INFO "Device is successfully closed\n");
	return 0;
}
 
/* Module initialization call up */
module_init(led_button_init);
module_exit(led_button_exit);


