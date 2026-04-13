from __future__ import annotations

from typing import Any, Dict, Iterable, Optional


DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"


def load_hf_dataset(split: str = "train", *, dataset_id: str = DATASET_ID):
    """
    Load the dataset from Hugging Face using the `datasets` library.

    Notes:
    - Hugging Face datasets are cached automatically in the user's HF cache directory.
    - We keep this function thin so later phases can replace the storage approach if needed.
    """
    from datasets import load_dataset  # local import to keep import-time lightweight

    return load_dataset(dataset_id, split=split)


def iter_records(ds) -> Iterable[Dict[str, Any]]:
    """Yield dataset rows as plain Python dicts."""
    for row in ds:
        # `datasets` already yields dict-like rows, but we coerce to dict for safety/serialization
        yield dict(row)


def detect_splits(dataset_id: str = DATASET_ID) -> Dict[str, Any]:
    """
    Return dataset metadata for available splits (best-effort).
    Useful for debugging when the dataset provides non-standard splits.
    """
    from datasets import get_dataset_split_names

    splits = get_dataset_split_names(dataset_id)
    return {"dataset_id": dataset_id, "splits": splits}

