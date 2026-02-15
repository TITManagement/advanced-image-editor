# Advanced Image Editor - Plugin System

プラグインシステム対応版画像編集アプリケーション

## 🎯 概要

プラグインシステムを採用した高度な画像編集アプリケーションです。4つの専門プラグイン（基本調整・濃度調整・フィルター処理・画像解析）により、基本的な画像補正から高度な画像解析まで幅広い機能を提供します。

### ✨ 主要機能
- **🎯 基本調整**: 明度・コントラスト・彩度調整
- **🌈 濃度調整**: ガンマ補正・シャドウ・ハイライト調整  
- **🌀 フィルター**: ブラー・シャープニング・特殊効果
- **🔬 画像解析**: ヒストグラム・特徴点検出・周波数解析

## 🚀 クイックスタート

### インストール
```bash
# リポジトリクローン
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor

# 自動セットアップ
python scripts/setup_dev_environment.py
```

### 実行
```bash
# 基本実行
.venv/bin/python src/advanced_image_editor.py

# デバッグモード  
.venv/bin/python src/advanced_image_editor.py --debug
```

## 📚 ドキュメント

| 📖 ドキュメント | 🎯 対象読者 | 📝 内容 |
|---------------|------------|--------|
| [📱 ユーザーガイド](../guide/USER_GUIDE.md) | エンドユーザー | 機能詳細・操作方法 |
| [👨‍💻 開発者ガイド](../dev/DEVELOPER_GUIDE.md) | プラグイン開発者 | プラグイン作成方法・API |
| [🏗️ アーキテクチャ](../architecture/ARCHITECTURE.md) | 技術評価者 | 設計思想・技術選択 |
| [🔧 技術ノート](../architecture/TECHNICAL_NOTES.md) | 実装者 | UIライブラリ対策・ノウハウ |

## ⚡ 技術スタック

- **Python 3.9+** (Cross-Platform)
- **CustomTkinter** (Modern GUI)
- **OpenCV + Pillow** (Image Processing)

## 🏗️ アーキテクチャ概要

```
🎨 プラグインシステム設計
├── 🔌 core/ - プラグイン基盤
├── 🎯 plugins/ - 4つの専門プラグイン  
├── 🖼️ editor/ - 画像処理エンジン
└── 🎨 ui/ - ユーザーインターフェース
```

## 🤝 貢献

プラグイン開発・機能改善の貢献を歓迎します！
詳細は [👨‍💻 開発者ガイド](../dev/DEVELOPER_GUIDE.md) をご覧ください。

---

**🎉 Advanced Image Editor で、プロ仕様の画像編集をお楽しみください！**
