import argparse
from typing import Callable, Optional, TypeAlias

from .git_object import GitBlob, GitCommit, GitObject, GitTag, GitTree
from .git_repository import GitRepository

COMMAND: TypeAlias = Callable[[argparse.Namespace], None]


def cmd_init(args: argparse.Namespace) -> None:
    GitRepository.create(args.path)


def cmd_cat_file(args: argparse.Namespace) -> None:
    repo: open[GitRepository] = GitRepository.find()
    type_ = str(args.type)
    obj_str = str(args.object)
    repo.cat_file(obj_str, fmt=type_.encode())


def object_hash(data: bytes, format: bytes, repo: Optional[GitRepository] = None):
    match format:
        case b"commit":
            return GitObject.write(GitCommit(data), repo)
        case b"tree":
            return GitObject.write(GitTree(data), repo)
        case b"tag":
            return GitObject.write(GitTag(data), repo)
        case b"blob":
            return GitObject.write(GitBlob(data), repo)
        case _:
            raise Exception(f"{format=} is unknown!")


def cmd_hash_object(args: argparse.Namespace) -> None:
    repo: Optional[GitRepository] = GitRepository.find() if args.write else None

    with open(args.path, "rb") as file_data:
        sha = object_hash(file_data.read(), args.type.encode(), repo)
        print(sha)


def cmd_log(args: argparse.Namespace) -> None:
    repo: Optional[GitRepository] = GitRepository.find()

    print("digraph wyaglog{")
    print("  node[shape=rect]")
    repo.log_graphviz(repo.get_file(args.commit), set())
    print("}")
