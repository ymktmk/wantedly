import argparse
import os
import sys
from csv_utils import detect_encoding, load_csv, iterate_csv
from datetime import datetime
import csv


def main():
    parser = argparse.ArgumentParser(description="CSVプレビュー: 列名と先頭N行を表示")
    parser.add_argument("--path", default="00_zenkoku_all_20250630.csv", help="CSVファイルのパス")
    parser.add_argument("--encoding", default="auto", help="エンコーディング。'auto' で自動判定")
    parser.add_argument("--sep", default=",", help="区切り文字。デフォルトはカンマ")
    parser.add_argument("--head", type=int, default=1, help="表示する先頭行数")
    parser.add_argument("--no-header", action="store_true", help="ヘッダー行が無い場合に指定")
    parser.add_argument("--filter-col", default=None, help="フィルタ対象の列名")
    parser.add_argument("--contains", default=None, help="指定文字列を含む行のみ表示")
    parser.add_argument("--date-from", default="2015-10-06", help="この日付(YYYY-MM-DD)以降の行のみ表示 (既定: 2015-10-05)")
    parser.add_argument("--date-col", default="date", help="日付列名 (デフォルト: 'date')")
    parser.add_argument("--out", default=None, help="フィルタ後のデータを書き出すCSVパス")
    parser.add_argument("--out-encoding", default="utf-8-sig", help="出力CSVのエンコーディング (既定: utf-8-sig)")
    parser.add_argument(
        "--out-cols",
        default="id,company,code,prefecture,date,homepage_url,contact_url,description",
        help="書き出し時の列（カンマ区切り、順序通りに出力）",
    )

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
        df = load_csv(csv_path, sep=args.sep, encoding=enc, header=not args.no_header, use_pandas=True)
        columns = list(df.columns)  # type: ignore
        print(f"推定エンコーディング: {enc}")
        print(f"区切り文字: '{args.sep}'")
        print("列名:")
        print(columns)
        # contains filter
        if args.filter_col and args.contains and args.filter_col in df.columns:  # type: ignore
            df = df[df[args.filter_col].astype(str).str.contains(args.contains, case=False, na=False)]  # type: ignore
        # date-from filter
        if args.date_from and args.date_col in df.columns:  # type: ignore
            import pandas as pd  # type: ignore
            try:
                threshold = pd.to_datetime(args.date_from, errors="raise")
            except Exception:
                print(f"無効な--date-from形式です: {args.date_from}. 例: 2015-10-05")
                sys.exit(2)
            dates = pd.to_datetime(df[args.date_col], errors="coerce")  # type: ignore
            df = df[dates >= threshold]
        print(f"\n先頭{min(args.head, len(df))}行:")  # type: ignore
        if len(df) == 0:  # type: ignore
            print("(該当データなし)")
        else:
            print(df.head(args.head).to_string(index=False))  # type: ignore
        # optional write-out of full filtered data
        if args.out:
            out_cols = [c.strip() for c in str(args.out_cols).split(',') if c.strip()]
            # ensure all columns exist, fill missing with empty string
            for c in out_cols:
                if c not in df.columns:  # type: ignore
                    df[c] = ""  # type: ignore
            df_out = df[out_cols]  # type: ignore
            df_out.to_csv(args.out, index=False, encoding=args.out_encoding)  # type: ignore
            print(f"\n💾 書き出し: {args.out} ({len(df_out)}行)")  # type: ignore
        return
    except Exception:
        pass

    # Fallback to iterator for low memory usage
    print(f"推定エンコーディング: {enc}")
    print(f"区切り文字: '{args.sep}'")

    header_row = None
    count = 0  # printed count
    write_count = 0
    writer = None
    out_file = None
    # prepare date threshold for iterator path
    date_threshold = None
    if args.date_from:
        try:
            date_threshold = datetime.strptime(args.date_from, "%Y-%m-%d")
        except ValueError:
            print(f"無効な--date-from形式です: {args.date_from}. 例: 2015-10-05")
            sys.exit(2)
    for i, row in enumerate(iterate_csv(csv_path, sep=args.sep, encoding=enc, header=not args.no_header)):
        if header_row is None:
            header_row = list(row.keys())
            print("列名:")
            print(header_row)
            print()
            if args.out:
                out_cols = [c.strip() for c in str(args.out_cols).split(',') if c.strip()]
                # 出力列がヘッダーに無ければ空列として扱うため、そのまま出力列を使う
                out_file = open(args.out, "w", encoding=args.out_encoding, newline="")
                writer = csv.DictWriter(out_file, fieldnames=out_cols)
                writer.writeheader()
        if args.filter_col and args.contains:
            if args.filter_col in row and args.contains.lower() not in str(row[args.filter_col]).lower():
                continue
        if date_threshold is not None:
            date_str = str(row.get(args.date_col, ""))
            if not date_str:
                continue
            try:
                # take first 10 chars to guard stray time strings
                row_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
            except ValueError:
                continue
            if row_date < date_threshold:
                continue
        # write all matching rows if output is requested
        if writer is not None:
            # 出力列に合わせて順序と欠損埋めを行う
            writer.writerow({k: row.get(k, "") for k in writer.fieldnames})
            write_count += 1

        if count < args.head:
            if count == 0:
                # print header again nicely
                widths = [max(len(str(h)), 10) for h in header_row]
                print(" | ".join(str(h).ljust(w) for h, w in zip(header_row, widths)))
                print("-+-".join("-" * w for w in widths))
            print(" | ".join(str(row.get(h, "")).ljust(max(len(str(h)), 10)) for h in header_row))
            count += 1
        # stop early only when not writing out
        if writer is None and count >= args.head:
            break
    if out_file is not None:
        out_file.close()
    if (count == 0) and (write_count == 0):
        print("(該当データなし)")
    if args.out and write_count > 0:
        print(f"\n💾 書き出し: {args.out} ({write_count}行)")


if __name__ == "__main__":
    main()
