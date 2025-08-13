# /Users/ymktmk/wantedly/company/zenkoku/diff.py
from __future__ import annotations

import argparse
import csv
import os
from typing import Iterable, List, Sequence, Set, Tuple, Dict

from csv_utils import detect_encoding, iterate_csv


def make_key(row: Dict[str, str], key_cols: Sequence[str]) -> Tuple[str, ...]:
    return tuple(str(row.get(col, "")).strip() for col in key_cols)


def read_key_set(path: str, key_cols: Sequence[str], sep: str, encoding: str, header: bool) -> Set[Tuple[str, ...]]:
    keys: Set[Tuple[str, ...]] = set()
    for row in iterate_csv(path, sep=sep, encoding=encoding, header=header):
        keys.add(make_key(row, key_cols))
    return keys


def diff_added_removed(
    old_path: str,
    new_path: str,
    out_added: str | None,
    out_removed: str | None,
    key_cols: Sequence[str],
    sep: str = ",",
    in_encoding: str = "auto",
    out_encoding: str = "utf-8-sig",
    header: bool = True,
) -> Tuple[int, int]:
    # 正規化パス
    if not os.path.isabs(old_path): old_path = os.path.abspath(old_path)
    if not os.path.isabs(new_path): new_path = os.path.abspath(new_path)
    if out_added and not os.path.isabs(out_added): out_added = os.path.abspath(out_added)
    if out_removed and not os.path.isabs(out_removed): out_removed = os.path.abspath(out_removed)

    if not os.path.exists(old_path): raise FileNotFoundError(old_path)
    if not os.path.exists(new_path): raise FileNotFoundError(new_path)

    enc_old = detect_encoding(old_path) if in_encoding == "auto" else in_encoding
    enc_new = detect_encoding(new_path) if in_encoding == "auto" else in_encoding

    # 旧→キー集合
    old_keys = read_key_set(old_path, key_cols, sep=sep, encoding=enc_old, header=header)

    # 新→追加の書き出し（ヘッダーは新側に合わせる）
    added_count = 0
    removed_count = 0

    added_writer: csv.DictWriter | None = None
    added_file = None
    new_header_fields: List[str] | None = None

    if out_added:
        # 先に新側のヘッダーを得るため1行見る
        for row in iterate_csv(new_path, sep=sep, encoding=enc_new, header=header):
            new_header_fields = list(row.keys())
            break
        if new_header_fields is None:
            new_header_fields = []

        added_file = open(out_added, "w", encoding=out_encoding, newline="")
        added_writer = csv.DictWriter(added_file, fieldnames=new_header_fields)
        added_writer.writeheader()

    # 新ファイルを流しながら追加判定
    for row in iterate_csv(new_path, sep=sep, encoding=enc_new, header=header):
        k = make_key(row, key_cols)
        if k not in old_keys:
            if added_writer is not None:
                added_writer.writerow({c: row.get(c, "") for c in added_writer.fieldnames})
            added_count += 1

    if added_file is not None:
        added_file.close()

    # 削除（旧にあるが新に無い）を出す場合は、新キー集合をまず作る
    if out_removed:
        new_keys = read_key_set(new_path, key_cols, sep=sep, encoding=enc_new, header=header)

        removed_file = None
        removed_writer: csv.DictWriter | None = None
        old_header_fields: List[str] | None = None

        # 旧側のヘッダー
        for row in iterate_csv(old_path, sep=sep, encoding=enc_old, header=header):
            old_header_fields = list(row.keys())
            break
        if old_header_fields is None:
            old_header_fields = []

        removed_file = open(out_removed, "w", encoding=out_encoding, newline="")
        removed_writer = csv.DictWriter(removed_file, fieldnames=old_header_fields)
        removed_writer.writeheader()

        # 旧を再走査して削除分を書く
        for row in iterate_csv(old_path, sep=sep, encoding=enc_old, header=header):
            k = make_key(row, key_cols)
            if k not in new_keys:
                removed_writer.writerow({c: row.get(c, "") for c in removed_writer.fieldnames})
                removed_count += 1

        removed_file.close()

    return added_count, removed_count


def main() -> None:
    parser = argparse.ArgumentParser(description="2つのCSVの差分（追加・削除）をキー列で判定してCSV出力")
    parser.add_argument("--old", required=True, help="旧CSVの絶対パス")
    parser.add_argument("--new", required=True, help="新CSVの絶対パス")
    parser.add_argument("--out-added", required=True, help="追加行を書き出すCSVパス（新CSVのヘッダー）")
    parser.add_argument("--out-removed", default=None, help="削除行を書き出すCSVパス（旧CSVのヘッダー）")
    parser.add_argument("--key-cols", default="id", help="キー列（カンマ区切り）。例: id,code")
    parser.add_argument("--sep", default=",", help="区切り文字（既定: ,）")
    parser.add_argument("--encoding", default="auto", help="入力の推定エンコーディング（autoで自動判定）")
    parser.add_argument("--out-encoding", default="utf-8-sig", help="出力エンコーディング（既定: utf-8-sig）")
    parser.add_argument("--no-header", action="store_true", help="ヘッダー無し入力を指定")

    args = parser.parse_args()
    key_cols = [c.strip() for c in args.key_cols.split(",") if c.strip()]

    added, removed = diff_added_removed(
        old_path=args.old,
        new_path=args.new,
        out_added=args.out_added,
        out_removed=args.out_removed,
        key_cols=key_cols,
        sep=args.sep,
        in_encoding=args.encoding,
        out_encoding=args.out_encoding,
        header=not args.no_header,
    )

    print(f"✅ 追加: {added} 行 -> {args.out_added}")
    if args.out_removed:
        print(f"✅ 削除: {removed} 行 -> {args.out_removed}")


if __name__ == "__main__":
    main()