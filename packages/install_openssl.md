# install openssl guide


依次序安装下面的软件包:


## zlib-1.2.11

    (不用: yum install zlib-devel)

    $ cd zlib-1.2.11/

    # only build static:
    # $ CFLAGS="-fPIC" ./configure --prefix=/usr/local --static
    
    # build static and dynamic:
    $ CFLAGS="-fPIC" ./configure --prefix=/usr/local

    $ make clean && make && sudo make install
    
## openssl-1.1.1g

    $ cd openssl-1.1.1g/

    $ ./config --prefix=/usr/local --openssldir=/usr/local/ssl

    $ make clean && make && sudo make install

    $ ./config shared --prefix=/usr/local --openssldir=/usr/local/ssl

    $ make clean && make && sudo make install

    $ sudo sh -c "echo /usr/local/lib64 > /etc/ld.so.conf.d/openssl-1.1.1g.x86_64.conf"

    $ sudo ldconfig
