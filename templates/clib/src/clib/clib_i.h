/**
 * clib_i.h
 */
#ifndef _CLIB_I_H_
#define _CLIB_I_H_

#ifdef _MSC_VER
# pragma warning (disable : 4996)
#endif

#ifdef    __cplusplus
extern "C" {
#endif

static const char LIBNAME[] = "clib";
static const char LIBVERSION[] = "0.0.1";


#include <common/mscrtdbg.h>
#include <common/cstrbuf.h>
#include <common/memapi.h>
#include <common/emerglog.h>

#include "clib_api.h"



#ifdef    __cplusplus
}
#endif

#endif /* _CLIB_I_H_ */
