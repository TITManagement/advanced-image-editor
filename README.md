# Advanced Image Editor - Plugin System

プラグインシステム対応版画像編集アプリケーション

## 概要

プラグインシステムを採用した高度な画像編集アプリケーションです。モジュラー設計により、各機能が独立したプラグインとして実装されており、優れた保守性・拡張性・可読性を実現しています。

4つの専門プラグイン（基本調整・濃度調整・フィルター処理・画像解析）により、基本的な画像補正から高度な画像解析まで幅広い画像編集機能を提供します。2Dカーブエディタによるガンマ補正など、プロ仕様の機能も搭載しています。

## 特徴

- **プラグインシステム**: 機能別完全分離による高い保守性
- **モジュラー設計**: 独立開発・テスト可能な設計
- **高度な画像処理**: OpenCVとPillowを使用した本格的な画像編集機能
- **モダンなUI**: CustomTkinterによる4タブ統一インターフェース
- **拡張性**: 新プラグイン簡単追加
- **分離されたアーキテクチャ**: editor/ui/utilsによる責任分担

## ディレクトリ構造

```
src/
├── core/                    # プラグインシステム中核
│   ├── plugin_base.py      # 基底クラス・API定義
│   └── __init__.py
├── plugins/                 # プラグイン格納ディレクトリ
│   ├── basic/              # 基本調整プラグイン
│   ├── density/            # 濃度調整プラグイン
│   ├── filters/            # フィルター処理プラグイン
│   └── analysis/           # 画像解析プラグイン
├── editor/                  # 画像編集機能モジュール
│   ├── image_editor.py     # 画像読み込み・保存・表示
│   └── __init__.py
├── ui/                      # UI関連モジュール
│   ├── main_window.py      # メインウィンドウUI構築
│   └── __init__.py
├── utils/                   # ユーティリティモジュール
│   ├── image_utils.py      # 画像変換・処理ヘルパー
│   └── __init__.py
├── main.py                 # 元の1865行版（参考保持）
└── main_plugin.py          # 新プラグインシステム版 ⭐メイン
```

## インストール方法

### 前提条件

このプロジェクトは外部ライブラリ`gui_framework`に依存しています。  
`gui_framework`は以下のいずれかの場所に配置してください：

- `../../lib/gui_framework` (推奨)
- `../lib/gui_framework`
- `./lib/gui_framework`

### 自動セットアップ（推奨）

全プラットフォーム共通で以下のコマンドを実行：

```bash
# リポジトリをクローン
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor

# 自動セットアップスクリプトを実行（gui_frameworkパスも自動検出）
python scripts/setup_dev_environment.py
```

> 💡 **新規環境構築の詳細ガイド**: 各スクリプトの詳細な使用方法、トラブルシューティング、シナリオ別の実行手順については [📁 scripts/README.md](./scripts/README.md) をご覧ください。

### 手動セットアップ

#### 1. gui_frameworkライブラリの配置確認

```bash
# gui_frameworkが正しい場所にあることを確認
ls ../../lib/gui_framework/__init__.py
# または
ls ../lib/gui_framework/__init__.py
```

#### 2. 仮想環境の作成

```bash
# macOS / Linux
python3 -m venv .venv

# Windows  
python -m venv .venv
```

#### 3. 依存関係のインストール

```bash
# macOS / Linux
.venv/bin/pip install -r requirements.txt

# Windows
.venv\Scripts\pip.exe install -r requirements.txt
```

## 実行方法

### 基本実行

#### macOS / Linux (Ubuntu等)

**推奨実行方法**
```bash
cd <本リポジトリのクローン先ディレクトリ>
.venv/bin/python src/main_plugin.py
```

**仮想環境アクティベート後**
```bash
cd <本リポジトリのクローン先ディレクトリ>
source .venv/bin/activate
python src/main_plugin.py
```

#### Windows

**推奨実行方法（PowerShell/コマンドプロンプト）**
```powershell
cd <本リポジトリのクローン先ディレクトリ>
.venv\Scripts\python.exe src\main_plugin.py
```

