# Advanced Image Editor

> 🔌 llllllllll

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](https://github.com/TITManagement/advanced-image-editor)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**リアルタイム画像処理** | **4つの専門プラグイン** | **モジュラー設計** | **クロスプラットフォーム**

## 🚀 クイックスタート

```bash
# 1. インストール
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor
python scripts/setup_dev_environment.py

# 2. 実行
.venv/bin/python src/main_plugin.py

# 3. 画像を開いて編集開始！
```

#### 【重要】pip index一元管理について
依存解決の再現性向上のため、pip の index 設定は  
`$AILAB_ROOT/lab_automation_libs/internal-PyPI/pip.conf.local` を正本とします。

ローカル環境では `AILAB_ROOT` を各マシンで設定してから `PIP_CONFIG_FILE` を指定してください。
```bash
export AILAB_ROOT=/path/to/AiLab
export PIP_CONFIG_FILE="$AILAB_ROOT/lab_automation_libs/internal-PyPI/pip.conf.local"
```

CI では `PIP_CONFIG_FILE` 固定ではなく、環境変数で index を注入してください。
```bash
export PIP_INDEX_URL="http://<internal-pypi>/simple"
export PIP_EXTRA_INDEX_URL="https://pypi.org/simple"
export PIP_TRUSTED_HOST="<internal-pypi-host>"
```

## 📚 ドキュメント

| 📖 **目的別ガイド** | 📝 **内容** |
|-------------------|------------|
| **[📖 ユーザーガイド](docs/guide/USER_GUIDE.md)** | 使い方・操作方法・トラブルシューティング |
| **[👨‍💻 開発者ガイド](docs/dev/DEVELOPER_GUIDE.md)** | プラグイン開発・コントリビューション |
| **[🏗️ アーキテクチャ](docs/architecture/ARCHITECTURE.md)** | システム設計・プラグインシステム |
| **[⚡ 技術ノート](docs/architecture/TECHNICAL_NOTES.md)** | UIソリューション・最適化技術 |

## ✨ 主な機能

- **🎯 基本調整**: 明度・コントラスト・彩度
- **🌈 濃度調整**: ガンマ補正・シャドウ・ハイライト
- **🌀 フィルター**: ブラー・シャープ・エッジ検出
- **📊 画像解析**: ヒストグラム・特徴点・品質解析

## 🔧 システム要件

- **Python**: 3.8以上
- **プラットフォーム**: macOS / Windows / Linux
- **メモリ**: 4GB以上推奨

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

- **[開発者ガイド](docs/dev/DEVELOPER_GUIDE.md)** - 開発環境の構築と基本的な開発フロー
- **[設計指針](docs/architecture/DESIGN_PRINCIPLES.md)** - コード修正時の基本方針とベストプラクティス
- **[SmartSliderガイド](docs/dev/SMART_SLIDER_GUIDE.md)** - 統一されたスライダー拡張機能パッケージシステム
- **[アーキテクチャ](docs/architecture/ARCHITECTURE.md)** - システム設計と技術詳細

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) をご覧ください。

---

**🏠 メインハブ** | 各ドキュメントから詳細情報にアクセスできます
