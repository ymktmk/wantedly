from __future__ import annotations

import csv
import os
from typing import Dict, Generator, Iterable, List, Optional, Sequence, Union


def detect_encoding(file_path: str, candidate_encodings: Optional[Sequence[str]] = None) -> str:
    """Detect a likely encoding by trial reading small chunk.

    Returns the first encoding that can read a small sample without UnicodeDecodeError.
    Falls back to 'utf-8'.
    """
    if candidate_encodings is None:
        candidate_encodings = ("utf-8-sig", "utf-8", "cp932", "shift_jis", "euc_jp")
    for enc in candidate_encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.read(2048)
            return enc
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise
    return "utf-8"


def load_csv(
    file_path: str,
    sep: str = ",",
    encoding: str = "auto",
    header: bool = True,
    use_pandas: bool = True,
    usecols: Optional[Sequence[str]] = None,
    nrows: Optional[int] = None,
) -> Union["pd.DataFrame", List[Dict[str, str]]]:
    """Load a CSV as pandas DataFrame when possible; fallback to list of dicts.

    - When header=False, generates generic names: col_1, col_2, ...
    - When pandas is unavailable or use_pandas=False, returns a list of dicts.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    actual_encoding = detect_encoding(file_path) if encoding == "auto" else encoding

    if use_pandas:
        try:
            import pandas as pd  # type: ignore
        except Exception:  # pandas not available
            return _load_csv_with_csv_module(file_path, sep, actual_encoding, header, usecols, nrows)

        header_arg = 0 if header else None
        names_arg = None
        if not header:
            # Read minimal chunk to infer number of columns
            tmp = pd.read_csv(file_path, encoding=actual_encoding, sep=sep, header=None, nrows=1)
            names_arg = [f"col_{i+1}" for i in range(tmp.shape[1])]

        df = pd.read_csv(
            file_path,
            encoding=actual_encoding,
            sep=sep,
            header=header_arg,
            names=names_arg,
            usecols=usecols,
            nrows=nrows,
        )
        return df

    # Fallback or explicitly requested non-pandas
    return _load_csv_with_csv_module(file_path, sep, actual_encoding, header, usecols, nrows)


def _load_csv_with_csv_module(
    file_path: str,
    sep: str,
    encoding: str,
    header: bool,
    usecols: Optional[Sequence[str]] = None,
    nrows: Optional[int] = None,
) -> List[Dict[str, str]]:
    """Load CSV using Python's csv module and return list of dicts."""
    rows: List[Dict[str, str]] = []
    with open(file_path, "r", encoding=encoding, newline="") as f:
        if header:
            reader = csv.DictReader(f, delimiter=sep)
            if usecols is not None:
                usecols_set = set(usecols)
                for i, row in enumerate(reader):
                    if nrows is not None and i >= nrows:
                        break
                    rows.append({k: row.get(k) for k in row.keys() if k in usecols_set})
            else:
                for i, row in enumerate(reader):
                    if nrows is not None and i >= nrows:
                        break
                    rows.append(row)
        else:
            reader = csv.reader(f, delimiter=sep)
            # Create generic header from first row count
            try:
                first = next(reader)
            except StopIteration:
                return []
            header_names = [f"col_{i+1}" for i in range(len(first))]
            rows.append({h: (first[i] if i < len(first) else "") for i, h in enumerate(header_names)})
            for i, row in enumerate(reader, start=1):
                if nrows is not None and i >= nrows:
                    break
                rows.append({h: (row[idx] if idx < len(row) else "") for idx, h in enumerate(header_names)})
    return rows


def iterate_csv(
    file_path: str,
    sep: str = ",",
    encoding: str = "auto",
    header: bool = True,
) -> Generator[Dict[str, str], None, None]:
    """Iterate rows as dicts without loading everything into memory.

    Yields one row at a time.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)

    actual_encoding = detect_encoding(file_path) if encoding == "auto" else encoding

    with open(file_path, "r", encoding=actual_encoding, newline="") as f:
        if header:
            reader = csv.DictReader(f, delimiter=sep)
            for row in reader:
                yield row
        else:
            reader = csv.reader(f, delimiter=sep)
            header_names: Optional[List[str]] = None
            for row in reader:
                if header_names is None:
                    header_names = [f"col_{i+1}" for i in range(len(row))]
                    yield {h: (row[i] if i < len(row) else "") for i, h in enumerate(header_names)}
                else:
                    yield {h: (row[i] if i < len(row) else "") for i, h in enumerate(header_names)}


__all__ = [
    "detect_encoding",
    "load_csv",
    "iterate_csv",
]