**仮想環境アクティベート後**
```powershell
# PowerShell
cd <本リポジトリのクローン先ディレクトリ>
.venv\Scripts\Activate.ps1
python src\main_plugin.py

# コマンドプロンプト
cd <本リポジトリのクローン先ディレクトリ>
.venv\Scripts\activate.bat
python src\main_plugin.py
```

### 起動オプション

アプリケーションは以下のコマンドライン引数をサポートしています：

#### ログレベル指定

**--log-level オプション**
```bash
# 各ログレベルでの起動
.venv/bin/python src/main_plugin.py --log-level DEBUG     # 全メッセージ表示（開発用）
.venv/bin/python src/main_plugin.py --log-level INFO      # 一般情報以上を表示（デフォルト）
.venv/bin/python src/main_plugin.py --log-level WARNING   # 警告以上のみ表示
.venv/bin/python src/main_plugin.py --log-level ERROR     # エラー以上のみ表示
.venv/bin/python src/main_plugin.py --log-level CRITICAL  # 致命的エラーのみ表示
```

**--debug オプション（下位互換性）**
```bash
# デバッグモードで起動（--log-level DEBUGと同等）
.venv/bin/python src/main_plugin.py --debug
```

#### ログレベルの説明

| レベル | 説明 | 表示される内容 |
|--------|------|-------------|
| **DEBUG** | 🔍 開発・デバッグ用 | 詳細な動作情報、プラグイン初期化過程、パラメータ変更履歴 |
| **INFO** | ℹ️ 一般情報（デフォルト） | アプリケーション起動、プラグイン登録、画像読み込み状況 |
| **WARNING** | ⚠️ 警告 | 設定ファイル不足、オプション機能無効化の通知 |
| **ERROR** | ❌ エラー | 機能の一部失敗、画像処理エラー、プラグイン読み込み失敗 |
| **CRITICAL** | 🚨 致命的エラー | アプリケーション継続困難な重大エラー |

#### 使用例

```bash
# 開発時：詳細なデバッグ情報を表示
.venv/bin/python src/main_plugin.py --debug

# 通常使用：重要な情報のみ表示
.venv/bin/python src/main_plugin.py --log-level INFO

# 静寂モード：警告・エラーのみ表示
.venv/bin/python src/main_plugin.py --log-level WARNING
```

## 利用可能なプラグイン

### 🎯 基本調整プラグイン (basic_adjustment)
- **明度調整** (-100〜+100)
- **コントラスト調整** (-100〜+100)  
- **彩度調整** (-100〜+100)
- **リセット機能**

### 🌈 濃度調整プラグイン (density_adjustment)  
- **ガンマ補正** (0.1〜3.0)
- **シャドウ調整** (-100〜+100)
- **ハイライト調整** (-100〜+100)
- **色温度調整** (-100〜+100)
- **2値化処理**
  - 閾値調整 (0〜255)
  - 2値化実行ボタン
- **ヒストグラム均等化ボタン**
- **リセット機能**

### 🌀 フィルター処理プラグイン (filter_processing)
- **ガウシアンブラー** (0〜20)
- **シャープニング** (0〜10)
- **特殊フィルター**
  - ノイズ除去ボタン
  - エンボスボタン
  - エッジ検出ボタン
- **モルフォロジー演算**
  - カーネルサイズ調整 (3〜15)
  - 侵食・膨張・開放・閉鎖ボタン
- **輪郭検出ボタン**
- **リセット機能**

### � 画像解析プラグイン (image_analysis)
- **ヒストグラム解析**
  - ヒストグラム表示ボタン
- **特徴点検出**
  - SIFT特徴点ボタン
  - ORB特徴点ボタン
- **周波数解析**
  - フーリエ変換ボタン
  - DCT変換ボタン
- **画像品質解析**
  - ブラー検出ボタン
  - ノイズ解析ボタン
- **リセット機能**

## 新しいプラグインの作成方法

### Step 1: プラグインディレクトリ作成
```bash
mkdir src/plugins/your_plugin_name
```

