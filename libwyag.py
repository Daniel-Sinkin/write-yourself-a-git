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


def parse_args(argv) -> argparse.Namespace:
    argparser = argparse.ArgumentParser(description="The stupidest content tracker")
    argsubparsers = argparser.add_subparsers(title="Commands", dest="command")
    argsubparsers.required = True
    args = argparser.parse_args(argv)


def get_cmd_map() -> dict[str]:
    cmd_map: dict[str, any] = {
        "add": cmd_add(args),
        "cat-file": cmd_cat_file(args),
        "check-ignore": cmd_check_ignore(args),
        "checkout": cmd_checkout(args),
        "commit": cmd_commit(args),
        "hash-object": cmd_hash_object(args),
        "init": cmd_init(args),
        "log": cmd_log(args),
        "ls-files": cmd_ls_files(args),
        "ls-tree": cmd_ls_tree(args),
        "rev-parse": cmd_rev_parse(args),
        "rm": cmd_rm(args),
        "show-ref": cmd_show_ref(args),
        "status": cmd_status(args),
        "tag": cmd_tag(args),
    }


def main(argv=sys.argv[1:]):
    args = parse_args(sys.argv[1:])
    cmd_map = get_cmd_map()
