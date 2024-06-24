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
from pathlib import Path
from typing import Callable, Optional, TypeAlias


class GitRepository:
    def __init__(self, path: str, force: bool = False):
        self.worktree: str = path
        self.gitdir: str = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"'{path}' is not a Git repo.")

        self.conf = configparser.ConfigParser()
        cf: Optional[str] = self.repo_file("config")
        if cf is not None and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing!")

        if not force:
            version = int(self.conf.get("core", "repositoryformatversion"))
            if version != 0:
                raise Exception(f"Unsupported respoitoryformatversion {version}")

    def __repr__(self):
        return f"GitRepository(path='{self.worktree}')"

    def __str__(self):
        return self.__repr__()

    def repo_path(self, *path: str | list[str]) -> str:
        return os.path.join(self.gitdir, *path)

    def repo_file(self, *path: str | list[str], mkdir: bool = False) -> Optional[str]:
        if self.repo_dir(*path[:-1], mkdir=mkdir):
            return self.repo_path(*path)
        else:
            return None

    def repo_dir(self, *path: str | list[str], mkdir: bool = False) -> Optional[str]:
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


def repo_create(path: str):
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

    with open(repo.repo_file("description"), "w") as file:
        file.write(
            "Unnamed repository; edit this file 'description' to name the repository.\n"
        )

    with open(repo.repo_file("HEAD"), "w") as file:
        file.write("ref: refs/heads/master\n")

    with open(repo.repo_file("config"), "w") as file:
        repo_default_config().write(file)


def cmd_init(args: argparse.Namespace) -> None:
    repo_create(args.path)


def repo_find(path: str = ".", required: bool = True):
    # Turns relative into absolute path
    path = Path(path).resolve()

    # Checks if there is a `.git` directory in path
    if (path / ".git").is_dir():
        return GitRepository(path)

    parent = path.parent
    if parent == path:
        # Base case, the path is a (the?) root
        if required:
            raise Exception("No git directory")
        else:
            return None

    return repo_find(parent, required)


# fmt: off
COMMAND: TypeAlias = Callable[[argparse.Namespace], None]
def get_cmd(key: Optional[str] = None) -> dict[str, COMMAND] | COMMAND:
    cmd_map: dict[str, COMMAND] = {
        "add": lambda: None,
        "cat-file": lambda: None,
        "check-ignore": lambda: None,
        "checkout": lambda: None,
        "commit": lambda: None,
        "hash-object": lambda: None,
        "init": cmd_init,
        "log": lambda: None,
        "ls-files": lambda: None,
        "ls-tree": lambda: None,
        "rev-parse": lambda: None,
        "rm": lambda: None,
        "show-ref": lambda: None,
        "status": lambda: None,
        "tag": lambda: None,
    }
    if key is None:
        return cmd_map
    else:
        return cmd_map[key]
# fmt: on


def parse_args(argv) -> argparse.Namespace:
    argparser = argparse.ArgumentParser(description="The stupidest content tracker")
    argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
    argsubparsers.required = True

    argsp: argparse.ArgumentParser = argsubparsers.add_parser(
        "init", help="Initialize a new, empty repository."
    )

    argsp.add_argument(
        "path",
        metavar="directory",
        nargs="?",
        default=".",
        help="Where to create the repository.",
    )

    return argparser.parse_args(argv)


def main():
    args = parse_args(sys.argv[1:])
    get_cmd(args.command)(args)


if __name__ == "__main__":
    print(repo_find("./a/b"))
    # main()