### Step 2: プラグインクラス作成 
ファイル: `your_plugin_name/your_plugin.py`

```python
from core.plugin_base import ImageProcessorPlugin, PluginUIHelper
import customtkinter as ctk
from PIL import Image

class YourPlugin(ImageProcessorPlugin):
    def __init__(self):
        """
        プラグインの初期化
        - plugin_id: プラグインの一意識別子（文字列）
        - version: プラグインのバージョン（文字列）
        """
        super().__init__("your_plugin_name", "1.0.0")
        self.parameter_value = 0
    
    def get_display_name(self) -> str:
        """
        UI上に表示されるプラグイン名を返す
        戻り値: プラグインの表示名（日本語可）
        """
        return "あなたのプラグイン"
    
    def get_description(self) -> str:
        """
        プラグインの説明文を返す
        戻り値: プラグインの機能説明（日本語可）
        """
        return "プラグインの説明をここに記載"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """
        プラグインのUI要素を作成
        引数:
        - parent: UI要素を配置する親フレーム（CustomTkinterのCTkFrame）
        """
        # スライダー作成例
        self._sliders['param'], self._labels['param'] = PluginUIHelper.create_slider_with_label(
            parent=parent,           # 親フレーム
            text="パラメータ名",        # スライダーのラベル
            from_=0,                # 最小値
            to=100,                 # 最大値
            default_value=0,        # 初期値
            command=self._on_parameter_change,  # 値変更時のコールバック関数
            value_format="{:.0f}"   # 値の表示フォーマット
        )
    
    def _on_parameter_change(self, value: float) -> None:
        """
        パラメータ変更時の処理
        引数:
        - value: 変更されたパラメータの値（float型）
        """
        self.parameter_value = int(value)
        self._on_parameter_change()  # 親クラスのコールバック呼び出し
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """
        画像処理の実行
        引数:
        - image: 処理対象の画像（PIL.Image.Image型）
        - **params: 追加パラメータ（辞書形式、将来の拡張用）
        戻り値: 処理済みの画像（PIL.Image.Image型）
        """
        # 画像処理ロジックをここに実装
        # self.parameter_valueを使用して画像を変換
        return image  # 処理済み画像を返す
```

### Step 3: __init__.py作成
ファイル: `your_plugin_name/__init__.py`

```python
from .your_plugin import YourPlugin
__all__ = ['YourPlugin']
```

### Step 4: メインアプリに登録
ファイル: `main_plugin.py`

```python
from plugins.your_plugin_name import YourPlugin

# setup_plugins()メソッド内に追加
your_plugin = YourPlugin()
your_plugin.set_parameter_change_callback(self.on_plugin_parameter_change)
self.plugin_manager.register_plugin(your_plugin)

# create_plugin_tabs()メソッドのplugin_tabsに追加
plugin_tabs = {
    # ... 既存のタブ ...
    "your_plugin_name": "タブ名"
}
```

## プラグインAPI仕様

### 必須実装メソッド
- `get_display_name()`: UI表示名
- `get_description()`: プラグイン説明  
- `create_ui(parent)`: UI作成
- `process_image(image, **params)`: 画像処理実行

### オプションメソッド
- `get_parameters()`: 現在のパラメータ取得
- `reset_parameters()`: パラメータリセット
- `set_parameter_change_callback(callback)`: パラメータ変更時コールバック

### ヘルパークラス利用

```python
from core.plugin_base import PluginUIHelper

# スライダー作成
slider, label = PluginUIHelper.create_slider_with_label(
    parent=parent,
    text="パラメータ名",
    from_=0,
    to=100,
    default_value=0,
    command=callback_function,
    value_format="{:.1f}"
)

# ボタン作成  
button = PluginUIHelper.create_button(
    parent=parent,
    text="ボタン名",
    command=button_callback,
    width=120
)
```

## アーキテクチャの特徴

### 🏗️ 設計パターン
- **SOLID原則準拠**
- **依存性注入パターン**
- **インターフェース統一**

