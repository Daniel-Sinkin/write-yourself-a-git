import argparse
import sys

from src.commands import cmd_cat_file, cmd_hash_object, cmd_init, cmd_log
from src.util import parse_args


def main() -> None:
    args: argparse.Namespace = parse_args(sys.argv[1:])

    match args.command:
        case "add":
            raise NotImplementedError
        case "cat-file":
            cmd_cat_file(args)
        case "check-ignore":
            raise NotImplementedError
        case "checkout":
            raise NotImplementedError
        case "commit":
            raise NotImplementedError
        case "hash-object":
            cmd_hash_object(args)
        case "init":
            cmd_init(args)
        case "log":
            cmd_log(args)
        case "ls-files":
            raise NotImplementedError
        case "ls-tree":
            raise NotImplementedError
        case "rev-parse":
            raise NotImplementedError
        case "rm":
            raise NotImplementedError
        case "show-ref":
            raise NotImplementedError
        case "status":
            raise NotImplementedError
        case "tag":
            raise NotImplementedError
        case _:
            raise ValueError(f"{args.command=} is not supported!")


if __name__ == "__main__":
    main()
