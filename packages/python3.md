## install yaml, jinja2 for python3 on msys2 (Windows)


	$ pacman -S libcrypt libcrypt-devel openssl openssl-devel python-pip

	$ tar -zxf yaml-0.2.5.tar.gz

	$ cd yaml-0.2.5/

	$ ./configure

	$ make && make install

	$ cd ../
	
	$ tar -zxf PyYAML-5.3.1.tar.gz
	
	$ cd PyYAML-5.3.1/
	
	$ python setup.py build
	
	$ python setup.py install

	$ pip install jinja2

## install yaml, jinja2 for python3 on cmd (Windows)

- install python-3.9.6-amd64.exe

- open cmd and types:

	> pip install yaml

	> pip install jinja2
