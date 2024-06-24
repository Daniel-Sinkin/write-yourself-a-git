import argparse
from argparse import ArgumentParser
from collections import OrderedDict
from typing import Optional, TypeAlias, cast

from .constants import BYTE_CHARS

SUBPARSER: TypeAlias = argparse._SubParsersAction


def _parse_args_cat_file(argsubparsers: SUBPARSER):
    argsp = argsubparsers.add_parser(
        "cat-file", help="Provide content of repository objects"
    )

    argsp.add_argument(
        "type",
        metavar="type",
        choices=["blob", "commit", "tag", "tree"],
        help="Specify the type",
    )

    argsp.add_argument("object", metavar="object", help="The object to display")


def _parse_args_init(argsubparsers: SUBPARSER):
    argsp: ArgumentParser = argsubparsers.add_parser(
        "init", help="Initialize a new, empty repository."
    )

    argsp.add_argument(
        "path",
        metavar="directory",
        nargs="?",
        default=".",
        help="Where to create the repository.",
    )


def _parse_args_hash_object(argsubparsers: SUBPARSER):
    argsp = argsubparsers.add_parser(
        "hash-object",
        help="Compute object ID and optionally creates a blob from a file",
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


def _parse_args_commit(argsubparsers: SUBPARSER):
    argsp: ArgumentParser = argsubparsers.add_parser(
        "log", help="Display history of a given commit."
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


# KVLM = Key-Value List with Message, as per https://wyag.thb.lt/#orgc8b86d2
def kvlm_parse(raw: bytes, start: int = 0, dict_: Optional[OrderedDict] = None):
    if dict_ is None:
        dict_ = OrderedDict()

    space_idx: int = raw.find(BYTE_CHARS.WHITESPACE, start)
    newline_idx: int = raw.find(BYTE_CHARS.NEWLINE, start)

    if space_idx < 0 or newline_idx < space_idx:
        assert newline_idx == start
        dict_[None] = raw[start + 1 :]
        return dict_

    key: bytes = raw[start:space_idx]

    end = start
    while True:
        end = raw.find(BYTE_CHARS.NEWLINE, end + 1)
        # TODO: CHeck if we could instead check for b" "
        if raw[end + 1] != ord(" "):
            break

    value: bytes = raw[space_idx + 1 : end].replace(
        BYTE_CHARS.NEWLINE + BYTE_CHARS.WHITESPACE, BYTE_CHARS.NEWLINE
    )

    if key in dict_:
        if isinstance(dict_[key], list):
            dict_[key].append(value)
        else:
            dict_[key] = [dict_[key], value]
    else:
        dict_[key] = value

    return kvlm_parse(raw, start=end + 1, dict_=dict_)


def kvlm_serialize(kvlm) -> bytes:
    retval: bytes = b""

    for k in kvlm:
        if k is None:
            continue
        val = kvlm[k]
        if not isinstance(val, list):
            val = [val]

        for v in val:
            retval += (
                k
                + BYTE_CHARS.WHITESPACE
                + v.replace(
                    BYTE_CHARS.NEWLINE, BYTE_CHARS.NEWLINE + BYTE_CHARS.WHITESPACE
                )
                + BYTE_CHARS.NEWLINE
            )

    retval += BYTE_CHARS.NEWLINE + kvlm[None] + BYTE_CHARS.NEWLINE
    return retval
