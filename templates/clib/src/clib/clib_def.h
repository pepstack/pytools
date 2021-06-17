/**
 * clib_def.h
 */
#ifndef CLIB_DEF_H_INCLUDED
#define CLIB_DEF_H_INCLUDED

#if defined(__cplusplus)
extern "C" {
#endif

#include <common/unitypes.h>

#if defined(CLIB_DLL)
/* win32 dynamic dll */
# ifdef CLIB_EXPORTS
#   define CLIB_API __declspec(dllexport)
# else
#   define CLIB_API __declspec(dllimport)
# endif
#else
/* static lib or linux so */
# define CLIB_API  extern
#endif

typedef int CLIB_BOOL;

#define CLIB_TRUE    1
#define CLIB_FALSE   0


typedef int CLIB_RESULT;

#define CLIB_SUCCESS     0
#define CLIB_ERROR     (-1)


#if defined(__cplusplus)
}
#endif

#endif /* CLIB_DEF_H_INCLUDED */