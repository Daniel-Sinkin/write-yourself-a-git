from __future__ import annotations

import configparser
import os
import sys
from pathlib import Path
from typing import Optional

from .git_object import GitObject


class GitRepository:
    def __init__(self, path: str, force: bool = False):
        self.worktree: str = path
        self.gitdir: str = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(f"'{path}' is not a Git repo.")

        self.conf = configparser.ConfigParser()
        cf: Optional[str] = self.get_file("config")
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

    def get_path(self, *path: str | list[str]) -> str:
        return os.path.join(self.gitdir, *path)

    def get_file(self, *path: str | list[str], mkdir: bool = False) -> Optional[str]:
        if self.get_dir(*path[:-1], mkdir=mkdir):
            return self.get_path(*path)
        else:
            return None

    def get_dir(self, *path: str | list[str], mkdir: bool = False) -> Optional[str]:
        path: str = self.get_path(*path)

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

    @staticmethod
    def get_default_config():
        retval = configparser.ConfigParser()

        retval.add_section("core")
        retval.set("core", "repositoryformatversion", "0")
        retval.set("core", "filemode", "false")
        retval.set("core", "bare", "false")

        return retval

    @staticmethod
    def create(path: str):
        repo = GitRepository(path, True)

        if os.path.exists(repo.worktree):
            if not os.path.isdir(repo.worktree):
                raise Exception(f"'{path}' is not a directory")
            elif os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
                raise Exception(f"'{path}' is not empty!")
        else:
            os.makedirs(repo.worktree)

        assert repo.get_dir("branches", mkdir=True) is not None
        assert repo.get_dir("objects", mkdir=True) is not None
        assert repo.get_dir("refs", "tags", mkdir=True) is not None
        assert repo.get_dir("refs", "heads", mkdir=True) is not None

        with open(repo.get_file("description"), "w") as file:
            file.write(
                "Unnamed repository; edit this file 'description' to name the repository.\n"
            )

        with open(repo.get_file("HEAD"), "w") as file:
            file.write("ref: refs/heads/master\n")

        with open(repo.get_file("config"), "w") as file:
            GitRepository.get_default_config().write(file)

    @staticmethod
    def find(path: str = ".", required: bool = True) -> Optional[GitRepository]:
        # Turns relative into absolute path
        path: Path = Path(path).resolve()

        # Checks if there is a `.git` directory in path
        if (path / ".git").is_dir():
            return GitRepository(path)

        parent: Path = path.parent
        if parent == path:
            # Base case, the path is a (the?) root
            if required:
                raise Exception("No git directory")
            else:
                return None

        return GitRepository.find(parent, required)

    def cat_file(self, object: str, fmt: Optional[bytes] = None) -> None:
        object = GitObject.read(self, self.find_object(object, fmt=fmt))
        sys.stdout.buffer.write(object.serialize())

    def find_object(
        self, name: str, fmt: Optional[bytes] = None, follow: bool = True
    ) -> None:
        return name
