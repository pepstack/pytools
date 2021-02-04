#!/bin/bash
#
# about curl usage:
#   https://www.cnblogs.com/hujiapeng/p/8470099.html
#
###############################################################
_file=$(readlink -f $0)
_cdir=$(dirname $_file)
_name=$(basename $_file)
_ver=1.0

# Treat unset variables as an error
set -o nounset

# Treat any error as exit
set -o errexit

# Set characters encodeing
#   LANG=en_US.UTF-8;export LANG
LANG=zh_CN.UTF-8;export LANG

# default values for variables:
#     host:port
PROXY=""

PREFIX=${_cdir}/downloads-cache

FILE=""

URI="--"

##############################################################

usage() {
    cat << EOT
Usage :  ${_name} FILE URI
  Use curl proxy to download URI to local FILE.

Options:
  -h, --help                  显示帮助
  -V, --version               显示版本

  -x,--proxy=PROXY      proxy ("host:port") used as option for -x. default is none
  -u,--uri=URI          url address of resource to download. for example: http://www.libsdl.org/release/SDL2-2.0.12.tar.gz
  -f,--file=FILE        specify name for file to save uri. for example: sdl.tar.gz
  -p,--prefix=PATH      path prefix for downloaded file. default: $PREFIX

Samples:

    ${_name} -x 192.168.102.51:11128 -u http://www.libsdl.org/release/SDL2-2.0.12.tar.gz

  or:

    ${_name} --uri=http://www.libsdl.org/release/SDL2-2.0.12.tar.gz --file=sdl.tar.gz


EOT
}

if [ $# -eq 0 ]; then usage; exit 1; fi

# parse options:
RET=`getopt -o Vhu:f:p: \
--l version,help,uri:,file:,proxy:,\
- n ' * ERROR'-- "$@" `

if [ $? != 0 ] ; then echo "$_name exited with doing nothing." >&2 ; exit 1 ; fi

# Note the quotes around $RET: they are essential!
eval set -- "$RET"

# set option values
while true; do
    case "$1" in
        -V | --version)
            echo "$(basename $0) -- version: $_ver"
            exit 1
            ;;

        -h | --help )
            usage
            exit 1
            ;;

        -u | --uri )
            URI="$2"
            shift 2
            ;;

        -f | --file )
            FILE="$2"
            shift 2
            ;;

        -p | --prefix )
            PREFIX="$2"
            shift 2
            ;;


        -x | --proxy )
            PROXY="$2"
            shift 2
            ;;


        -- )
            shift
            break
            ;;

        * ) break
            ;;
    esac
done


# input args validation

if [ ! -d "$PREFIX" ]; then
    echo "Path not exists: $PREFIX"
    exit 1
fi


if [ -z "$FILE" ]; then
    FILE=$(basename $URI)
fi


if [ -a "$PREFIX/$FILE" ]; then
    echo "File already exists:"
    echo "    $PREFIX/$FILE"

    if read -t 5 -p "Overwrite existing file? (yes or no):" answer
      then
        if [ "$answer" == "yes" ]; then
           echo -e "\nFile is being overwritten!"
        else
           echo -e "\nDownloading cancelled!"
           exit 1
        fi
      else
        echo -e "\nDownloading cancelled!"
        exit 1
      fi
fi


echo "Start downloading (proxy=$PROXY)..."
echo    "  $URI"
echo    "    => $PREFIX/$FILE"

if [ -z "$PROXY" ]; then
    curl -o "$PREFIX/$FILE" "$URI"
else
    curl -x $PROXY -o "$PREFIX/$FILE" "$URI"
fi

exit 0
