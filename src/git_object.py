from __future__ import annotations

import hashlib
import os
import zlib
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional

from .constants import BYTE_CHARS
from .util import kvlm_parse, kvlm_serialize

if TYPE_CHECKING:
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
    def serialize(self) -> bytes: ...

    @abstractmethod
    def deserialize(self): ...

    def init(self): ...

    @property
    @abstractmethod
    def format(self) -> bytes: ...

    @staticmethod
    def read(repo: GitRepository, sha: str) -> Optional[GitObject]:
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

            contents = raw[header_end + 1 :]
            return fmt_to_class_map[file_format](contents)

    @staticmethod
    def write(object, repo: Optional[GitRepository] = None) -> str:
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

    def deserialize(self, data: Optional[bytes]):
        self._blobdata: Optional[bytes] = data


class GitTree(GitObject):
    def __str__(self):
        return super().__str__().replace("GitObject", "GitTree")

    @property
    def format(self) -> bytes:
        return b"tree"

    def serialize(self) -> Optional[bytes]:
        return self._blobdata

    def deserialize(self, data: Optional[bytes]):
        self._blobdata: Optional[bytes] = data


class GitCommit(GitObject):
    def __str__(self):
        return super().__str__().replace("GitObject", "GitCommit")

    @property
    def format(self) -> bytes:
        return b"commit"

    def serialize(self) -> Optional[bytes]:
        return kvlm_serialize(self.kvlm)

    def deserialize(self, data: Optional[bytes]):
        self.kvlm: Optional[OrderedDict] = kvlm_parse(data)

    def init(self):
        self.kvlm = {}


class GitTag(GitObject):
    def __str__(self):
        return super().__str__().replace("GitObject", "GitTag")

    @property
    def format(self) -> bytes:
        return b"tag"

    def serialize(self) -> Optional[bytes]:
        return self._blobdata

    def deserialize(self, data: Optional[bytes]):
        self._blobdata: Optional[str] = data


fmt_to_class_map: dict[bytes, GitObject] = {
    b"commit": GitCommit,
    b"tree": GitTree,
    b"tag": GitTag,
    b"blob": GitBlob,
}
