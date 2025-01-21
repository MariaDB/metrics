#!/usr/bin/env bash

# load common functions
# shellcheck disable=SC1091
. ./bash_lib.sh

if [ "$#" -ne 4 ]; then
  echo "Usage: $0 <GITHUB_PATH> <START_DATE> <END_DATE> <NO_UPDATE>"
  echo "NO_UPDATE should be 0 to update the git trees, any other number to"
  echo "skip the update."
  echo "So for all of 2020 with MariaDB Server do:"
  echo "$0 mariadb/server 2020-01-01 2020-12-31 0"
  exit 1
fi
mkdir -p git_trees
cd git_trees || exit
TREE=$(basename "$1")
# End date is exclusive so need to add one day to it
END_DATE=$(date +%Y-%m-%d -d "$3+1 day")
if [ "$4" -eq 0 ]; then
  if [ -d "$TREE" ]; then
    echo "Updating repo $1"
    cd "$TREE" || exit
    git fetch
    cd ..
  else
    echo "Cloning repo $1"
    git clone https://github.com/"$1" --no-tags
  fi
fi
echo "Extracting git log"
if [ "$TREE" = "server" ]; then
  BRANCHES="--remotes=\"*/10.[0-9]\" --remotes=\"*/10.1[0-9]\" --remotes=\"*/11.[0-9]\" --remotes=\"*/main\""
elif [ "$TREE" = "mariadb-columnstore-engine" ]; then
  BRANCHES="--remotes=\"*/develo?\" --remotes=\"*/develop-1.[0-9]\" --remotes=\"*/develop-[5-9]\"  --remotes=\"*/develop-2[0-9].[0-9][0-9]\""
elif [ "$TREE" = "mariadb-connector-c" ]; then
  BRANCHES="--remotes=\"*/[0-9].[0-9]\""
elif [ "$TREE" = "libmarias3" ]; then
  BRANCHES="origin/master"
else
  BRANCHES="--all"
fi
COMMAND="git --git-dir $TREE/.git log ${BRANCHES} --cherry-pick --numstat -M --since-as-filter=\"$2\" --until=\"$END_DATE\" > git.log"
eval "$COMMAND"
cd ..
echo "Processing git log"
mkdir -p output/"$TREE"
#gitdm/gitdm -c config/mariadb_server/gitdm.config -u -U -n -H output/$TREE/people-$2..$3.csv -E output/$TREE/organisations-$2..$3.csv < git_trees/git.log > output/$TREE/out-$2..$3.txt
gitdm/gitdm -c config/gitdm.config -n -H output/"$TREE"/people-"$2".."$3".csv -E output/"$TREE"/organisations-"$2".."$3".csv -A output/"$TREE"/categories-"$2".."$3".csv <git_trees/git.log >output/"$TREE"/out-"$2".."$3".txt
