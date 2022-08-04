from typing import Tuple, List


def is_spoil(message: str, idx: int) -> bool:
    """Returns whether idx of message is within a spoiler text"""
    if idx >= len(message) or idx < 0:
        return False

    # list of tuples of spoil ranges, [start, stop)
    # e.g.: blah blah ||bababababababababab||
    #                   ^start             ^end
    spoil_ranges: List[Tuple[int, int]] = []
    in_spoil = False
    spoil_start = -1
    i = 0
    while i < len(message):
        c = message[i]
        if c == "\\" and not in_spoil:
            # ignore backslashes only for the start of the spoiler
            i += 1
        elif c == "|":
            if i + 1 < len(message) and message[i + 1] == "|":
                if in_spoil:
                    # reached the end of a spoiled section
                    spoil_ranges.append((spoil_start, i))
                else:
                    # start of spoil section
                    spoil_start = i + 2

                i += 1
                in_spoil = not in_spoil

        i += 1

    for start, end in spoil_ranges:
        if start <= idx < end:
            return True
    return False


def maybe_make_link_spoiler(message: str, spoil: bool) -> str:
    """Returns message maybe wrapped in spoiler tags."""
    # Discord will only embed links with spoilers if there is padding
    # between the spoiler tags and the link.
    spoiler_fmt = "|| {} ||" if spoil else "{}"
    return spoiler_fmt.format(message)
