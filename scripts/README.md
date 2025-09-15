# 📁 **Scripts Directory - Advanced Image Editor**

このディレクトリには、Advanced Image Editorの開発・配布・検証に必要なユーティリティスクリプトが含まれています。

## 🕐 **いつ使うのか**

これらのスクリプトは以下のシチュエーションで使用します：

### 🚀 **新規環境でのセットアップ時**
- 新しいPC・サーバーでの開発環境構築
- チームメンバーの環境統一
- CI/CDパイプラインでの自動環境構築

**👉 使用スクリプト**: `setup_dev_environment.py` → `comprehensive_verification.py`

### 📦 **リリース・配布準備時**
- 顧客向け配布パッケージの作成
- 異なるOSでのテスト配布
- ポータブル版・インストーラー生成

**👉 使用スクリプト**: `comprehensive_verification.py` → `build_distribution.py`

### 🧪 **システム検証・デバッグ時**
- 新機能追加後の動作確認
- 環境変更後の整合性チェック
- バグ報告前の基本機能確認

**👉 使用スクリプト**: `comprehensive_verification.py`

### 🔄 **定期メンテナンス時**
- 依存関係の更新確認
- 全プラットフォームでの動作テスト
- パフォーマンス・品質チェック

**👉 使用スクリプト**: `setup_dev_environment.py` → `comprehensive_verification.py` → `build_distribution.py`

---

## 📋 **スクリプト一覧**



### 🚀 **setup_dev_environment.py**
**クロスプラットフォーム開発環境自動セットアップ**

#### 📝 **概要**
Windows, macOS, Linux での完全対応環境を自動構築するスクリプトです。

#### 🎯 **主要機能**
- **仮想環境の自動作成** (OS別最適化)
- **依存関係の自動インストール** (OS固有パッケージ含む)
- **GUI Framework の検出・インストール**
- **システム要件の検証・診断**
- **環境構築状況の詳細レポート**

#### 🔧 **対応OS**
- **Windows** 10/11 (x64, ARM64)
- **macOS** 10.15+ (Intel, Apple Silicon)
- **Linux** (Ubuntu, CentOS, Fedora, Arch)

#### 💻 **使用方法**
```bash
# 基本実行（推奨）
python scripts/setup_dev_environment.py

# 仮想環境有効化後
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate     # Windows
```

#### ✅ **実行後の確認**
- 仮想環境が `.venv/` に作成される
- 必要な依存関係がインストールされる
- システム診断レポートが表示される

---

### 📦 **build_distribution.py**
**クロスプラットフォーム配布パッケージ生成**

#### 📝 **概要**
Windows, macOS, Linux 用の配布パッケージを自動生成するスクリプトです。

#### 🎯 **主要機能**
- **ワンクリックインストーラー生成**
- **OS別バイナリパッケージ作成**
- **依存関係バンドリング**
- **ポータブル版作成**

#### 📦 **生成される配布形式**
- **Windows**: `.exe` 実行ファイル、NSIS インストーラー
- **macOS**: `.app` バンドル、`.dmg` インストーラー
- **Linux**: バイナリ、`.desktop` ファイル、AppImage 準備

#### 💻 **使用方法**
```bash
# 全配布形式を作成
python scripts/build_distribution.py

# 特定の形式のみ作成
python scripts/build_distribution.py executable    # 実行ファイルのみ
python scripts/build_distribution.py installer     # インストーラーのみ
python scripts/build_distribution.py portable      # ポータブル版のみ
```

#### 📁 **出力ディレクトリ**
- `dist/` - 生成された配布パッケージ
- `build/` - ビルド中間ファイル

---

### 🧪 **comprehensive_verification.py**
**包括的システム検証**

#### 📝 **概要**
Advanced Image Editorの全機能を段階的に検証し、システムの健全性を確認するスクリプトです。

#### 🎯 **検証項目**
- **環境チェック**: Python バージョン、依存関係
- **インポートテスト**: 全モジュールの読み込み確認
- **プラグインシステム**: 4つのプラグインの動作確認
- **画像処理機能**: 基本的な画像処理テスト
- **UI コンポーネント**: GUI要素の初期化確認

#### 💻 **使用方法**
```bash
# 完全検証実行
python scripts/comprehensive_verification.py

# 検証結果は標準出力に表示
```

#### 📊 **出力例**
```
🔍 環境チェック
✅ Python バージョン: 3.11.5
✅ 必要ライブラリ: すべてインストール済み

🔍 プラグインシステム検証
✅ 基本調整プラグイン
✅ 濃度調整プラグイン
✅ フィルタープラグイン
✅ 高度処理プラグイン
```

---

## 🚀 **クイックスタート**

### 1️⃣ **開発環境構築**
```bash
# リポジトリクローン
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor

# 環境自動構築
python scripts/setup_dev_environment.py
```

### 2️⃣ **動作確認**
```bash
# 検証実行
python scripts/comprehensive_verification.py

# アプリケーション起動
python src/main_plugin.py
```

### 3️⃣ **配布パッケージ作成**
```bash
# 配布版生成
python scripts/build_distribution.py
```

---

## 🔧 **開発者向け情報**

### 📋 **前提条件**
- **Python**: 3.9以上 (推奨: 3.11+)
- **Git**: 最新版
- **OS固有要件**:
  - Windows: Visual Studio Build Tools
  - macOS: Xcode Command Line Tools
  - Linux: python3-dev, python3-tk

### 🔗 **依存関係**
- **GUI**: `customtkinter`, `tkinter`
- **画像処理**: `opencv-python`, `Pillow`, `numpy`
- **科学計算**: `scipy`, `scikit-image`
- **配布**: `PyInstaller`

### 🏗️ **ビルドプロセス**
1. **環境準備**: `setup_dev_environment.py`
2. **検証**: `comprehensive_verification.py`
3. **配布作成**: `build_distribution.py`

---

## 🛠️ **トラブルシューティング**

### ❓ **よくある問題**

#### **Q: 環境構築でエラーが発生する**
```bash
# Python バージョン確認
python --version

# 管理者権限で実行 (Windows)
# または sudo 権限 (Linux)
```

#### **Q: 依存関係のインストールに失敗する**
```bash
# pip 更新
python -m pip install --upgrade pip

# 仮想環境再作成
rm -rf .venv
python scripts/setup_dev_environment.py
```

#### **Q: 配布パッケージ作成に失敗する**
```bash
# PyInstaller インストール確認
pip install pyinstaller

# OS固有ツール確認
# Windows: NSIS
# macOS: Xcode
# Linux: build-essential
```

### 🆘 **サポート**
- **GitHub Issues**: [Issues ページ](https://github.com/TITManagement/advanced-image-editor/issues)
- **Discussions**: [Discussions ページ](https://github.com/TITManagement/advanced-image-editor/discussions)

---

## 📄 **ライセンス**
MIT License - 詳細は [LICENSE](../LICENSE) ファイルを参照

---

**🎉 これらのスクリプトで、Advanced Image Editor の開発・配布・検証が完全自動化されます！**