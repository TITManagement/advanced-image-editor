# ライブラリガイド - Advanced Image Editor

このドキュメントは、プロジェクト内で利用されている自作ライブラリ（内部モジュール）の構成・役割・利用方法・依存関係を詳細にまとめたものです。

---

## 目次
- 概要
- ディレクトリ構造
- 主要ライブラリ一覧と役割
- インポート例
- 依存関係・設計方針
- よくある質問

---

## 概要

Advanced Image Editorは、拡張性・保守性・テスタビリティを重視したモジュラー設計です。各機能は独立した自作ライブラリ（Pythonモジュール）として`src/`配下に実装されています。

---

## ディレクトリ構造

```
src/
├── core/           # プラグイン基盤・ログ
├── plugins/        # 画像処理プラグイン群
├── editor/         # 画像エディタ
├── ui/             # UI部品
└── utils/          # ユーティリティ
```

---

## 主要ライブラリ一覧と役割

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

---

## インポート例

各ライブラリは、Pythonのimport文でパッケージ階層に従って利用します。

```python
# コア基盤
from core.plugin_base import ImageProcessorPlugin, PluginManager, PluginUIHelper
from core.logging import LogLevel, set_log_level, debug_print

# プラグイン
from plugins.basic import BasicAdjustmentPlugin
from plugins.density import DensityAdjustmentPlugin
from plugins.filters import FilterProcessingPlugin
from plugins.analysis import ImageAnalysisPlugin

# UI部品
from ui.main_window import MainWindowUI
from ui.curve_editor import CurveEditor

# エディタ
from editor.image_editor import ImageEditor

# ユーティリティ
from utils.image_utils import ImageUtils
from utils.platform_utils import PlatformManager
```

---

## 依存関係・設計方針

- **プラグインアーキテクチャ**：`core.plugin_base`を基底とし、各プラグインはこのクラスを継承。UIヘルパーも共通利用。
- **UI分離設計**：`ui`配下にウィンドウ・カーブエディタ等のUI部品を分離。プラグインは必要に応じてUI部品を利用。
- **ユーティリティ分離**：画像処理・OS依存処理は`utils`配下に集約。各プラグインやエディタから呼び出し。
- **依存関係の流れ**：main_plugin → core/plugin_base → plugins/* → ui/*, utils/*, editor/*
- **外部ライブラリとの関係**：Pillow, OpenCV, CustomTkinter, numpy等は自作モジュール内部でラップ・拡張して利用。

---

## よくある質問

### Q. importでModuleNotFoundErrorが出る場合は？
A. プロジェクトルート（src/の親）をカレントディレクトリにして実行してください。必要に応じて`PYTHONPATH`に`src/`を追加。

### Q. 外部ライブラリとの違いは？
A. 画像処理・UI・OS依存処理などの基礎部分は外部ライブラリ（Pillow, OpenCV, CustomTkinter等）を利用し、プロジェクト独自の拡張・統合部分は自作ライブラリで実装しています。

### Q. プラグイン追加時の推奨構成は？
A. `src/plugins/your_plugin/`に新規ディレクトリを作成し、`ImageProcessorPlugin`を継承したクラスを実装してください。

---

このガイドを参考に、プロジェクト内の自作ライブラリの構造・利用方法・拡張ポイントを把握してください。
