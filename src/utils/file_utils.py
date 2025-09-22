import csv
import os
import tempfile
from collections.abc import Iterable, Sequence


def atomic_write_csv(path: str, rows: Iterable[Sequence[str]], header: Sequence[str]) -> None:
    """Write CSV atomically: write to temp file, then rename."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dir_name = os.path.dirname(path) or "."
    with tempfile.NamedTemporaryFile(
        "w",
        delete=False,
        dir=dir_name,
        newline="",
        encoding="utf-8",
    ) as tmp:
        writer = csv.writer(tmp)
        writer.writerow(header)
        writer.writerows(rows)
        tmp_name = tmp.name
    os.replace(tmp_name, path)
