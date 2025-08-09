import argparse
import os
import sys
from csv_utils import detect_encoding, load_csv, iterate_csv


def main():
    parser = argparse.ArgumentParser(description="CSVプレビュー: 列名と先頭N行を表示")
    parser.add_argument("--path", default="/workspace/company/00_zenkoku_all_20250630_filtered.csv", help="CSVファイルのパス")
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

    enc = detect_encoding(csv_path) if args.encoding == "auto" else args.encoding

    # Try pandas path
    try:
        df = load_csv(csv_path, sep=args.sep, encoding=enc, header=not args.no_header, use_pandas=True, nrows=args.head)
        columns = list(df.columns)  # type: ignore
        print(f"推定エンコーディング: {enc}")
        print(f"区切り文字: '{args.sep}'")
        print("列名:")
        print(columns)
        if args.filter_col and args.contains and args.filter_col in df.columns:  # type: ignore
            df = df[df[args.filter_col].astype(str).str.contains(args.contains, case=False, na=False)]  # type: ignore
        print(f"\n先頭{min(args.head, len(df))}行:")  # type: ignore
        if len(df) == 0:  # type: ignore
            print("(該当データなし)")
        else:
            print(df.to_string(index=False))  # type: ignore
        return
    except Exception:
        pass

    # Fallback to iterator for low memory usage
    print(f"推定エンコーディング: {enc}")
    print(f"区切り文字: '{args.sep}'")

    header_row = None
    count = 0
    for i, row in enumerate(iterate_csv(csv_path, sep=args.sep, encoding=enc, header=not args.no_header)):
        if header_row is None:
            header_row = list(row.keys())
            print("列名:")
            print(header_row)
            print()
        if args.filter_col and args.contains:
            if args.filter_col in row and args.contains.lower() not in str(row[args.filter_col]).lower():
                continue
        if count < args.head:
            if count == 0:
                # print header again nicely
                widths = [max(len(str(h)), 10) for h in header_row]
                print(" | ".join(str(h).ljust(w) for h, w in zip(header_row, widths)))
                print("-+-".join("-" * w for w in widths))
            print(" | ".join(str(row.get(h, "")).ljust(max(len(str(h)), 10)) for h in header_row))
            count += 1
        else:
            break
    if count == 0:
        print("(該当データなし)")


if __name__ == "__main__":
    main()