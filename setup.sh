#!/bin/bash

# EC2インスタンスでPython環境とPlaywright、PostgreSQLセットアップスクリプト
# 実行方法: chmod +x setup.sh && ./setup.sh

echo "=== EC2インスタンス環境セットアップ開始 ==="

# 1. システムアップデート
echo "システムをアップデート中..."
sudo yum update -y

# 2. Gitのインストール
echo "Gitをインストール中..."
sudo yum install git -y

# 3. Python3とpip3のインストール
echo "Python3とpip3をインストール中..."
sudo yum install python3 python3-pip -y

# 4. PostgreSQL関連の依存関係をインストール
echo "PostgreSQL開発パッケージをインストール中..."
sudo yum install postgresql-devel gcc python3-devel libpq-devel -y

# 5. 開発ツールをインストール
echo "開発ツールをインストール中..."
sudo yum groupinstall -y "Development Tools"

# 6. Playwright用の追加パッケージ
echo "Playwright用システムパッケージをインストール中..."
sudo yum install -y \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    ipa-gothic-fonts \
    libXcomposite \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    xorg-x11-fonts-100dpi \
    xorg-x11-fonts-75dpi \
    xorg-x11-fonts-cyrillic \
    xorg-x11-fonts-misc \
    xorg-x11-fonts-Type1 \
    xorg-x11-utils \
    mesa-libgbm \
    nss \
    nspr \
    at-spi2-atk \
    libdrm \
    xorg-x11-server-Xvfb

# 7. pipを最新にアップデート
echo "pipをアップデート中..."
pip3 install --upgrade pip

# 8. Pythonパッケージのインストール
echo "Pythonパッケージをインストール中..."
pip3 install psycopg2-binary
pip3 install playwright

# 9. Playwrightのブラウザをインストール
echo "Playwrightブラウザをインストール中..."
playwright install chromium

# 10. Playwrightの依存関係をインストール
echo "Playwright依存関係をインストール中..."
playwright install-deps

# 11. git clone
echo "git cloneを実行中..."
git clone https://github.com/ymktmk/wantedly.git

# 12. Pythonファイルの実行
echo "Pythonファイルを実行中..."
python3 wantedly/company/main.py
