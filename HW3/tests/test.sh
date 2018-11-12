#!/bin/sh

HOST='localhost'
PORT='2123'
USER='josephmulray'
PASSWD='root'
FILE='file.txt'
RETRFILE='Makefile' #just grab the makefile as an example
STORFILE='storfile'

ftp -n $HOST $PORT <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
ls
passive on
ls
epsv4
ls
pwd
cdup
pwd
passive off
cd HW3
ls
quote get $RETRFILE
system
quote send $STORFILE
quit
END_SCRIPT
exit 0
