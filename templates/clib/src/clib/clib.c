/**
 * clib.c
 */
#include "clib_i.h"


const char * clib_lib_version(const char **_libname)
{
    if (_libname) {
        *_libname = LIBNAME;
    }
    return LIBVERSION;
}