#!/bin/sh

for YEARS_AGO in 0 1 2 3
do
    START_DATE=$(date +%Y-%m-%d -d "`date +%Y-01-01` -$YEARS_AGO years")
    END_DATE=$(date +%Y-%m-%d -d "`date +%Y-12-31` -$YEARS_AGO years")
    YEAR=$(date +%Y -d "`date +%Y-01-01` -$YEARS_AGO years")
    echo "Generating $YEAR"
    ./get_git_log.sh $START_DATE $END_DATE
    sed -i "1s/\$/,Year/; 2,\$s/\$/,$YEAR/" people-$START_DATE..$END_DATE.csv
    if [ $YEARS_AGO -eq 0 ]
    then
        cat people-$START_DATE..$END_DATE.csv > people.csv
    else
        tail -n +2 people-$START_DATE..$END_DATE.csv >> people.csv
    fi
done
