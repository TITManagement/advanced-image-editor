# ImageEditor

高度な画像編集機能を持つPythonアプリケーション

## 概要

このプロジェクトは、既存のimage_gui_templateライブラリを活用して構築された、プロフェッショナル向けの画像編集アプリケーションです。

## 特徴

- **高度な画像処理**: OpenCVとPillowを使用した本格的な画像編集機能
- **モダンなUI**: CustomTkinterによる洗練されたユーザーインターフェース
- **ライブラリ活用**: 再利用可能なGUIコンポーネントの活用
- **拡張可能**: プラグインシステムによる機能拡張

## 技術スタック

- **Python 3.8+**
- **CustomTkinter**: モダンなGUIフレームワーク
- **OpenCV**: 画像処理ライブラリ
- **Pillow**: Python画像処理ライブラリ
- **NumPy**: 数値計算ライブラリ
- **image_gui_template**: ベースGUIライブラリ

## プロジェクト構造

```
ImageEditor/
├── src/                     # ソースコード
│   ├── main.py             # メインアプリケーション
│   ├── editor/             # 画像編集機能
│   ├── ui/                 # UIコンポーネント
│   └── utils/              # ユーティリティ
├── assets/                 # アセット
├── config/                 # 設定ファイル
├── tests/                  # テストコード
├── requirements.txt        # 依存関係
└── setup.py               # パッケージ設定
```

## インストール

### 1. 依存ライブラリのインストール

```bash
# image_gui_templateライブラリをローカルインストール
pip install -e /Users/tinoue/Development.local/lib/image_gui_template

# その他の依存関係
pip install -r requirements.txt
```

### 2. アプリケーションの実行

```bash
python src/main.py
```

## 開発

このプロジェクトは image_gui_template ライブラリの以下のコンポーネントを活用します：

- `apps.gui_image_processor`: 画像処理アプリケーションベース
- `launchers`: アプリケーション起動システム
- カスタムウィジェットとレイアウト
- 設定管理システム

## ライセンス

MIT License
