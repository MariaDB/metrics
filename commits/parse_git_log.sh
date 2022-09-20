#!/bin/sh

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <GITHUB_PATH> <START_DATE> <END_DATE>"
    echo "So for all of 2020 with MariaDB Server do:"
    echo "$0 mariadb/server 2020-01-01 2020-12-31"
    exit 1
fi
mkdir -p git_trees
cd git_trees
TREE=$(basename $1)
# End date is exclusive so need to add one day to it
END_DATE=$(date +%Y-%m-%d -d "$3+1 day")
if [ -d "$TREE" ]; then
    echo "Updating server repo"
    cd $TREE
    git pull --ff-only
    cd ..
else
    echo "Cloning server repo"
    git clone https://github.com/$1 --no-tags
fi
echo "Extracting git log"
git --git-dir $TREE/.git log --all --numstat -M --since-as-filter="$2" --until="$END_DATE" > git.log
cd ..
echo "Generating category config"
./parse_categories.py
echo "Processing git log"
mkdir -p output/$TREE
#gitdm/gitdm -c config/mariadb_server/gitdm.config -u -U -n -H output/$TREE/people-$2..$3.csv -E output/$TREE/organisations-$2..$3.csv < git_trees/git.log > output/$TREE/out-$2..$3.txt
gitdm/gitdm -c config/mariadb_server/gitdm.config -n -H output/$TREE/people-$2..$3.csv -E output/$TREE/organisations-$2..$3.csv < git_trees/git.log > output/$TREE/out-$2..$3.txt
gitdm/gitdm -c config/mariadb_server_categories/gitdm.config -u -U -n -E output/$TREE/categories-$2..$3.csv < git_trees/git.log > output/$TREE/categories_out-$2..$3.txt
