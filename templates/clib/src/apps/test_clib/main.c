/**
 * main.c
 *   clib static lib test app.
 */
#include <common/cstrbuf.h>

#include <clib/clib_api.h>


int main(int argc, char *argv[])
{
    WINDOWS_CRTDBG_ON

    const char *libname;
    const char *libversion = clib_lib_version(&libname);

    printf("start testing: %s-%s\n", libname, libversion);


    printf("test end.\n");
    return 0;
}