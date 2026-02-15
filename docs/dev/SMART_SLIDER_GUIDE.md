````markdown
# SmartSliderシステム - Smart Slider System

## 概要

このドキュメントは、Advanced Image EditorのSmartSliderシステムの使用方法を説明します。SmartSliderは、スライダーの拡張機能（オーバーシュート対策・チャタリング防止）を「常にセットで適用される」統一パッケージです。

### 🎯 SmartSliderの特徴
- **自動オーバーシュート対策**: 値が範囲外に設定されることを自動防止
- **100msデバウンスチャタリング防止**: 高速な値変更時の不要な処理実行を自動抑制
- **後方互換API**: 既存のスライダー作成コードとほぼ同じインターフェース
- **統一された品質**: 全プラグインで一貫したスライダー体験
- **型安全**: int/float両対応の値処理

## SmartSliderの基本使用法

### 1. 基本的なスライダー作成

```python
from utils.smart_slider import SmartSlider

class MyPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
        self._sliders = {}
        self._labels = {}
    
    def create_ui(self, parent):
        # SmartSliderを使用（推奨）
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
    
    def _on_brightness_change(self, value: int):
        """明度変更時のコールバック（オーバーシュート対策・チャタリング防止済み）"""
        self._brightness = value
        # ここで画像処理や他の更新処理を実行
        if self._parameter_change_callback:
            self._parameter_change_callback()
```

### 2. 浮動小数点スライダー

```python
# 浮動小数点値のスライダー
self._sliders['gamma'], self._labels['gamma'] = SmartSlider.create(
    parent=parent,
    text="ガンマ調整",
    from_=0.1,
    to=3.0,
    default_value=1.0,
    command=self._on_gamma_change,
    value_format="{:.1f}",
    value_type=float
)
```

### 3. 完全なプラグイン実装例

```python
from utils.smart_slider import SmartSlider
from core.plugin_base import ImageProcessorPlugin, PluginUIHelper

class SmartSliderExamplePlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("smart_example", "1.0.0")
        
        # パラメータ値
        self._brightness = 0
        self._contrast = 0
        self._saturation = 0
        
        # UI要素管理
        self._sliders = {}
        self._labels = {}
        self._buttons = {}
    
    def create_ui(self, parent):
        """SmartSliderを使用したUI作成"""
        
        # 明度調整
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
        
        # コントラスト調整
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
        
        # 彩度調整
        self._sliders['saturation'], self._labels['saturation'] = SmartSlider.create(
            parent=parent,
            text="彩度調整",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_saturation_change,
            value_format="{:.0f}",
            value_type=int
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent,
            text="全リセット",
            command=self.reset_parameters
        )
    
    def _on_brightness_change(self, value: int):
        """明度変更（SmartSlider自動対策済み）"""
        self._brightness = value
        self._on_parameter_change()
    
    def _on_contrast_change(self, value: int):
        """コントラスト変更（SmartSlider自動対策済み）"""
        self._contrast = value
        self._on_parameter_change()
    
    def _on_saturation_change(self, value: int):
        """彩度変更（SmartSlider自動対策済み）"""
        self._saturation = value
        self._on_parameter_change()
    
    def reset_parameters(self):
        """パラメータリセット"""
        # パラメータ値をリセット
        self._brightness = 0
        self._contrast = 0
        self._saturation = 0
        
        # スライダーをリセット（SmartSliderが自動でラベル更新）
        for param in ['brightness', 'contrast', 'saturation']:
            if param in self._sliders:
                self._sliders[param].set(0)
        
        # 画像更新
        self._on_parameter_change()
    
    def _on_parameter_change(self):
        """パラメータ変更時の処理（SmartSliderがチャタリング防止済み）"""
        if self._parameter_change_callback:
            self._parameter_change_callback()
```

## SmartSlider.create()パラメータ詳細

### 必須パラメータ
- `parent`: スライダーを配置する親ウィジェット
- `text`: スライダーのラベルテキスト
- `from_`: スライダーの最小値
- `to`: スライダーの最大値
- `command`: 値変更時のコールバック関数

### オプションパラメータ
- `default_value`: 初期値（デフォルト: 0）
- `value_format`: 値の表示フォーマット（デフォルト: "{:.0f}"）
- `value_type`: 値の型（int または float、デフォルト: int）

