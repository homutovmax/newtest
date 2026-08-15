#!/bin/bash
# Deploy HR project to server 192.168.1.92
# Usage: ./deploy.sh [server] [user]
# Defaults: server=192.168.1.92, user=root

SERVER=${1:-192.168.1.92}
USER=${2:-root}
PROJECT_DIR="/opt/hr"
LOCAL_DIR="$(dirname "$0")"

echo "=== Deploying HR to $SERVER ==="

# 1. Sync all files via rsync (exclude generated + archive + .git)
rsync -avz --delete \
  --exclude='archive/' \
  --exclude='cover_v*.html' \
  --exclude='vacancies_report.html' \
  --exclude='vacancies_history.*' \
  --exclude='vacancies_analytics.html' \
  --exclude='audit_report.md' \
  --exclude='__pycache__/' \
  --exclude='.git/' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache/' \
  "$LOCAL_DIR/" "$USER@$SERVER:$PROJECT_DIR/"

echo "=== Files synced ==="

# 2. Restart web container to pick up changes
ssh "$USER@$SERVER" "cd $PROJECT_DIR && docker compose restart web"
echo "=== Web container restarted ==="

# 3. Run migration for new pipeline_runs table
ssh "$USER@$SERVER" "cd $PROJECT_DIR && docker exec hr-web-1 alembic upgrade head"
echo "=== Migration applied ==="

echo "=== Deploy complete ==="
echo "Report: http://$SERVER:8000/report"
echo "Monitoring: http://$SERVER:8000/monitoring"
