import pandas as pd
import os

def split_by_prefecture():
    """
    企業CSVファイルを都道府県別に分割して保存する
    """
    
    # 入力ファイルのパス
    input_files = [
        '00_zenkoku_all_20250630_filtered.csv',
    ]
    
    # 出力ディレクトリ
    output_dir = 'prefecture_split'
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in input_files:
        filepath = filename
        
        if not os.path.exists(filepath):
            print(f"ファイルが見つかりません: {filepath}")
            continue
            
        try:
            print(f"処理中: {filename}")
            
            # CSVファイルを読み込み
            df = pd.read_csv(filepath)
            
            # 列名を確認
            print(f"列名: {df.columns.tolist()}")
            
            # 都道府県の列を特定（prefecture または 4番目の列）
            if 'prefecture' in df.columns:
                prefecture_col = 'prefecture'
            elif len(df.columns) >= 4:
                prefecture_col = df.columns[3]  # 4番目の列
            else:
                print(f"都道府県の列が見つかりません: {filename}")
                continue
            
            print(f"全体データ数: {len(df)}")
            
            # 都道府県別にデータを分割
            prefecture_counts = df[prefecture_col].value_counts()
            print(f"都道府県数: {len(prefecture_counts)}")
            print("都道府県別データ数:")
            for pref, count in prefecture_counts.items():
                print(f"  {pref}: {count}件")
            
            # 各都道府県のファイルを作成して保存
            base_filename = os.path.splitext(filename)[0]
            
            for prefecture in prefecture_counts.index:
                if pd.isna(prefecture):
                    continue
                    
                # 都道府県のデータを抽出
                pref_df = df[df[prefecture_col] == prefecture]
                
                # 都道府県名をファイル名に適した形に変換
                safe_pref_name = str(prefecture).replace('/', '_').replace('\\', '_')
                
                # 出力ファイル名
                output_filename = f"{safe_pref_name}_{base_filename}.csv"
                output_path = os.path.join(output_dir, output_filename)
                
                # CSVファイルとして保存
                pref_df.to_csv(output_path, index=False, encoding='utf-8')
                print(f"保存: {safe_pref_name} ({len(pref_df)}件) -> {output_filename}")
                
        except Exception as e:
            print(f"エラーが発生しました ({filename}): {str(e)}")
        
        print("-" * 50)

def create_summary():
    """
    分割結果のサマリーを作成
    """
    output_dir = 'prefecture_split'
    
    if not os.path.exists(output_dir):
        print(f"出力ディレクトリが見つかりません: {output_dir}")
        return
    
    print("=== 分割結果サマリー ===")
    
    files = os.listdir(output_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    
    from collections import defaultdict
    prefecture_summary = defaultdict(int)
    
    for filename in csv_files:
        filepath = os.path.join(output_dir, filename)
        try:
            df = pd.read_csv(filepath)
            count = len(df)
            
            # 都道府県名を抽出
            if '_' in filename:
                pref_name = filename.split('_')[0]
                prefecture_summary[pref_name] += count
            
            print(f"{filename}: {count}件")
            
        except Exception as e:
            print(f"エラー ({filename}): {str(e)}")
    
    print("\n=== 都道府県別合計 ===")
    for pref, total in sorted(prefecture_summary.items(), key=lambda x: x[1], reverse=True):
        print(f"{pref}: {total}件")

if __name__ == "__main__":
    print("=== 企業データの都道府県別分割 ===")
    split_by_prefecture()
    
    print("\n=== サマリー作成 ===")
    create_summary()
    
    print("\n=== 処理完了 ===")
    print("prefecture_split/ ディレクトリに都道府県別の企業データが保存されました。")
