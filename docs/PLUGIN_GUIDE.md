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

## 5. SmartSlider対応プラグインテンプレート

### 基本的なSmartSlider使用例
```python
from core.plugin_base import ImageProcessorPlugin, PluginUIHelper
from utils.smart_slider import SmartSlider

class MySmartPlugin(ImageProcessorPlugin):
    """
    SmartSliderを使用した新規プラグインのサンプル
    """
    
    def __init__(self, plugin_id="my_smart_plugin", version="1.0.0"):
        super().__init__(plugin_id, version)
        
        # パラメータ値
        self._brightness = 0
        self._contrast = 0
        
        # UI要素管理
        self._sliders = {}
        self._labels = {}
        self._buttons = {}
        
        # コールバック
        self._parameter_change_callback = None
    
    def get_display_name(self) -> str:
        return "スマートプラグイン"
    
    def get_description(self) -> str:
        return "SmartSliderを使用したサンプルプラグイン"
    
    def set_parameter_change_callback(self, callback):
        """パラメータ変更コールバックの設定"""
        self._parameter_change_callback = callback
    
    def create_ui(self, parent):
        """SmartSliderを使用したUI作成"""
        
        # 明度調整スライダー（SmartSlider使用）
        self._sliders['brightness'], self._labels['brightness'] = SmartSlider.create(
            parent=parent,
            text="明度調整",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_brightness_change,
            value_format="{:.0f}",
            value_type=int
        )
        
        # コントラスト調整スライダー（SmartSlider使用）
        self._sliders['contrast'], self._labels['contrast'] = SmartSlider.create(
            parent=parent,
            text="コントラスト調整",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_contrast_change,
            value_format="{:.0f}",
            value_type=int
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent,
            text="パラメータリセット",
            command=self.reset_parameters
        )
    
    def _on_brightness_change(self, value: int):
        """明度変更時のコールバック（SmartSlider自動対策済み）"""
        self._brightness = value
        self._on_parameter_change()
    
    def _on_contrast_change(self, value: int):
        """コントラスト変更時のコールバック（SmartSlider自動対策済み）"""
        self._contrast = value
        self._on_parameter_change()
    
    def _on_parameter_change(self):
        """パラメータ変更時の共通処理"""
        if self._parameter_change_callback:
            self._parameter_change_callback()
    
    def process_image(self, image):
        """画像処理メソッド"""
        # ここで実際の画像処理を実装
        processed_image = image.copy()
        # ... 明度・コントラスト処理 ...
        return processed_image
    
    def reset_parameters(self):
        """パラメータリセット"""
        self._brightness = 0
        self._contrast = 0
        
        # スライダーをリセット（SmartSliderが自動でラベル更新）
        for param in ['brightness', 'contrast']:
            if param in self._sliders:
                self._sliders[param].set(0)
        
        self._on_parameter_change()
    
    def get_parameters(self):
        """現在のパラメータを取得"""
        return {
            'brightness': self._brightness,
            'contrast': self._contrast
        }
```

