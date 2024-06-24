from collections import OrderedDict
from typing import Optional

from .constants import BYTE_CHARS


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

    end: int = start
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
