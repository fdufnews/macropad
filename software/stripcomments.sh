#!/bin/sh

if [ $# -lt 2 ]; then
    echo "$0 \n    Strips comments from a Python file"
    echo "    usage $0 source dest"
    exit 1
fi
if [ -e $1 ];
then 
  echo "Removing comments from $0 and writing output to $2"; echo;
  sed -e '/^[ \t]*#/d' $1 > $2;
else
  echo $1 does not exist;
fi
