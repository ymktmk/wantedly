# /Users/ymktmk/wantedly/company/zenkoku/filter.py
from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import Dict, Optional, Set

from csv_utils import detect_encoding, iterate_csv


def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c not in '\\/:*?"<>|\n\r\t')


def split_by_prefecture(
    input_path: str,
    out_dir: str,
    pref_col: str = "prefecture",
    sep: str = ",",
    encoding: str = "auto",
    header: bool = True,
    out_encoding: str = "utf-8-sig",
    include_prefs: Optional[Set[str]] = None,
    name_template: str = "{pref}_{stem}_filtered.csv",
) -> Dict[str, int]:
    if not os.path.isabs(input_path):
        input_path = os.path.abspath(input_path)
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    if not os.path.isabs(out_dir):
        out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    actual_encoding = detect_encoding(input_path) if encoding == "auto" else encoding
    stem = os.path.splitext(os.path.basename(input_path))[0]

    writers: Dict[str, csv.DictWriter] = {}
    files: Dict[str, "os.PathLike"] = {}
    counts: Dict[str, int] = {}

    header_fields = None

    try:
        for i, row in enumerate(
            iterate_csv(input_path, sep=sep, encoding=actual_encoding, header=header)
        ):
            if header_fields is None:
                header_fields = list(row.keys())
                if pref_col not in header_fields:
                    raise KeyError(f"列 '{pref_col}' が見つかりません。列: {header_fields}")

            pref = str(row.get(pref_col, "")).strip()
            if not pref:
                continue
            if include_prefs is not None and pref not in include_prefs:
                continue

            if pref not in writers:
                filename = sanitize_filename(
                    name_template.format(pref=pref, base=os.path.basename(input_path), stem=stem)
                )
                out_path = os.path.join(out_dir, filename)
                f = open(out_path, "w", encoding=out_encoding, newline="")
                files[pref] = f
                w = csv.DictWriter(f, fieldnames=header_fields)
                w.writeheader()
                writers[pref] = w

            writers[pref].writerow({k: row.get(k, "") for k in header_fields})
            counts[pref] = counts.get(pref, 0) + 1
    finally:
        for f in files.values():
            try:
                f.close()
            except Exception:
                pass

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="CSVを都道府県ごとに分割")
    parser.add_argument("--path", required=True, help="入力CSVの絶対パス")
    parser.add_argument(
        "--out-dir",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "prefecture_split")),
        help="出力ディレクトリ（既定: company/prefecture_split）",
    )
    parser.add_argument("--pref-col", default="prefecture", help="都道府県の列名（既定: prefecture）")
    parser.add_argument("--sep", default=",", help="区切り文字（既定: ,）")
    parser.add_argument("--encoding", default="auto", help="入力エンコーディング（autoで自動判定）")
    parser.add_argument("--out-encoding", default="utf-8-sig", help="出力エンコーディング（既定: utf-8-sig）")
    parser.add_argument("--no-header", action="store_true", help="ヘッダー無し入力を指定")
    parser.add_argument(
        "--pref",
        action="append",
        help="対象の都道府県名。複数指定可。未指定なら全件。例: --pref 東京都 --pref 神奈川県",
    )
    parser.add_argument(
        "--name-template",
        default="{pref}_{stem}_filtered.csv",
        help="ファイル名テンプレ。利用可能: {pref}, {base}, {stem}",
    )

    args = parser.parse_args()

    include_prefs = set(args.pref) if args.pref else None

    try:
        counts = split_by_prefecture(
            input_path=args.path,
            out_dir=args.out_dir,
            pref_col=args.pref_col,
            sep=args.sep,
            encoding=args.encoding,
            header=not args.no_header,
            out_encoding=args.out_encoding,
            include_prefs=include_prefs,
            name_template=args.name_template,
        )
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    total = sum(counts.values())
    kinds = len(counts)
    print(f"✅ 出力先: {args.out_dir}")
    print(f"✅ 都道府県数: {kinds}（総行数: {total}）")
    for pref, n in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        print(f"- {pref}: {n} 行")


if __name__ == "__main__":
    main()
