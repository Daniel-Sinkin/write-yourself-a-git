from __future__ import annotations

import hashlib
import os
import zlib
from abc import ABC, abstractmethod
from typing import Optional

from .constants import BYTE_CHARS
from .git_repository import GitRepository


class GitObject(ABC):
    def __init__(self, data: Optional[bytes] = None):
        if data is not None:
            if not isinstance(data, bytes):
                raise TypeError(f"Only bytedata is supported, not {type(data)}.")
            self.deserialize(data)
        else:
            self.init()

    def __str__(self):
        return f'GitObject("{self.serialize()}")'

    @abstractmethod
    def serialize(repo) -> bytes: ...

    @abstractmethod
    def deserialize(repo): ...

    def init(self): ...

    @property
    @abstractmethod
    def format(self) -> bytes: ...

    @staticmethod
    def read(repo: GitRepository, sha) -> Optional[GitObject]:
        path: Optional[str] = repo.get_file("objects", sha[0:2], sha[2:])

        if path is None or not os.path.isfile(path):
            return None

        with open(path, "rb") as file:
            raw: bytes = zlib.decompress(file.read())

            header_type_size_seperator = raw.find(b" ")
            file_format: bytes = raw[0:header_type_size_seperator]

            header_end: int = raw.find(b"\x00", header_type_size_seperator)
            size = int(raw[header_type_size_seperator:header_end].decode("ascii"))
            if size != len(raw) - header_end - 1:
                raise Exception(f"Malformed object {sha}: bad length")

            match file_format:
                case b"commit":
                    object_type = GitCommit
                case b"tree":
                    object_type = GitTree
                case b"tag":
                    object_type = GitTag
                case b"blob":
                    object_type = GitBlob
                case _:
                    raise Exception(
                        f"Malformed object {sha}: Unknown type {file_format.decode('ascii')}"
                    )

            contents = raw[header_end + 1 :]
            return object_type(contents)

    def write(object: GitObject, repo: Optional[GitRepository] = None) -> str:
        data: bytes = object.serialize()

        result: bytes = (
            object.format
            + BYTE_CHARS.WHITESPACE
            + str(len(data)).encode()
            + BYTE_CHARS.HEADER_SEPERATOR
            + data
        )

        sha: str = hashlib.sha1(result).hexdigest()

        if repo is not None:
            path: Optional[str] = repo.get_file(
                "objects", sha[0:2], sha[2:], mkdir=True
            )

            if path is None or not os.path.exists(path):
                with open(path, "wb") as file:
                    file.write(zlib.compress(result))

        return sha


class GitBlob(GitObject):
    def __str__(self):
        return super().__str__().replace("GitObject", "GitBlob")

    @property
    def format(self) -> bytes:
        return b"blob"

    def serialize(self) -> Optional[bytes]:
        return self._blobdata

    def deserialize(self, data: Optional[str]):
        self._blobdata: Optional[str] = data
