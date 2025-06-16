#!/bin/sh

if [ "$#" -eq 0 ]; then
    TASK_NAME="iowa_gambling_task"
else
    TASK_NAME=$1
fi

# export OTREE_AUTH_LEVEL=STUDY
export OTREE_PRODUCTION=1
# export OTREE_ADMIN_PASSWORD=otreeadmin123
# export OTREE_SESSIONS=MAIN
# export DATABASE_URL="postgres://postgres:password@localhost/django_db"


./run_otree.sh prodserver 8000 &
./run_otree.sh prodserver 8001 & # For static files (for multi-modal only)
otree browser_bots $TASK_NAME &
