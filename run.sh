#!/bin/bash

LOGFILE=log.txt

echo "\n\n[`date`] Starting Python Script" >> $LOGFILE
python piweatherbox.py &>> $LOGFILE
exitcode=$?
echo "[`date`] Python Script Exited With Code $exitcode" >> $LOGFILE

if [ $exitcode -eq 0 ]; then
echo "Exited Normally"
else
echo "Bad Exit Condition"
fi
