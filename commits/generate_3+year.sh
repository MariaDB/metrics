#!/bin/sh

for REPO in "mariadb/server" "mariadb-corporation/mariadb-columnstore-engine" "mariadb-corporation/libmarias3" "mariadb/mariadb_kernel" "mariadb/mariadb-docker"
do
    TREE=$(basename $REPO)
    for YEARS_AGO in 0 1 2 3
    do
        START_DATE=$(date +%Y-%m-%d -d "`date +%Y-01-01` -$YEARS_AGO years")
        END_DATE=$(date +%Y-%m-%d -d "`date +%Y-12-31` -$YEARS_AGO years")
        YEAR=$(date +%Y -d "`date +%Y-01-01` -$YEARS_AGO years")
        echo "Generating $YEAR for $REPO"
        ./parse_git_log.sh $REPO $START_DATE $END_DATE
        sed -i "1s/\$/,Year/; 2,\$s/\$/,$YEAR/" output/$TREE/people-$START_DATE..$END_DATE.csv
        if [ $YEARS_AGO -eq 0 ]
        then
            cat output/$TREE/people-$START_DATE..$END_DATE.csv > output/$TREE/people.csv
        else
            tail -n +2 output/$TREE/people-$START_DATE..$END_DATE.csv >> output/$TREE/people.csv
        fi
    done
done
