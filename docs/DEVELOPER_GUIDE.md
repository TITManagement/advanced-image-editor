# 開発者ガイド - Advanced Image Editor

> 🏠 **メインハブ**: [README](../README.md) へ戻る | **関連ドキュメント**: [ユーザーガイド](USER_GUIDE.md) | [アーキテクチャ](ARCHITECTURE.md) | [技術ノート](TECHNICAL_NOTES.md)

## 目次
- [セットアップ](#セットアップ)
- [自作ライブラリ一覧・設計補足](#プロジェクト内自作ライブラリ一覧・設計補足)
- [プラグイン開発](#プラグイン開発)
- [コントリビューション](#コントリビューション)
- [テスト・ビルド・CI](#テスト・ビルド・CI)

## セットアップ

- Python 3.8以上（3.9以上推奨）
- Git
- 必要な外部ライブラリは `requirements.txt` 参照
- 仮想環境推奨: `python3 -m venv .venv && source .venv/bin/activate`
- インストール: `pip install -e .[dev]`
- 開発ツール: `black`, `flake8`, `pytest` など

## プロジェクト内自作ライブラリ一覧・設計補足

このプロジェクトは、拡張性・保守性・テスタビリティを重視した独自モジュール構成となっています。下記は主要な自作ライブラリとその役割、設計上の依存関係です。

| モジュール | 役割・機能 | 依存関係 |
|-----------|------------|----------|
| `core.plugin_base` | プラグイン基底クラス・管理・UIヘルパー | すべてのプラグイン、main_plugin |
| `core.logging` | 統一ログシステム | 全体（開発・運用） |
| `plugins.basic.basic_plugin` | 明度・コントラスト・彩度調整 | core.plugin_base |
| `plugins.density.density_plugin` | ガンマ補正・シャドウ/ハイライト・色温度 | core.plugin_base, ui.curve_editor |
| `plugins.filters.filters_plugin` | ブラー・シャープ・ノイズ除去・エンボス・エッジ検出 | core.plugin_base |
| `plugins.analysis.analysis_plugin` | ヒストグラム解析・特徴点検出・フーリエ変換 | core.plugin_base |
| `ui.main_window` | メインウィンドウUI | main_plugin |
| `ui.curve_editor` | ガンマ補正カーブエディタ | plugins.density |
| `editor.image_editor` | 画像の読み込み・保存・表示 | main_plugin |
| `utils.image_utils` | 画像変換・フォーマット処理 | plugins, editor |
| `utils.platform_utils` | クロスプラットフォーム対応・ファイルダイアログ | editor, ui |

### 設計・依存関係の観点
- **プラグインアーキテクチャ**：`core.plugin_base`を基底とし、各プラグインはこのクラスを継承。UIヘルパーも共通利用。
- **UI分離設計**：`ui`配下にウィンドウ・カーブエディタ等のUI部品を分離。プラグインは必要に応じてUI部品を利用。
- **ユーティリティ分離**：画像処理・OS依存処理は`utils`配下に集約。各プラグインやエディタから呼び出し。
- **依存関係の流れ**：main_plugin → core/plugin_base → plugins/* → ui/*, utils/*, editor/*
- **外部ライブラリとの関係**：Pillow, OpenCV, CustomTkinter, numpy等は自作モジュール内部でラップ・拡張して利用。

#### 参考：ディレクトリ構造
```
src/
├── core/           # プラグイン基盤・ログ
├── plugins/        # 画像処理プラグイン群
├── editor/         # 画像エディタ
├── ui/             # UI部品
└── utils/          # ユーティリティ
```

## プラグイン開発

- 新規プラグインは `src/plugins/your_plugin/` に配置
- 必須: `ImageProcessorPlugin` を継承し、`get_display_name`, `get_description`, `create_ui`, `process_image` を実装
- UI部品は `PluginUIHelper` で統一
- 主要API:
```python
from core.plugin_base import ImageProcessorPlugin, PluginUIHelper
class YourPlugin(ImageProcessorPlugin):
    def get_display_name(self): ...
    def get_description(self): ...
    def create_ui(self, parent): ...
    def process_image(self, image, **params): ...
```
- 詳細なサンプルやテストは `tests/plugins/` 参照

## コントリビューション

- Issue・Pull RequestはGitHub上で管理
- ブランチ戦略: `feature/`, `bugfix/`, `hotfix/` プレフィックス推奨
- コミットメッセージは Conventional Commits 準拠
- コードスタイル: PEP8, 型ヒント, docstring推奨
- フォーマット: `black`, `isort`, `flake8` で統一

## テスト・ビルド・CI

- テスト: `pytest tests/ -v` で実行
- カバレッジ: `pytest --cov=src --cov-report=html`
- ビルド: `python scripts/build_distribution.py` または `python -m build`
- CI: `.github/workflows/ci.yml` 参照（Pythonバージョンマトリクス、スタイルチェック、テスト）

---

このガイドは中級者以上の開発者向けに、プロジェクトの内部構造・拡張ポイント・運用ルールを簡潔にまとめています。詳細は各ドキュメント・コード・テストケースを参照してください。