### 🚀 開発効率
- **プラグイン独立開発**
- **単体テスト容易**
- **並行開発可能**

### 🔧 保守性
- **機能別完全分離**
- **コード重複除去**
- **責任分担明確**

### 📈 拡張性
- **新プラグイン簡単追加**
- **既存コード影響なし**
- **バージョン管理対応**

## モジュール構成の詳細

### 🖼️ editor/
**画像エディター機能**
- `image_editor.py`: 画像読み込み・保存・表示・状態管理
- 画像ファイルの入出力処理
- キャンバス表示とリサイズ処理
- オリジナル/現在画像の管理

### 🎨 ui/  
**ユーザーインターフェース**
- `main_window.py`: メインウィンドウレイアウト構築
- ウィンドウプロパティ設定
- パネル・キャンバス・ボタンレイアウト
- プラグインタブビュー管理

### 🔧 utils/
**ユーティリティ機能**
- `image_utils.py`: 画像変換・処理ヘルパー関数
- PIL ↔ OpenCV 変換
- 各種画像処理アルゴリズム（明度・コントラスト・彩度・ガンマ・ブラー等）
- 画像情報取得・フォーマット処理

## gui_framework連携

gui_frameworkライブラリが利用可能な場合は高度なUI機能を使用。
利用できない場合は基本機能のみで動作（フォールバック対応済み）。

## トラブルシューティング

### インポートエラー
- プラグインディレクトリの`__init__.py`ファイル確認
- Pythonパス設定確認

### UI表示エラー  
- `create_ui()`メソッドの実装確認
- PluginUIHelperの正しい使用確認

### 画像処理エラー
- `process_image()`メソッドの例外処理確認
- 入力画像の形式確認

## 変革の成果

### Before (元のコード)
- **main.py**: 1865行の巨大ファイル
- **保守性**: 機能追加が困難、コード重複多数
- **拡張性**: 新機能追加で既存コードに影響
- **可読性**: 機能が混在、責任分離不明確

### After (プラグインシステム + モジュラー設計)
- **main_plugin.py**: ~320行の軽量メインアプリ
- **4個のプラグイン**: 機能別完全分離
- **3個のモジュール**: editor/ui/utils責任分担
- **統一API**: 一貫したインターフェース
- **モジュラー設計**: 独立開発・テスト可能

### アーキテクチャの改善
```
【旧構造】
main.py (1865行)
└── すべての機能が混在

【新構造】  
main_plugin.py (320行)
├── editor/ (画像処理)
├── ui/ (インターフェース)
├── utils/ (ヘルパー)
├── core/ (プラグインベース)
└── plugins/ (4個の専門プラグイン)
```

## 今後の拡張ロードマップ

1. **外部プラグインサポート**: 独立パッケージとしてのプラグイン配布
2. **プラグインストア**: 動的ダウンロード・インストール機能
3. **AI画像処理プラグイン**: 機械学習ベースの高度処理
4. **リアルタイム処理**: GPU加速・並列処理最適化
5. **クラウド連携**: オンラインプラグインレポジトリ

## 技術スタック

- **Python 3.8+** (Cross-Platform Compatible)
- **CustomTkinter**: モダンなGUIフレームワーク
- **OpenCV**: 画像処理ライブラリ
- **Pillow**: Python画像処理ライブラリ
- **NumPy**: 数値計算ライブラリ
- **Matplotlib**: データ可視化ライブラリ

### 対応プラットフォーム

- **macOS** 10.14+ (Mojave以降)
- **Windows** 10/11 (64-bit)
- **Linux** (Ubuntu 18.04+, その他ディストリビューション)

### システム要件

- **Python**: 3.8以上
- **メモリ**: 4GB以上推奨
- **ディスク容量**: 500MB以上の空き容量
- **ディスプレイ**: 1024x768以上の解像度

---

**作成者**: GitHub Copilot + プラグインシステム設計  
**バージョン**: Plugin System 1.0.0  
**最終更新**: 2025年9月13日
