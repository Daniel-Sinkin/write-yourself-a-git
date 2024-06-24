from dataclasses import dataclass


@dataclass
class BYTE_CHARS:
    WHITESPACE = b" "
    HEADER_SEPERATOR = b"\x00"
    NEWLINE = b"\n"
