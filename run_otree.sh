#/bin/sh

# export OTREE_AUTH_LEVEL=STUDY
export OTREE_PRODUCTION=1
# export OTREE_ADMIN_PASSWORD=otreeadmin123
# export OTREE_SESSIONS=MAIN
# export DATABASE_URL="postgres://postgres:password@localhost/django_db"

otree "$@"