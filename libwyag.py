import argparse
import collections
import configparser
import datetime as dt
import grp
import hashlib
import os
import pwd
import sys
import zlib
from fnmatch import fnmatch
from math import ceil
from typing import Optional


class GitRepository:
    conf = None

    def __init_(self, path: str, force: bool = False):
        self.worktree: str = path
        self.gitdir: str = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"'{path}' is not a Git repo.")

        self.conf = configparser.ConfigParser()
        cf = self.repo_file("config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing!")

        if not force:
            version = int(self.conf.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception(f"Unsupported respoitoryformatversion {version}")

    def repo_path(self, *path) -> str:
        return os.path.join(self.gitdir, *path)

    def repo_file(self, *path, mkdir=False) -> Optional[str]:
        if self.repo_dir(*path[:-1], mkdir=mkdir):
            return self.repo_path(*path)
        else:
            return None

    def repo_dir(self, *path, mkdir=False) -> Optional[str]:
        path: str = self.repo_path(*path)

        if os.path.exists(path):
            if os.path.isdir(path):
                return path
            else:
                raise Exception(f"'{path}' is not a directory")

        if mkdir:
            os.makedirs(path)
            return path
        else:
            return None


def repo_default_config():
    retval = configparser.ConfigParser()

    retval.add_section("core")
    retval.set("core", "repositoryformatversion", "0")
    retval.set("core", "filemode", "false")
    retval.set("core", "bare", "false")

    return retval


def repo_create(path):
    repo = GitRepository(path, True)

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception(f"'{path}' is not a directory")
        elif os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"'{path}' is not empty!")
    else:
        os.makedirs(repo.worktree)

    assert repo.repo_dir("branches", mkdir=True) is not None
    assert repo.repo_dir("objects", mkdir=True) is not None
    assert repo.repo_dir("refs", "tags", mkdir=True) is not None
    assert repo.repo_dir("refs", "heads", mkdir=True) is not None

    with open(repo.repo_file(repo, "description"), "w") as file:
        file.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    with open(repo.repo_file("HEAD"), "w") as file:
        file.write("ref: refs/heads/master\n")

    with open(repo.repo_file("config"), "w") as file:
        repo_default_config().write(file)


def get_cmd_map() -> dict[str]:
    cmd_map: dict[str, any] = {
        "add": cmd_add(args),
        "cat-file": cmd_cat_file(args),
        "check-ignore": cmd_check_ignore(args),
        "checkout": cmd_checkout(args),
        "commit": cmd_commit(args),
        "hash-object": cmd_hash_object(args),
        "init": cmd_init(args),
        "log": cmd_log(args),
        "ls-files": cmd_ls_files(args),
        "ls-tree": cmd_ls_tree(args),
        "rev-parse": cmd_rev_parse(args),
        "rm": cmd_rm(args),
        "show-ref": cmd_show_ref(args),
        "status": cmd_status(args),
        "tag": cmd_tag(args),
    }


def parse_args(argv) -> argparse.Namespace:
    argparser = argparse.ArgumentParser(description="The stupidest content tracker")
    argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
    argsubparsers.required = True
    args = argparser.parse_args(argv)


def main(argv=sys.argv[1:]):
    args = parse_args(sys.argv[1:])
    cmd_map = get_cmd_map()
