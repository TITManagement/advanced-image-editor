# Advanced Image Editor

> プラグインシステム対応の高度な画像編集アプリケーション

**リアルタイム画像処理** | **4つの専門プラグイン** | **モジュラー設計** | **クロスプラットフォーム**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](https://github.com/TITManagement/advanced-image-editor)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## � クイックスタート

### 1. インストール

```bash
# リポジトリをクローン
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor

# 自動セットアップ（推奨）
python scripts/setup_dev_environment.py

# または手動セットアップ
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. 実行

```bash
# 基本実行
.venv/bin/python src/main_plugin.py

# デバッグモード
.venv/bin/python src/main_plugin.py --debug
```

### 3. 基本的な使い方

1. **画像を開く**: 左上の「画像を開く」ボタン
2. **調整**: 4つのプラグインタブで画像を編集
3. **保存**: 「画像を保存」ボタンで結果を保存

## 📁 プロジェクト構造

```
src/
├── core/           # プラグインシステム中核
├── plugins/        # 4つの専門プラグイン
├── editor/         # 画像編集エンジン
├── ui/             # ユーザーインターフェース
└── utils/          # ユーティリティ
```

## 🎯 利用可能な機能

### 基本調整プラグイン
- 明度・コントラスト・彩度調整 (-100〜+100)

### 濃度調整プラグイン  
- ガンマ補正 (0.1〜3.0)
- シャドウ/ハイライト調整
- 2値化・ヒストグラム均等化

### フィルター処理プラグイン
- ガウシアンブラー・シャープニング
- ノイズ除去・エッジ検出・エンボス

### 画像解析プラグイン
- ヒストグラム解析・特徴点検出
- フーリエ変換・品質解析

## 📚 詳細ドキュメント

| ドキュメント | 内容 |
|-------------|------|
| **[📖 ユーザーガイド](docs/USER_GUIDE.md)** | 詳細な使い方・操作方法・トラブルシューティング |
| **[👨‍💻 開発者ガイド](docs/DEVELOPER_GUIDE.md)** | プラグイン開発・コントリビューション方法 |
| **[🏗️ アーキテクチャ](docs/ARCHITECTURE.md)** | システム設計・プラグインシステム詳細 |
| **[⚡ 技術ノート](docs/TECHNICAL_NOTES.md)** | UIソリューション・パフォーマンス最適化 |

## 🔧 システム要件

- **Python**: 3.8以上（3.9以上推奨）
- **プラットフォーム**: macOS 10.14+ / Windows 10+ / Linux (Ubuntu 18.04+)
- **メモリ**: 4GB以上推奨
- **依存関係**: OpenCV, Pillow, CustomTkinter, NumPy

## 🤝 コントリビューション

プロジェクトへの貢献を歓迎します！

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. プルリクエストを作成

詳細は [開発者ガイド](docs/DEVELOPER_GUIDE.md) をご覧ください。

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。詳細は [LICENSE](LICENSE) ファイルをご覧ください。

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/TITManagement/advanced-image-editor/issues)
- **Documentation**: [docs/](docs/)
- **Wiki**: [プロジェクトWiki](https://github.com/TITManagement/advanced-image-editor/wiki)

---

**作成者**: TIT Management  
**バージョン**: Plugin System 1.0.0  
**最終更新**: 2025年9月19日
