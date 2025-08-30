import csv
import pandas as pd

# Pandasを使用したバージョン（より簡潔）
def extract_company_info_pandas(input_file, output_file=None):
    """
    Pandasを使用してCSVから特定列を抽出（英語ヘッダーを付与）
    """
    try:
        # CSVを読み込み（ヘッダーなしとして読み込み）
        df = pd.read_csv(input_file, header=None, encoding='utf-8')
        
        # 必要な列のみを選択し、英語の列名を設定
        result_df = df.iloc[:, [1, 4, 5, 6, 9, 10, 11, 15]].copy()
        result_df.columns = [
            'corporate_number',
            'last_update_date',
            'corporate_number_assigned_date',
            'company_name',
            'prefecture',
            'city_town',
            'address_details',
            'postal_code'
        ]
        
        # 文字列の前後の空白とクォートを削除
        for col in result_df.columns:
            if result_df[col].dtype == 'object':
                result_df[col] = result_df[col].astype(str).str.strip().str.strip('"')

        # 郵便番号を "XXX-XXXX" 形式に整形（例: 1120004.0 -> 112-0004）
        result_df['postal_code'] = (
            result_df['postal_code']
            .astype('string')
            .str.replace(r'\.0$', '', regex=True)          # 末尾の .0 を除去
            .str.replace(r'\D', '', regex=True)            # 数字以外を除去
            .str.zfill(7)                                  # 7桁にゼロ埋め
            .str.replace(r'(\d{3})(\d{4})', r'\1-\2', regex=True)  # ハイフン挿入
        )

        # 法人番号指定年月日が 2015-10-05 より後のみ残す
        date_threshold = pd.Timestamp('2015-10-05')
        tmp = (
            result_df['corporate_number_assigned_date']
            .astype('string')
            .str.replace(r'\D', '', regex=True)  # 数字以外を除去して YYYYMMDD に正規化
        )
        parsed = pd.to_datetime(tmp, format='%Y%m%d', errors='coerce')
        result_df = result_df[parsed > date_threshold]

        # 会社名が「株式会社」を含む行のみに絞り込み
        result_df = result_df[result_df['company_name'].str.contains('株式会社', na=False)]
        
        if output_file:
            # 英語ヘッダーを出力
            result_df.to_csv(output_file, index=False, header=True, encoding='utf-8')
            print(f"結果を '{output_file}' に保存しました。({len(result_df)}件)")
        else:
            print("\n抽出結果:")
            # 英語ヘッダーを表示
            print(result_df.to_string(index=False, header=True))
        
        return result_df
        
    except Exception as e:
        print(f"エラー: {e}")
        return None


# 使用例
if __name__ == "__main__":
    input_filename = "13_tokyo_all_20250829_01.csv"  # 入力ファイル名を指定
    output_filename = "tokyo_all_01.csv"  # 出力ファイル名を指定
    
    # 方法2: Pandasを使用（推奨）
    print("\n=== Pandasを使用（推奨） ===")
    extract_company_info_pandas(input_filename, output_filename)
