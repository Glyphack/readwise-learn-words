from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import os
import json


@dataclass
class Tag:
    id: int
    name: str

    @staticmethod
    def from_dict(d: dict) -> "Tag":
        return Tag(id=d["id"], name=d["name"])


@dataclass
class Highlight:
    id: int
    is_deleted: bool
    text: str
    location: int
    location_type: str
    note: str
    color: str
    highlighted_at: str
    created_at: str
    updated_at: str
    external_id: Optional[str]
    end_location: int
    url: Optional[str]
    book_id: int
    tags: List[Tag]
    is_favorite: bool
    is_discard: bool
    readwise_url: str

    @staticmethod
    def from_dict(d: dict) -> "Highlight":
        return Highlight(
            id=d["id"],
            is_deleted=d["is_deleted"],
            text=d["text"],
            location=d["location"],
            location_type=d["location_type"],
            note=d["note"],
            color=d["color"],
            highlighted_at=d["highlighted_at"],
            created_at=d["created_at"],
            updated_at=d["updated_at"],
            external_id=d.get("external_id"),
            end_location=d["end_location"],
            url=d.get("url"),
            book_id=d["book_id"],
            tags=[Tag.from_dict(t) for t in d.get("tags", [])],
            is_favorite=d["is_favorite"],
            is_discard=d["is_discard"],
            readwise_url=d["readwise_url"],
        )


@dataclass
class WordEntry:
    text: str
    note: str


@dataclass
class HighlightWithMeaning:
    highlight: Highlight
    meaning: str


@dataclass
class SyncedData:
    words: dict[str, str]
    last_synced_at: Optional[str] = None

    @staticmethod
    def load(path: str) -> "SyncedData":
        if not os.path.exists(path):
            return SyncedData(words={}, last_synced_at=None)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return SyncedData(
                words=data.get("words", {}), last_synced_at=data.get("last_synced_at")
            )
        except (json.JSONDecodeError, IOError):
            return SyncedData(words={}, last_synced_at=None)

    def save(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"words": self.words, "last_synced_at": self.last_synced_at},
                f,
                ensure_ascii=False,
                indent=2,
            )
