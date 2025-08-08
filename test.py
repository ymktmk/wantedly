import pandas as pd
import os
from datetime import datetime

def remove_duplicate_companies(input_file, output_file):
    """
    CSVファイルから重複する会社名を除去して新しいCSVファイルを作成する
    
    Args:
        input_file (str): 入力CSVファイルのパス
        output_file (str): 出力CSVファイルのパス
    """
    
    try:
        # CSVファイルを読み込み
        df = pd.read_csv(input_file)
        
        print(f"元のデータ行数: {len(df)}")
        print(f"重複前の会社数: {len(df['company'].unique())}")
        
        # 重複する会社名を確認
        duplicates = df[df.duplicated(subset=['company'], keep=False)]
        duplicate_companies = duplicates['company'].unique()
        
        print(f"重複している会社数: {len(duplicate_companies)}")
        print("\n重複している会社名の例:")
        for i, company in enumerate(duplicate_companies[:10]):  # 最初の10個だけ表示
            count = len(df[df['company'] == company])
            print(f"  {i+1}. {company} (重複数: {count})")
        
        if len(duplicate_companies) > 10:
            print(f"  ... その他 {len(duplicate_companies) - 10} 社")
        
        # 重複を除去（最初の出現を保持）
        df_unique = df.drop_duplicates(subset=['company'], keep='first')
        
        print(f"\n重複除去後の行数: {len(df_unique)}")
        print(f"除去された行数: {len(df) - len(df_unique)}")
        
        # 新しいCSVファイルに保存
        df_unique.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"\n新しいCSVファイルを作成しました: {output_file}")
        
        return df_unique
        
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {input_file}")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

def analyze_duplicates(input_file):
    """
    重複の詳細分析を行う
    
    Args:
        input_file (str): 入力CSVファイルのパス
    """
    
    try:
        df = pd.read_csv(input_file)
        
        # 重複数の分析
        duplicate_counts = df['company'].value_counts()
        duplicated_companies = duplicate_counts[duplicate_counts > 1]
        
        print("\n=== 重複分析結果 ===")
        print(f"重複している会社数: {len(duplicated_companies)}")
        print(f"最も重複の多い会社 TOP 10:")
        
        for i, (company, count) in enumerate(duplicated_companies.head(10).items()):
            print(f"  {i+1}. {company}: {count}回")
            
        return duplicated_companies
        
    except Exception as e:
        print(f"分析中にエラーが発生しました: {e}")
        return None

def main():
    """
    メイン処理
    """
    
    input_file = "wantedly_jobs3.csv"
    
    # タイムスタンプ付きの出力ファイル名を生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"wantedly_jobs_unique_{timestamp}.csv"
    
    print("=== Wantedly求人データ 重複除去ツール ===")
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}")
    
    # 入力ファイルの存在確認
    if not os.path.exists(input_file):
        print(f"エラー: 入力ファイル '{input_file}' が見つかりません。")
        return
    
    # 重複分析
    analyze_duplicates(input_file)
    
    # 重複除去実行
    result_df = remove_duplicate_companies(input_file, output_file)
    
    if result_df is not None:
        print("\n=== 処理完了 ===")
        print("重複除去が正常に完了しました。")
        
        # 簡単な統計情報を表示
        print(f"\n最終結果:")
        print(f"  ユニークな会社数: {len(result_df)}")
        print(f"  保存ファイル: {output_file}")

if __name__ == "__main__":
    main() 