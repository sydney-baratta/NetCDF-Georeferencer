#!/bin/bash
DEBUG=""

# Check for -d debug flag
if [[ "$1" == "-d" ]]; then
    DEBUG="-d"
    shift  # Shift arguments so that IN_FILE is now $1
fi

IN_FILE=$1 # Inbound .nc file
OUT_DIR=$2 # Outbound directory for .tif files
BANDS=$3 # 5 bit binary code for band selection. Bands high to low correlate to MSB.
python georefing.py $DEBUG $IN_FILE $OUT_DIR $BANDS