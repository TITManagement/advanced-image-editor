# プラグイン追加・開発ガイド

このドキュメントは、`advanced-image-editor` プロジェクトに新しい画像解析プラグインを追加・開発するための手順と設計方針をまとめたものです。

## 1. プラグイン追加の流れ（概要）

1. `src/plugins/analysis/` ディレクトリに新規プラグインファイル（例: `my_plugin.py`）を作成
2. `ImageProcessorPlugin` を継承したクラスを定義
3. 必要なコールバック・UI生成・解析API・イベントハンドラを実装
4. `main_plugin.py` でプラグインを登録

## 2. 設計方針（抜粋）
- 外部APIはパブリックメソッド（アンダースコアなし）で公開
- 内部処理はプライベートメソッド（先頭に _）で隠蔽
- コールバック設定・UI生成はパブリックAPIで提供
- 画像解析処理・イベントハンドラはプライベートで実装
- 機能単位（例：ガンマ、シャドウ、2値化など）で関連メソッドをグループ化し、追加・削除・保守を容易にする
- セクションごとにコメントで区切り、保守性を高める
- 必要に応じて docstring で設計意図や利用例を明記

## 3. 推奨メソッド並び順（機能単位グループ化例）
1. 初期化・基本情報
2. 機能A（ガンマ補正関連）
    - 例:
        - setup_gamma_ui
        - set_gamma_callback
        - process_gamma
        - _on_gamma_change
        - _on_gamma_mode_change
        - _on_curve_change
    - UI生成、コールバック、API、イベントハンドラ
3. 機能B（シャドウ/ハイライト関連）
    - UI生成、コールバック、API、イベントハンドラ
4. 機能C（色温度関連）
    - ...
5. 機能D（2値化関連）
    - ...
6. 機能E（ヒストグラム均等化関連）
    - ...
7. その他・汎用

## 4. プラグイン登録方法

1. `src/plugins/analysis/` に新規プラグインファイル（例: `my_plugin.py`）を作成
2. `ImageProcessorPlugin` を継承したクラスを定義し、必要なコールバック・UI生成・解析API・イベントハンドラを実装
3. `main_plugin.py` のプラグイン管理リストに新規クラスを追加
4. 必要に応じて以下も行う
    - 関連するUI部品やコールバックの設定
    - `docs/` 配下へのガイドやサンプルの追加
    - 他プラグインとの連携・依存関係の確認

> 補足：追加後は、動作確認・依存関係のチェック・ガイドの更新を推奨します。

## 5. サンプルテンプレート（機能単位グループ化例）
```python
from core.plugin_base import ImageProcessorPlugin

class MyAnalysisPlugin(ImageProcessorPlugin):
    """
    新規画像解析プラグインのサンプル
    機能単位でメソッドをグループ化する設計方針例
    """
    # --- 初期化・基本情報 ---
    def __init__(self, name="my_analysis"):
        super().__init__(name)
        self.image = None
        # ...必要な属性を初期化...

    # --- ガンマ補正関連 ---
    def set_gamma_callback(self, callback):
        self.gamma_callback = callback
    def setup_gamma_ui(self, parent):
        # ...ガンマUI生成...
    def process_gamma(self, image):
        # ...ガンマ処理...
    def _on_gamma_change(self):
        # ...ガンマイベント...

    # --- シャドウ/ハイライト関連 ---
    def set_shadow_callback(self, callback):
        self.shadow_callback = callback
    def setup_shadow_ui(self, parent):
        # ...シャドウUI生成...
    def process_shadow(self, image):
        # ...シャドウ処理...
    def _on_shadow_change(self):
        # ...シャドウイベント...

    # --- 2値化関連 ---
    def set_threshold_callback(self, callback):
        self.threshold_callback = callback
    def setup_threshold_ui(self, parent):
        # ...2値化UI生成...
    def process_threshold(self, image):
        # ...2値化処理...
    def _on_threshold_change(self):
        # ...2値化イベント...

    # --- その他・汎用 ---
    def reset_parameters(self):
        # ...パラメータリセット...
```


## 6. プラグイン削除方法

1. `src/plugins/analysis/` から対象プラグインファイル（例: `my_plugin.py`）を削除
2. `main_plugin.py` のプラグイン管理リストから該当クラスの登録行を削除
3. 必要に応じて `docs/` 配下の関連ガイドやサンプルも削除
4. 他プラグインやUI部品との依存関係がないか確認

> 補足：削除前に必ずバックアップを取得し、影響範囲を確認してください。

## 6. 詳細設計・拡張ノウハウ
- より詳細な設計方針や拡張例は `analysis_plugin.py` のdocstringおよび本ガイドを参照してください。
- 既存プラグインのコード（特に `ImageAnalysisPlugin`）を参考にすると、UI部品やUndoロジックの実装例が分かります。
- プラグインごとに `docs/` 配下へ個別ガイドを追加しても構いません。

## 7. よくある質問（FAQ）
- Q: プラグインのUIをタブで分けたい場合は？
    A: `create_ui` 内で `CTkFrame` などを活用し、セクションごとにUIを分割してください。
- Q: Undoボタンの制御は？
    A: `_enable_undo_button`, `_disable_undo_button` を活用し、各解析ごとに状態管理します。
- Q: コールバックの設計例は？
    A: `set_display_image_callback` などを参考に、外部連携用APIを設計してください。

---

ご不明点や追加ガイドが必要な場合は `README.md` または本ファイルに追記してください。
