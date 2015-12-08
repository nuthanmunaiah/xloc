#!/bin/bash

usage=$(cat <<EOS
USAGE: $0 file

Arguments

  file : Path to a CSV file to export the SLOC to.
EOS
)

if [ $# -lt 1 ]; then
    echo "$usage"
    exit 1
fi

file=$1

if [ ! -f db.sqlite3 ]; then
    echo "ERROR: No database to export from."
    exit 1
fi

count=$(sqlite3 -csv -noheader db.sqlite3 \
    "SELECT COUNT(*) FROM app_function" 2> /dev/null)

if [ $count -eq 0 ]; then
    echo "Nothing to export. Database is empty."
    exit 0
else
    sqlite3 -csv -noheader db.sqlite3 \
        "SELECT file, name, sloc FROM app_function" 1> $file 2> /dev/null
    echo "SLOC exported to $file"
    exit 0
fi
