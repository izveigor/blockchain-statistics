#!bin/sh
if [ ! -f db.sqlite3 ]; then
    python3 manage.py migrate
    # You can download blocks from 0 to 10
    # python3 manage.py download_blocks [0 to 10]
fi
exec "$@"