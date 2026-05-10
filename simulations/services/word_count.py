from __future__ import annotations

import re

WORD_RE = re.compile(r"[^\W_]+(?:['-][^\W_]+)*", re.UNICODE)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text or ""))
