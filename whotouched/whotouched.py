#!/usr/bin/python3
from git import Git
from file_parser import FileParser
import csv
from dataclasses import dataclass
from operator import getitem
import yaml
from glob import glob
import argparse
from datetime import datetime
from pathlib import Path

git_path = None
verbose = False
date = None
outdir = None

def get_from_dirs(paths):
    git = Git(git_path)
    if date:
        git.set_date(date)
    output = git.get_authors_from_paths(paths)
    return output

def summarise(commits):
    authors = {}
    commit_ids = []
    for commit in commits:
        # De-duplicate as we may be combining lists
        if commit.commit_id in commit_ids:
            continue
        commit_ids.append(commit.commit_id)
        for author in commit.authors:
            if author.email in authors:
                old = authors[author.email]
                old["count"] += 1
                authors[author.email] = old
            else:
                authors[author.email] = {"name": author.name, "count": 1}
    authors = dict(sorted(authors.items(), key=lambda item: getitem(item[1], 'count'), reverse=True))
    return authors

def output_csv(name, authors):
    with open(outdir + "/" + name + '.csv', 'w') as f:
        w = csv.writer(f, quoting = csv.QUOTE_NONNUMERIC)
        w.writerow(["Email", "Name", "Count"])
        for key, value in authors.items():
            w.writerow([key, value["name"], value["count"]])
    if verbose:
        print("{}.csv written".format(name))


def find_files_postfix(postfix):
    return glob("**/" + postfix, root_dir=git_path, recursive=True)


def get_commits_for_areas(define, paths_in):
    git = Git(git_path)
    if date:
        git.set_date(date)
    commit_ids = []
    fp = FileParser()
    # Trim files that aren't relevant
    paths = []
    for path in paths_in:
        try:
            file = git.get_file_from_commit(git.get_head_commit_id(), path)
            fp.buffer(file)
            found = fp.define_exists(define)
            if found:
                paths.append(path)
        except:
            continue

    for path in paths:
        if verbose:
            print("Looking into {}".format(path))
        # Second param is an optimisation to skip things we have already included
        lines = git.get_commit_lines_for_file(path, commit_ids)


        commit = None
        found = False
        positions = []
        for line in lines:
            if commit != line["commit"]:
                if found:
                    found = False
                    commit_ids.append(commit)
                commit = line["commit"]
                try:
                    file = git.get_file_from_commit(commit, path)
                except:
                    # File not in commit
                    break
                fp.buffer(file)
                positions = fp.find_define("_WIN32")

            if found:
                continue
            for position in positions:
                # Deletion
                if line["new_lineno"] == -1 and line["old_lineno"] > position["start"] and line["old_lineno"] < position["end"]:
                    found = True
                    break
                # Addition
                else:
                    git_line_end = line["new_lineno"] + line["num_lines"]
                    if max(line["new_lineno"], position["start"]) <= min(git_line_end, position["end"]):
                        found = True
                        break

    ret = []
    for commit_id in set(commit_ids):
        ret.append(git.get_commit_from_id(commit_id))

    return ret


def generate():
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    for key, value in config.items():
        if verbose:
            print("Processing {}".format(key))
        commits = []
        if "paths" in value:
            commits = get_from_dirs(value["paths"])
        if "files_postfix" in value:
            paths = []
            for postfix in value["files_postfix"]:
                paths += find_files_postfix(postfix)
            commits = get_from_dirs(paths)
        if "define" in value:
            paths = []
            for postfix in value["file_types"]:
                paths += find_files_postfix("*." + postfix)
            commits = get_commits_for_areas(value["define"], paths)
        authors = summarise(commits)
        output_csv(key, authors)

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='whotouched',
            description='Works out who touched certain area of the codebase')
    parser.add_argument('git_path', help='The path to the git checkout')
    parser.add_argument('-v', '--verbose', action=argparse.BooleanOptionalAction)
    parser.add_argument('-d', '--date', help='Oldest date to scan in the git treein YYYY-MM-DD format', type=valid_date)
    parser.add_argument('-o', '--output', help='Output directory', default="output")
    args = parser.parse_args()
    git_path = args.git_path;
    verbose = args.verbose
    date = args.date
    outdir = args.output
    Path(outdir).mkdir(parents=True, exist_ok=True)
    generate()