### 使用例
```python
# 整数スライダー
slider, label = SmartSlider.create(
    parent=parent,
    text="整数値",
    from_=-50,
    to=50,
    default_value=0,
    command=callback,
    value_format="{:.0f}",  # 整数表示
    value_type=int
)

# 浮動小数点スライダー
slider, label = SmartSlider.create(
    parent=parent,
    text="小数値",
    from_=0.0,
    to=2.0,
    default_value=1.0,
    command=callback,
    value_format="{:.2f}",  # 小数点2桁表示
    value_type=float
)
```

## 既存コードからの移行

### Before（従来のスライダー）

```python
def create_ui(self, parent):
    # 従来の複雑な方法
    self._sliders['brightness'], self._labels['brightness'] = \
        PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="明度",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_brightness_change,
            value_format="{:.0f}"
        )

def _on_brightness_change(self, value: float):
    # 手動オーバーシュート対策が必要
    clamped_value = max(-100, min(100, int(round(value))))
    self._brightness = clamped_value
    self._update_value_label('brightness', clamped_value)
    
    # 手動チャタリング対策が必要
    if self._update_timer:
        self._update_timer.cancel()
    self._update_timer = threading.Timer(0.1, self._delayed_update)
    self._update_timer.start()
```

### After（SmartSlider）

```python
def create_ui(self, parent):
    # SmartSliderでシンプルに
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

def _on_brightness_change(self, value: int):
    # オーバーシュート対策・チャタリング防止は自動処理済み
    self._brightness = value
    if self._parameter_change_callback:
        self._parameter_change_callback()
```

## SmartSliderの内部動作

### 自動オーバーシュート対策
```python
def _safe_callback(self, raw_value):
    """内部で自動実行される安全なコールバック"""
    # 値を指定範囲内に自動制限
    safe_value = max(self.from_, min(self.to, raw_value))
    
    # 型変換
    if self.value_type == int:
        safe_value = int(round(safe_value))
    else:
        safe_value = float(safe_value)
    
    # ラベル自動更新
    self.label.configure(text=self.value_format.format(safe_value))
    
    # ユーザーコールバック実行（安全な値で）
    self.user_callback(safe_value)
```

### 自動チャタリング防止
```python
def _debounced_callback(self, value):
    """100msデバウンス処理"""
    # 既存タイマーをキャンセル
    if self._timer:
        self._timer.cancel()
    
    # 新しいタイマーで100ms後に実行
    self._timer = threading.Timer(0.1, self._safe_callback, (value,))
    self._timer.start()
```

## ベストプラクティス

### 1. 一貫したvalue_type指定
```python
# 整数パラメータには必ずint指定
SmartSlider.create(..., value_type=int)

# 浮動小数点パラメータには必ずfloat指定
SmartSlider.create(..., value_type=float)
```

### 2. 適切なvalue_format
```python
# 整数値用
value_format="{:.0f}"

# 小数点1桁用
value_format="{:.1f}"

# 小数点2桁用
value_format="{:.2f}"
```

### 3. スライダーのリセット
```python
def reset_parameters(self):
    """推奨リセット方法"""
    # パラメータ値をリセット
    self._brightness = 0
    
    # スライダーもリセット（SmartSliderが自動でラベル更新）
    if 'brightness' in self._sliders:
        self._sliders['brightness'].set(0)
```

### 4. エラーハンドリング
```python
def _on_brightness_change(self, value: int):
    """エラーに強いコールバック"""
    try:
        self._brightness = value
        self._on_parameter_change()
    except Exception as e:
        print(f"明度変更エラー: {e}")
        # SmartSliderが既に安全な値を保証しているため、
        # 基本的にエラーは発生しない
```

## トラブルシューティング

### Q: 値が期待した範囲外になる
**A**: SmartSliderが自動で範囲制限するため、この問題は発生しません。

### Q: スライダー操作でCPU使用率が高い
**A**: SmartSliderが自動で100msデバウンスするため、この問題は発生しません。

### Q: 既存コードとの互換性
**A**: SmartSlider.create()は既存のcreate_slider_with_label()とほぼ同じAPIです。

### Q: カスタムデバウンス時間を設定したい
**A**: 現在の実装では100ms固定です。必要に応じてSmartSliderクラスを拡張してください。

## 現在の使用状況

### 実装済みプラグイン
- ✅ **basic_plugin**: brightness, contrast, saturation (3スライダー)
- ✅ **density_plugin**: shadow, highlight, temperature, threshold (4スライダー)
- ✅ **filters_plugin**: blur, sharpen, kernel (3スライダー)

### 全プラグインでの統一品質
- 自動オーバーシュート対策
- 自動チャタリング防止
- 一貫したUI体験
- 後方互換性維持

---

**最終更新**: 2025年10月5日  
**バージョン**: 2.0.0 (SmartSlider統合版)
````