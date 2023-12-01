import pygit2 as git
import re
from collections import deque
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Author:
    email: str
    name: str

@dataclass
class CommitData:
    commit_id: str
    authors: list[Author]


class Git:
    __repo = None
    __date = 0
    __cache = {}

    def __init__(self, path):
        self.__repo = git.Repository(path)

    def set_date(self, date):
        __date = datetime.timestamp(date)

    def __cache_lookup(self, sha):
        if sha not in self.__cache:
            self.__cache[sha] = self.__repo[sha]

        return self.__cache[sha]

    def __get_path_oid_from_commit(self, commit, path):
        obj = commit.tree
        for name in path.split('/'):
            if obj.type != git.GIT_OBJ_TREE:
                return None

            if name not in obj:
                return None
            entry = obj[name]
            obj = self.__cache_lookup(entry.oid)
        return obj

    def __get_commit_from_paths(self, paths):
        last = self.__repo[self.__repo.head.target]
        for commit in self.__repo.walk(last.id, git.GIT_SORT_NONE):
            # Skip merge commits
            if len(commit.parents) > 1:
                continue
            # Skip old commits
            if commit.commit_time < self.__date:
                continue
            if commit.parents:
                parent = commit.parents[0]
            else:
                parent = None

            for path in paths:
                try:
                    a = self.__get_path_oid_from_commit(commit, path)
                    if parent is None:
                        # If first commit in tree and that contains a change for path
                        if a:
                            yield commit
                    else:
                        b = self.__get_path_oid_from_commit(parent, path)
                        # If the file changed between parent and now
                        if a is not b:
                            yield commit
                except:
                    # Invalid path, probably from a submodule
                    continue

    def __get_coauthors(self, commit):
        ret = []
        co_authors = re.findall("Co-authored-by: (.*)", commit.message)
        for ca in co_authors:
            user = re.findall("(.*) <(.*)>", ca)
            item = {"name": user[0][0], "email": user[0][1]}
            ret.append(item)
        return ret

    def get_authors_from_paths(self, paths):
        ret = []
        for commit in self.__get_commit_from_paths(paths):
            authors = []
            authors.append(Author(commit.author.email, commit.author.name))
            cas = self.__get_coauthors(commit)
            for ca in cas:
                authors.append(Author(ca["email"], ca["name"]))
            ret.append(CommitData(commit.oid, authors))
        return ret

    def get_commit_from_id(self, commit_id):
        commit = self.__repo[commit_id]
        authors = []
        authors.append(Author(commit.author.email, commit.author.name))
        cas = self.__get_coauthors(commit)
        for ca in cas:
            authors.append(Author(ca["email"], ca["name"]))
        return CommitData(commit_id, authors)

# This has no utility right now, keeping it because it was a pain to write and
# will be a pain to figure out again
#
#    def __get_blame(self, file):
#        commits = deque([self.__repo.head.target])
#        cache = []
#        ret = []
#
#        while len(commits) > 0:
#            commit = commits.pop()
#            print (commit)
#            try:
#                hunks = self.__repo.blame(file, newest_commit=commit, flags=git.GIT_BLAME_FIRST_PARENT)
#            except:
#                # File does not exist in this timeline
#                continue
#
#            for hunk in hunks:
#                ret.append({"commit_id": hunk.final_commit_id, "start": hunk.orig_start_line_number, "lines": hunk.lines_in_hunk})
#                next_commit_id = self.__repo[hunk.final_commit_id].parents[0].oid
#                if next_commit_id != commit:
#                    if next_commit_id not in cache:
#                        cache.append(next_commit_id)
#                        commits.append(next_commit_id)
#
#        return ret

    def __get_diff(self, commit1, commit2):
        diff = self.__repo.diff(commit1, commit2, context_lines=0)
        return diff.deltas


    def get_commit_lines_for_file(self, file, skip_ids):
        ret = []
        # Clear the cache or it grows into 10s of GB
        self.__cache = {}
        for commit in self.__get_commit_from_paths([file]):
            if commit.oid in skip_ids:
                continue
            try:
                parent = self.__repo[commit.oid].parents[0].oid
            except:
                # TODO: no parent means initial commit
                continue
            diff = self.__repo.diff(parent, commit, context_lines=0)
            for obj in diff:
                if type(obj) == git.Patch and obj.delta.new_file.path == file:
                    for hunk in obj.hunks:
                        for line in hunk.lines:
                            ret.append({"commit": commit.oid, "parent": parent, "old_lineno": line.old_lineno, "new_lineno": line.new_lineno, "num_lines": line.num_lines})
        return ret

    def get_head_commit_id(self):
        return self.__repo.head.target


    def get_file_from_commit(self, commit_id, file):
        obj = self.__repo[commit_id].tree / file
        view = memoryview(obj)
        # A few files have had dodgy characters in
        return str(view, 'utf8', errors='replace')
