#!/bin/bash
# HR Pipeline cron job (10:00 MSK)
LOG=/var/log/hr-pipeline.log
echo "=== $(date) ===" >> $LOG
cd /opt/hr

# Full pipeline: scrape -> merge -> covers -> report -> analytics -> email -> PG migration
docker exec hr-web-1 sh -c "python -m src.pipeline && python -m src.migration" >> $LOG 2>&1
STATUS=$?
echo "pipeline+migration: exit $STATUS" >> $LOG
echo "=== done $(date) ===" >> $LOG
