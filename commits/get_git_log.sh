#!/bin/sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <START_DATE> <END_DATE>"
    echo "So for all of 2020 do:"
    echo "$0 2020-01-01 2020-12-31"
    exit 1
fi
# End date is exclusive so need to add one day to it
END_DATE=$(date +%Y-%m-%d -d "$2+1 day")
if [ -d "server" ]; then
    echo "Updating server repo"
    cd server
    git pull --ff-only
    cd ..
else
    echo "Cloning server repo"
    git clone https://github.com/mariadb/server --no-tags
fi
echo "Extracting git log"
git --git-dir server/.git log --all --numstat -M --since-as-filter="$1" --until="$END_DATE" > git.log
echo "Generating category config"
./parse_categories.py
echo "Processing git log"
gitdm/gitdm -c gitdm_config/gitdm.config -u -U -n -H people-$1..$2.csv -E employers-$1..$2.csv < git.log > out-$1..$2.txt
gitdm/gitdm -c gitdm_config_categories/gitdm.config -u -U -n -E catgegories-$1..$2.csv < git.log > categories_out-$1..$2.txt
echo "Cleaning up"
rm git.log
