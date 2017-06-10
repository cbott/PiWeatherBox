#!/bin/bash
#This file runs on startup
#Add to /etc/rc.local
## cd /path/to/this/file
## ./run.sh

LOGFILE=log.txt
exitcode=1

while [ $exitcode -ne 0 ]
do
echo -e "\n[`date`] Starting Python Script" >> $LOGFILE
python3 piweatherbox.py &>> $LOGFILE
exitcode=$?
echo "[`date`] Python Script Exited With Code $exitcode" >> $LOGFILE

# Restart program if it exits with nonzero exit code
if [ $exitcode -ne 0 ]; then
  echo "Bad exit condition. Attempting program restart in 10 seconds..." >> $LOGFILE
  sleep 10
fi
done
echo -e "Program exited normally -- Finished\n" >> $LOGFILE
