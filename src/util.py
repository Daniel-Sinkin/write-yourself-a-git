import argparse
import sys


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
