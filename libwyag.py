import argparse
import sys

from src.commands import get_cmd
from src.git_object import GitBlob
from src.git_repository import GitRepository
from src.util import parse_args


def main() -> None:
    args: argparse.Namespace = parse_args(sys.argv[1:])
    get_cmd(args.command)(args)


if __name__ == "__main__":
    repo = GitRepository("./test", force=True)

    gb = GitBlob(b"AyoByo!")
    print(gb.write(repo))

    print(gb.read(repo, gb.write(repo)))
