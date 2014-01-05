#include <linux/kernel.h>
//#include <linux/ftdi.h>
//#include <linux/ftdi_driver.h>
#include <linux/platform_device.h>

#define DRIVER_DESC "nysa ftdi device"
#define DRIVER_VERSION "v0.01"

#define NYSA_TTY_MAJOR 240

/*
 * Revisions
 *  11/15/2013: Initial Commit
 *
 * */


typedef struct _nysa_ftdi_driver_t nysa_ftdi_driver_t;

static int nysa_platform_probe(struct platform_device *pdev);
static int __devexit nysa_platform_remove(struct platform_device *pdev);

static int nysa_ftdi_open(struct ftdi_driver * driver, struct file * filep);
static void nysa_ftdi_close(struct ftdi_driver * driver, struct file * filep);
static int nysa_ftdi_write(struct ftdi_struct * ftdi,
								const unsigned char *buf, int count);
static int nysa_ftdi_write_room(struct ftdi_struct * ftdi);
static int nysa_ftdi_set_termios(struct ftdi_struct *ftdi, struct ktermios * old);

static struct platform_driver nysa_platform_driver = {
	.probe	= nysa_platform_probe,
	.remove = __devexit_p(nysa_platform_remove),

	.driver = {
		.name = "nysa_ftdi",
		.owner = THIS_MODULE,
	},
};

struct _nysa_ftdi_driver_t {
	struct ftdi_driver *ftdi_driver;
	int lock;
};

static nysa_ftdi_driver_t nysa_ftdi_driver;

static struct ftdi_operations nysa_ftdi_ops = {
	.open = nysa_ftdi_open,
	.close = nysa_ftdi_close,
	.write = nysa_ftdi_write,
	.write_room = nysa_ftdi_write_room,
	.set_termios = nysa_ftdi_set_termios,
};


//insertion and removal of the module
static int __init nysa_ftdi_init(void){
	int result = 0;
	result = platform_driver_register(&nysa_platform_driver);
	printk (KERN_INFO "%s: registering platform", __func__);
	if (result != 0){
		printk (KERN_INFO "%s: Failed to register platform device", __func__);
		return result;
	}
	nysa_ftdi_driver.lock = 0;
	return 0;
}
static void __exit nysa_ftdi_exit(void){
	printk (KERN_INFO "%s: unregistering platform", __func__);
	platform_driver_unregister(&nysa_platform_driver);
}


//insertion and removal of a device
static int nysa_platform_probe(struct platform_device *pdev){
	int result = 0;

	//allocate space for the nysa_ftdi_device
	nysa_ftdi_driver.ftdi_driver = alloc_ftdi_driver(1); //1 ftdi device

	if (nysa_ftdi_driver.ftdi_driver == NULL) {
		return -ENOMEM;
	}


	//initialize the driver
	nysa_ftdi_driver.ftdi_driver->owner = THIS_MODULE;
	nysa_ftdi_driver.ftdi_driver->driver_name = "nysa_ftdi";
	nysa_ftdi_driver.ftdi_driver->name = "nysa_ftdi";
	nysa_ftdi_driver.ftdi_driver->major = NYSA_TTY_MAJOR;

	nysa_ftdi_driver.ftdi_driver->type = TTY_DRIVER_TYPE_SERIAL;
	nysa_ftdi_driver.ftdi_driver->subtype = SERIAL_TYPE_NORMAL;
	nysa_ftdi_driver.ftdi_driver->flags = TTY_DRIVER_REAL_RAW;
	nysa_ftdi_driver.ftdi_driver->ops = &nysa_ftdi_ops;

	nysa_ftdi_driver.ftdi_driver->init_termios = ftdi_std_termios;
	nysa_ftdi_driver.ftdi_driver->init_termios.c_cflag = B9600 | CS8 | CREAD | HUPCL | CLOCAL;
	//ftdi_set_operations(&nysa_ftdi_driver.ftdi_driver, &nysa_ftdi_ops);


	//register this ftdi_device
	//this line registers the first minor number too!, so if you only want one
	//then only register this one
	result = ftdi_register_driver(nysa_ftdi_driver.ftdi_driver);
	if (result){
		printk(KERN_ERR "failed to register nysa_ftdi_driver.ftdi_driver");
		//put_ftdi_driver(nysa_ftdi_driver.ftdi_driver);
		return result;
	}

	//ftdi_register_device(nysa_ftdi_driver.ftdi_driver, 0, NULL);

	printk(KERN_INFO DRIVER_DESC " " DRIVER_VERSION);
	return result;
}
static int __devexit nysa_platform_remove(struct platform_device *pdev){

	ftdi_unregister_driver(nysa_ftdi_driver.ftdi_driver);
	put_ftdi_driver(nysa_ftdi_driver.ftdi_driver);
	return 0;
}


//ftdi specific operations
static int nysa_ftdi_open(struct ftdi_driver * driver, struct file * filep){
	return 0;
}
static void nysa_ftdi_close(struct ftdi_driver * driver, struct file * filep){
}
static int nysa_ftdi_write(struct ftdi_struct * ftdi,
								const unsigned char *buf, int count){
	printk (KERN_INFO "%s: user entered: %s", __func__, buf);
	return count;
}
static int nysa_ftdi_write_room(struct ftdi_struct * ftdi){
	return 10;
}
static int nysa_ftdi_set_termios(struct ftdi_struct *ftdi, struct ktermios * old){
	return 0;
}

module_init(nysa_ftdi_init);
module_exit(nysa_ftdi_exit);

MODULE_DESCRIPTION(DRIVER_DESC);
MODULE_VERSION(DRIVER_VERSION);
MODULE_LICENSE("GPL");