### 複数機能プラグインの例
```python
class MultiFeaturePlugin(ImageProcessorPlugin):
    """
    複数機能を持つプラグインのサンプル（機能単位グループ化）
    """
    
    def __init__(self):
        super().__init__("multi_feature", "1.0.0")
        self._sliders = {}
        self._labels = {}
        self._buttons = {}
    
    def create_ui(self, parent):
        """機能単位でUIを構成"""
        
        # --- 基本調整セクション ---
        basic_frame = ctk.CTkFrame(parent)
        basic_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(basic_frame, text="基本調整", font=("Arial", 12, "bold")).pack(anchor="w")
        
        self._create_basic_adjustment_ui(basic_frame)
        
        # --- フィルターセクション ---
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(filter_frame, text="フィルター", font=("Arial", 12, "bold")).pack(anchor="w")
        
        self._create_filter_ui(filter_frame)
    
    def _create_basic_adjustment_ui(self, parent):
        """基本調整UI（SmartSlider使用）"""
        self._sliders['brightness'], self._labels['brightness'] = SmartSlider.create(
            parent=parent,
            text="明度",
            from_=-100, to=100, default_value=0,
            command=self._on_brightness_change,
            value_type=int
        )
        
        self._sliders['contrast'], self._labels['contrast'] = SmartSlider.create(
            parent=parent,
            text="コントラスト",
            from_=-100, to=100, default_value=0,
            command=self._on_contrast_change,
            value_type=int
        )
    
    def _create_filter_ui(self, parent):
        """フィルターUI（SmartSlider使用）"""
        self._sliders['blur'], self._labels['blur'] = SmartSlider.create(
            parent=parent,
            text="ブラー強度",
            from_=0, to=20, default_value=0,
            command=self._on_blur_change,
            value_type=int
        )
        
        self._sliders['sharpen'], self._labels['sharpen'] = SmartSlider.create(
            parent=parent,
            text="シャープネス",
            from_=0.0, to=5.0, default_value=0.0,
            command=self._on_sharpen_change,
            value_format="{:.1f}",
            value_type=float
        )
    
    # --- イベントハンドラー（SmartSlider自動対策済み） ---
    def _on_brightness_change(self, value: int):
        self._brightness = value
        self._on_parameter_change()
    
    def _on_contrast_change(self, value: int):
        self._contrast = value
        self._on_parameter_change()
    
    def _on_blur_change(self, value: int):
        self._blur = value
        self._on_parameter_change()
    
    def _on_sharpen_change(self, value: float):
        self._sharpen = value
        self._on_parameter_change()
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

## 6. SmartSliderのメリットとベストプラクティス

### SmartSliderを使用する理由
- **自動オーバーシュート対策**: 手動で値の範囲チェックを書く必要がない
- **自動チャタリング防止**: 手動でタイマー処理を書く必要がない
- **統一品質**: 全プラグインで一貫したスライダー体験
- **保守性向上**: 複雑な制御コードを書かずに済む

### ベストプラクティス

#### 1. 適切な型指定
```python
# 整数パラメータの場合
SmartSlider.create(..., value_type=int, value_format="{:.0f}")

# 浮動小数点パラメータの場合
SmartSlider.create(..., value_type=float, value_format="{:.1f}")
```

#### 2. 一貫したコールバック設計
```python
def _on_parameter_change(self, value):
    """SmartSliderからのコールバック（安全な値が保証されている）"""
    # 値の検証は不要（SmartSliderが自動実行）
    self._parameter_value = value
    
    # 共通の更新処理
    if self._parameter_change_callback:
        self._parameter_change_callback()
```

#### 3. リセット処理の標準化
```python
def reset_parameters(self):
    """推奨されるリセット処理"""
    # 1. パラメータ値をリセット
    self._brightness = 0
    self._contrast = 0
    
    # 2. スライダーをリセット（SmartSliderが自動でラベル更新）
    for param, default in [('brightness', 0), ('contrast', 0)]:
        if param in self._sliders:
            self._sliders[param].set(default)
    
    # 3. 画像更新
    self._on_parameter_change()
```

### 従来コードからの移行
```python
# 従来の複雑なコード
def _on_old_change(self, value: float):
    # 手動オーバーシュート対策
    clamped = max(-100, min(100, int(round(value))))
    self._param = clamped
    self._update_label('param', clamped)
    
    # 手動チャタリング対策
    if self._timer: self._timer.cancel()
    self._timer = threading.Timer(0.1, self._delayed_update)
    self._timer.start()

# SmartSlider使用のシンプルなコード
def _on_smart_change(self, value: int):
    # オーバーシュート対策・チャタリング防止は自動
    self._param = value
    self._on_parameter_change()
```

## 7. よくある質問（FAQ）

### SmartSlider関連
- **Q: SmartSliderと従来のスライダーの違いは？**
  A: SmartSliderはオーバーシュート対策とチャタリング防止が自動で適用されます。

- **Q: 既存プラグインをSmartSliderに移行するには？**
  A: `PluginUIHelper.create_slider_with_label()`を`SmartSlider.create()`に変更し、手動の制御コードを削除します。

- **Q: カスタムデバウンス時間を設定できますか？**
  A: 現在は100ms固定です。必要に応じてSmartSliderクラスを拡張してください。

### UI設計関連
- **Q: プラグインのUIをタブで分けたい場合は？**
  A: `create_ui` 内で `CTkFrame` などを活用し、セクションごとにUIを分割してください。

- **Q: Undoボタンの制御は？**
  A: `_enable_undo_button`, `_disable_undo_button` を活用し、各解析ごとに状態管理します。

- **Q: コールバックの設計例は？**
  A: `set_display_image_callback` などを参考に、外部連携用APIを設計してください。

### パフォーマンス関連
- **Q: SmartSliderはパフォーマンスに影響しますか？**
  A: むしろパフォーマンスが向上します。チャタリング防止により無駄な処理が削減されます。

---

ご不明点や追加ガイドが必要な場合は `README.md` または本ファイルに追記してください。
