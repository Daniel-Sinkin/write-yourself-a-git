import argparse
from typing import Callable, Optional, TypeAlias

from .git_repository import GitRepository


def cmd_init(args: argparse.Namespace) -> None:
    GitRepository.create(args.path)


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
