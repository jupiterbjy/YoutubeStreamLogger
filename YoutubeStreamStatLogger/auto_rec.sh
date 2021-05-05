#!/usr/bin/env sh
mkdir -p ./Logs
./auto_record_data.py 2>&1 | tee -a ./Logs/auto_record.log
