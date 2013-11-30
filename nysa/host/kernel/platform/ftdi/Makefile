obj-m += nysa_ftdi_platform.o

nysa_ftdi_platform-objs := nysa_ftdi.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
install_dep:
	./ins_m.sh

