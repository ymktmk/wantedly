import argparse
import csv
import os
import sys
from typing import List, Optional


def detect_encoding(file_path: str, candidate_encodings: Optional[List[str]] = None) -> str:
    if candidate_encodings is None:
        candidate_encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis", "euc_jp"]
    for enc in candidate_encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                f.read(1024)
            return enc
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            raise
    return "utf-8"


def read_preview_with_csv(
    file_path: str,
    encoding: str,
    delimiter: str,
    head: int,
    no_header: bool,
    filter_col: Optional[str],
    contains: Optional[str],
):
    header: List[str] = []
    preview_rows: List[List[str]] = []

    with open(file_path, "r", encoding=encoding, newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        first_row: Optional[List[str]] = None
        try:
            first_row = next(reader)
        except StopIteration:
            print("ファイルが空です。")
            return

        if no_header:
            num_cols = len(first_row)
            header = [f"col_{i+1}" for i in range(num_cols)]
            data_iter = [first_row]
        else:
            header = first_row
            data_iter = []

        # Filtering setup
        col_index: Optional[int] = None
        if filter_col is not None:
            if filter_col in header:
                col_index = header.index(filter_col)
            else:
                print(f"指定した列が見つかりません: {filter_col}")
                print(f"利用可能な列: {header}")
                sys.exit(2)

        def row_matches(row: List[str]) -> bool:
            if contains is None or col_index is None:
                return True
            target = row[col_index] if col_index < len(row) else ""
            return contains.lower() in str(target).lower()

        # Gather preview rows
        for row in data_iter:
            if row_matches(row):
                preview_rows.append(row)
                if len(preview_rows) >= head:
                    break

        if len(preview_rows) < head:
            for row in reader:
                if row_matches(row):
                    preview_rows.append(row)
                    if len(preview_rows) >= head:
                        break

    print(f"推定エンコーディング: {encoding}")
    print(f"区切り文字: '{delimiter}'")
    print("列名:")
    print(header)

    print(f"\n先頭{len(preview_rows)}行:")
    if not preview_rows:
        print("(該当データなし)")
    else:
        # Pretty print rows with header widths
        col_widths = [max(len(str(h)), *(len(str(r[i])) if i < len(r) else 0 for r in preview_rows)) for i, h in enumerate(header)]
        def fmt_row(row: List[str]) -> str:
            cells = []
            for i, w in enumerate(col_widths):
                val = row[i] if i < len(row) else ""
                cells.append(str(val).ljust(w))
            return " | ".join(cells)
        print(fmt_row(header))
        print("-+-".join("-" * w for w in col_widths))
        for r in preview_rows:
            print(fmt_row(r))


def read_preview_with_pandas(
    file_path: str,
    encoding: str,
    delimiter: str,
    head: int,
    no_header: bool,
    filter_col: Optional[str],
    contains: Optional[str],
):
    import pandas as pd  # type: ignore

    header_arg = None if no_header else 0
    names_arg = None
    if no_header:
        # Read minimal rows to infer number of columns
        tmp = pd.read_csv(file_path, encoding=encoding, sep=delimiter, header=None, nrows=1)
        names_arg = [f"col_{i+1}" for i in range(tmp.shape[1])]

    df = pd.read_csv(file_path, encoding=encoding, sep=delimiter, header=header_arg, nrows=head, names=names_arg)

    if filter_col is not None and contains is not None and filter_col in df.columns:
        df = df[df[filter_col].astype(str).str.contains(contains, case=False, na=False)]

    print(f"推定エンコーディング: {encoding}")
    print(f"区切り文字: '{delimiter}'")
    print("列名:")
    print(list(df.columns))

    print(f"\n先頭{min(head, len(df))}行:")
    if df.empty:
        print("(該当データなし)")
    else:
        # Avoid index column
        print(df.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="CSVプレビュー: 列名と先頭N行を表示")
    parser.add_argument("--path", default="/workspace/company/00_zenkoku_all_20250630.csv", help="CSVファイルのパス")
    parser.add_argument("--encoding", default="auto", help="エンコーディング。'auto' で自動判定")
    parser.add_argument("--sep", default=",", help="区切り文字。デフォルトはカンマ")
    parser.add_argument("--head", type=int, default=5, help="表示する先頭行数")
    parser.add_argument("--no-header", action="store_true", help="ヘッダー行が無い場合に指定")
    parser.add_argument("--filter-col", default=None, help="フィルタ対象の列名")
    parser.add_argument("--contains", default=None, help="指定文字列を含む行のみ表示")

    args = parser.parse_args()

    csv_path = args.path
    if not os.path.isabs(csv_path):
        csv_path = os.path.abspath(csv_path)

    if not os.path.exists(csv_path):
        print(f"ファイルが見つかりません: {csv_path}")
        sys.exit(1)

    encoding = args.encoding
    if encoding == "auto":
        encoding = detect_encoding(csv_path)

    # Try pandas first if available, otherwise fallback
    try:
        import pandas as pd  # noqa: F401
        read_preview_with_pandas(
            file_path=csv_path,
            encoding=encoding,
            delimiter=args.sep,
            head=args.head,
            no_header=args.no_header,
            filter_col=args.filter_col,
            contains=args.contains,
        )
    except Exception:
        read_preview_with_csv(
            file_path=csv_path,
            encoding=encoding,
            delimiter=args.sep,
            head=args.head,
            no_header=args.no_header,
            filter_col=args.filter_col,
            contains=args.contains,
        )


if __name__ == "__main__":
    main()