#!/bin/bash
#This file runs on startup
#Add to /etc/rc.local
## cd /path/to/this/file
## ./run.sh

LOGFILE=log.txt

echo -e "\n\n[`date`] Starting Python Script" >> $LOGFILE
python piweatherbox.py &>> $LOGFILE
exitcode=$?
echo "[`date`] Python Script Exited With Code $exitcode" >> $LOGFILE

# Perhaps add something to restart the program if it crashed
#if [ $exitcode -eq 0 ]; then
#echo -e "Complete\n" >> $LOGFILE
#else
#echo "Bad exit condition. Attempting program restart..." >> $LOGFILE
#fi
