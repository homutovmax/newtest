#!/bin/bash
# Send report email (no re-scrape) — 14:00 MSK
LOG=/var/log/hr-pipeline.log
echo "=== $(date) sending report ===" >> $LOG
cd /opt/hr
docker exec hr-web-1 python /app/src/send_report.py >> $LOG 2>&1
echo "=== done ===" >> $LOG
