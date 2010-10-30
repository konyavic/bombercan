#!/bin/sh

log="dll.log"

ldd $1 | grep "E:" | sed -ne 's/\\/\\\\/gp' > $log

awk '{system("cp "$3" .")}' $log
