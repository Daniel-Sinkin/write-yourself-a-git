import argparse
from argparse import ArgumentParser
from typing import TypeAlias, cast

SUBPARSER: TypeAlias = argparse._SubParsersAction


def _parse_args_cat_file(argsubparsers: SUBPARSER) -> None:
    argsp = cast(
        ArgumentParser,
        argsubparsers.add_parser(
            "cat-file", help="Provide content of repository objects"
        ),
    )

    argsp.add_argument(
        "type",
        metavar="type",
        choices=["blob", "commit", "tag", "tree"],
        help="Specify the type",
    )

    argsp.add_argument("object", metavar="object", help="The object to display")


def _parse_args_init(argsubparsers: SUBPARSER) -> None:
    argsp = cast(
        ArgumentParser,
        argsubparsers.add_parser("init", help="Initialize a new, empty repository."),
    )

    argsp.add_argument(
        "path",
        metavar="directory",
        nargs="?",
        default=".",
        help="Where to create the repository.",
    )


def _parse_args_hash_object(argsubparsers: SUBPARSER) -> None:
    argsp = cast(
        ArgumentParser,
        argsubparsers.add_parser(
            "hash-object",
            help="Compute object ID and optionally creates a blob from a file",
        ),
    )

    argsp.add_argument(
        "-t",
        metavar="type",
        dest="type",
        choices=["blob", "commit", "tag", "tree"],
        default="blob",
        help="Specify the type",
    )

    argsp.add_argument(
        "-w",
        dest="write",
        action="store_true",
        help="Actually write the object into the database",
    )

    argsp.add_argument("path", help="Read object from <file>")


def _parse_args_commit(argsubparsers: SUBPARSER) -> None:
    argsp: ArgumentParser = cast(
        ArgumentParser,
        argsubparsers.add_parser("log", help="Display history of a given commit."),
    )
    argsp.add_argument("commit", default="HEAD", nargs="?", help="Commit to start at.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    argparser = ArgumentParser(description="Scuffed Git")
    argsubparsers: SUBPARSER = argparser.add_subparsers(
        title="Commands", dest="command"
    )
    argsubparsers.required = True

    _parse_args_init(argsubparsers)
    _parse_args_cat_file(argsubparsers)
    _parse_args_hash_object(argsubparsers)

    _parse_args_commit(argsubparsers)

    return argparser.parse_args(argv)
