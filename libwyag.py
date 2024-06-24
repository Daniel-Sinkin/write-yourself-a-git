import argparse
import sys

from src.commands import get_cmd
from src.git_object import GitBlob
from src.util import parse_args


def main() -> None:
    args: argparse.Namespace = parse_args(sys.argv[1:])
    get_cmd(args.command)(args)


if __name__ == "__main__":
    main()
