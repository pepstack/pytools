###########################################################
# Makefile
#   Build libclib
#
# Author: 350137278@qq.com
#
# Update: 2021-06-14
#
# Show all predefinitions of gcc:
#
#   https://blog.csdn.net/10km/article/details/49023471
#
#   $ gcc -posix -E -dM - < /dev/null
#
###########################################################
# Linux, CYGWIN_NT, MSYS_NT, ...
shuname="$(shell uname)"
OSARCH=$(shell echo $(shuname)|awk -F '-' '{ print $$1 }')

# debug | release (default)
RELEASE = 1
BUILDCFG = release

# 32 | 64 (default)
BITS = 64


CC = gcc

# for gcc-8+
# -Wno-unused-const-variable
CFLAGS += -std=gnu99 -D_GNU_SOURCE -fPIC -Wall -Wno-unused-function -Wno-unused-variable

LDFLAGS += -lpthread -lm


#######################################
ifeq ($(RELEASE), 0)
	# debug: make RELEASE=0
	CFLAGS += -D_DEBUG -g
	BUILDCFG = debug
else
	# release: make RELEASE=1
	CFLAGS += -DNDEBUG -O3
	BUILDCFG = release
endif

ifeq ($(BITS), 32)
	# 32bits: make BITS=32
	CFLAGS += -m32
	LDFLAGS += -m32
else
	ifeq ($(BITS), 64)
		# 64bits: make BITS=64
		CFLAGS += -m64
		LDFLAGS += -m64
	endif
endif

ifeq ($(OSARCH), MSYS_NT)
	ifeq ($(BITS), 64)
		CFLAGS += -D__MINGW64__
	else
		CFLAGS += -D__MINGW32__
	endif
endif

ifeq ($(OSARCH), CYGWIN_NT)
	ifeq ($(BITS), 64)
		CFLAGS += -D__CYGWIN64__ -D__CYGWIN__
	else
		CFLAGS += -D__CYGWIN32__ -D__CYGWIN__
	endif
endif


#######################################
PREFIX = .

SRC_DIR = $(PREFIX)/src
COMMON_DIR = $(PREFIX)/src/common

INCLUDE_DIRS += -I$(PREFIX) \
	-I$(SRC_DIR) \
	-I$(COMMON_DIR)

	
CLIB_DIR = $(PREFIX)/src/clib

CLIB_VERSION_FILE = $(CLIB_DIR)/VERSION
CLIB_VERSION = $(shell cat $(CLIB_VERSION_FILE))

CLIB_STATIC_LIB = libclib.a
CLIB_DYNAMIC_LIB = libclib.so.$(CLIB_VERSION)

CLIB_DIST_ROOT = $(PREFIX)/libclib-$(CLIB_VERSION)
CLIB_DIST_LIBDIR=$(CLIB_DIST_ROOT)/lib/$(OSARCH)/$(BITS)/$(BUILDCFG)

DIST_APPS_ROOT = $(PREFIX)/dist-apps


# C objects
CLIB_OBJS = clib.o



all: $(CLIB_DYNAMIC_LIB) $(CLIB_STATIC_LIB).$(OSARCH) 


help:
	@echo
	@echo Build libclib-$(shell cat $(CLIB_VERSION_FILE)) for:
	@echo
	@echo "1) 64 bits release (default)"
	@echo "    $$ make"
	@echo
	@echo "2) 32 bits debug"
	@echo "    $$ make RELEASE=0 BITS=32"
	@echo
	@echo Dist target into default path: ${CLIB_DIST_ROOT}"
	@echo "    $$ make dist"
	@echo
	@echo Dist target into given path:
	@echo "    $$ make CLIB_DIST_ROOT=/path/to/YourInstallDir dist"
	@echo
	@echo "Show make options:"
	@echo "    $$ make help"


$(CLIB_STATIC_LIB).$(OSARCH): $(CLIB_OBJS)
	rm -f $@
	rm -f $(CLIB_STATIC_LIB)
	ar cr $@ $(CLIB_OBJS)
	rm -f $(CLIB_OBJS)
	ln -s $@ $(CLIB_STATIC_LIB)


$(CLIB_DYNAMIC_LIB): $(CLIB_OBJS)
	$(CC) $(CFLAGS) -shared \
		-Wl,--soname=$(CLIB_DYNAMIC_LIB) \
		-Wl,--rpath='$(PREFIX):$(PREFIX)/lib:$(PREFIX)/../lib:$(PREFIX)/../libs/lib' \
		-o $@ \
		$(CLIB_OBJS) \
		$(LDFLAGS)


clib.o: $(CLIB_DIR)/clib.c
	$(CC) $(CFLAGS) -c $(CLIB_DIR)/clib.c $(INCLUDE_DIRS) -I$(CLIB_DIR) -o $@


dist: all
	@mkdir -p $(CLIB_DIST_ROOT)/include/clib
	@mkdir -p $(CLIB_DIST_ROOT)/include/common
	@mkdir -p $(CLIB_DIST_LIBDIR)
	@cp $(COMMON_DIR)/unitypes.h $(CLIB_DIST_ROOT)/include/common/
	@cp $(CLIB_DIR)/clib_api.h $(CLIB_DIST_ROOT)/include/clib/
	@cp $(CLIB_DIR)/clib_def.h $(CLIB_DIST_ROOT)/include/clib/
	@cp $(PREFIX)/$(CLIB_STATIC_LIB).$(OSARCH) $(CLIB_DIST_LIBDIR)/$(CLIB_STATIC_LIB)
	@cp $(PREFIX)/$(CLIB_DYNAMIC_LIB) $(CLIB_DIST_LIBDIR)/$(CLIB_DYNAMIC_LIB)


clean:
	-rm -f $(PREFIX)/*.stackdump
	-rm -f $(PREFIX)/*.o
	-rm -f $(PREFIX)/$(CLIB_STATIC_LIB)
	-rm -f $(PREFIX)/$(CLIB_STATIC_LIB).*
	-rm -f $(PREFIX)/$(CLIB_DYNAMIC_LIB)
	-rm -f $(PREFIX)/msvc/*.VC.db
	-rm -rf $(PREFIX)/msvc/libclib/build
	-rm -rf $(PREFIX)/msvc/libclib/target
	-rm -rf $(PREFIX)/msvc/libclib_dll/build
	-rm -rf $(PREFIX)/msvc/libclib_dll/target
	-rm -rf $(PREFIX)/msvc/test_clib/build
	-rm -rf $(PREFIX)/msvc/test_clib/target
	-rm -rf $(PREFIX)/msvc/test_clibdll/build
	-rm -rf $(PREFIX)/msvc/test_clibdll/target
	-rm -rf $(PREFIX)/dist-apps/Debug
	-rm -rf $(CLIB_DIST_LIBDIR)


cleanall: clean
	-rm -rf $(DIST_APPS_ROOT)
	-rm -rf $(CLIB_DIST_ROOT)


.PHONY: clean cleanall dist
