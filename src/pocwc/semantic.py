from __future__ import annotations

import math
import re
from typing import Protocol


class EmbeddingAdapter(Protocol):
    def embed_texts(self, *, texts: list[str]) -> list[list[float]]:
        ...


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Zа-яА-Я0-9]+", text.lower()))


def lexical_jaccard(a: str, b: str) -> float:
    aa = tokenize(a)
    bb = tokenize(b)
    if not aa or not bb:
        return 0.0
    return len(aa.intersection(bb)) / max(1, len(aa.union(bb)))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def semantic_similarity(a: str, b: str, adapter: EmbeddingAdapter | None = None) -> float:
    if not a.strip() or not b.strip():
        return 0.0
    lexical = lexical_jaccard(a, b)
    if adapter is not None:
        try:
            emb = adapter.embed_texts(texts=[a, b])
            if len(emb) == 2:
                emb_sim = cosine_similarity(emb[0], emb[1])
                emb_norm = max(0.0, min(1.0, (emb_sim + 1.0) / 2.0))
                # Keep lexical overlap in the loop to reduce embedding-only false positives.
                return max(0.0, min(1.0, emb_norm * 0.75 + lexical * 0.25))
        except Exception:  # noqa: BLE001
            pass
    return lexical
