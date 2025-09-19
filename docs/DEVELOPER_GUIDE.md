# 開発者ガイド - Advanced Image Editor

> 🏠 **メインハブ**: [README](../README.md) へ戻る | **関連ドキュメント**: [ユーザーガイド](USER_GUIDE.md) | [アーキテクチャ](ARCHITECTURE.md) | [技術ノート](TECHNICAL_NOTES.md)

## 目次
- [開発環境のセットアップ](#開発環境のセットアップ)
- [プラグイン開発](#プラグイン開発)
- [コントリビューション](#コントリビューション)
- [テスト](#テスト)
- [ビルドとデプロイ](#ビルドとデプロイ)

## 開発環境のセットアップ

### 前提条件

#### システム要件
- **Python**: 3.8以上（3.9以上推奨）
- **Git**: バージョン管理
- **外部依存関係**: `gui_framework`ライブラリ

#### 外部ライブラリの配置

`gui_framework`を以下のいずれかの場所に配置：
```
../../lib/gui_framework    # 推奨
../lib/gui_framework       # 代替1
./lib/gui_framework        # 代替2
```

### 自動セットアップ（推奨）

```bash
# リポジトリクローン
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor

# 自動セットアップ実行
python scripts/setup_dev_environment.py
```

### 手動セットアップ

#### 1. 仮想環境作成

```bash
# 仮想環境作成
python3 -m venv .venv

# アクティベート（macOS/Linux）
source .venv/bin/activate

# アクティベート（Windows）
.venv\Scripts\activate
```

#### 2. 開発用依存関係インストール

```bash
# 開発用フル機能インストール
pip install -e .[dev]

# または基本インストール
pip install -e .

# または従来方式
pip install -r requirements.txt
```

#### 3. 開発ツールの確認

```bash
# コードフォーマット
black --check src/
flake8 src/

# テストの実行
python -m pytest tests/ -v
```

## プラグイン開発

### プラグイン開発の基本フロー

1. **プラグイン設計**: 機能要件と入出力の定義
2. **ディレクトリ作成**: `src/plugins/your_plugin/`
3. **基底クラス継承**: `ImageProcessorPlugin`を継承
4. **UI実装**: `create_ui()`メソッドの実装
5. **画像処理実装**: `process_image()`メソッドの実装
6. **テスト作成**: 単体テストの実装
7. **統合**: メインアプリへの登録

### 新規プラグインテンプレート

#### ディレクトリ構造
```bash
mkdir src/plugins/your_plugin_name
cd src/plugins/your_plugin_name
```

#### プラグインクラスの実装

**ファイル**: `your_plugin_name_plugin.py`

```python
from core.plugin_base import ImageProcessorPlugin, PluginUIHelper
import customtkinter as ctk
from PIL import Image
import numpy as np
import cv2
from core.logging import logger

class YourPluginNamePlugin(ImageProcessorPlugin):
    """
    あなたのプラグインの説明をここに記載
    
    機能:
    - 機能1の説明
    - 機能2の説明
    - 機能3の説明
    """
    
    def __init__(self):
        super().__init__("your_plugin_name", "1.0.0")
        
        # パラメータの初期化
        self.param1_value = 0
        self.param2_value = 50
        self.param3_enabled = False
        
        # UI要素の参照保持用
        self._sliders = {}
        self._labels = {}
        self._buttons = {}
        
        logger.info(f"プラグイン {self.get_display_name()} を初期化しました")
    
    def get_display_name(self) -> str:
        """UI上に表示されるプラグイン名"""
        return "あなたのプラグイン"
    
    def get_description(self) -> str:
        """プラグインの機能説明"""
        return "このプラグインの機能説明をここに記載します"
    
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """
        プラグインのUI要素を作成
        
        Args:
            parent: UI要素を配置する親フレーム
        """
        # パラメータ1: スライダー
        self._sliders['param1'], self._labels['param1'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="パラメータ1",
            from_=-100,
            to=100,
            default_value=0,
            command=self._on_param1_change,
            value_format="{:.0f}"
        )
        
        # パラメータ2: スライダー（浮動小数点）
        self._sliders['param2'], self._labels['param2'] = PluginUIHelper.create_slider_with_label(
            parent=parent,
            text="パラメータ2",
            from_=0.0,
            to=100.0,
            default_value=50.0,
            command=self._on_param2_change,
            value_format="{:.1f}"
        )
        
        # 処理実行ボタン
        self._buttons['process'] = PluginUIHelper.create_button(
            parent=parent,
            text="特殊処理実行",
            command=self._on_special_process,
            width=150
        )
        
        # リセットボタン
        self._buttons['reset'] = PluginUIHelper.create_button(
            parent=parent,
            text="リセット",
            command=self.reset_parameters,
            width=100
        )
        
        logger.debug(f"{self.get_display_name()}: UI作成完了")
    
    def _on_param1_change(self, value: float) -> None:
        """パラメータ1変更時の処理"""
        try:
            self.param1_value = int(value)
            logger.debug(f"{self.get_display_name()}: パラメータ1 = {self.param1_value}")
            self._on_parameter_change()
        except Exception as e:
            logger.error(f"パラメータ1変更エラー: {e}")
    
    def _on_param2_change(self, value: float) -> None:
        """パラメータ2変更時の処理"""
        try:
            self.param2_value = float(value)
            logger.debug(f"{self.get_display_name()}: パラメータ2 = {self.param2_value}")
            self._on_parameter_change()
        except Exception as e:
            logger.error(f"パラメータ2変更エラー: {e}")
    
    def _on_special_process(self) -> None:
        """特殊処理実行"""
        try:
            self.param3_enabled = True
            logger.info(f"{self.get_display_name()}: 特殊処理を実行")
            self._on_parameter_change()
        except Exception as e:
            logger.error(f"特殊処理エラー: {e}")
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """
        画像処理の実行
        
        Args:
            image: 処理対象画像
            **params: 追加パラメータ
            
        Returns:
            処理済み画像
        """
        try:
            # PIL -> OpenCV変換
            image_array = np.array(image)
            if len(image_array.shape) == 3:
                image_cv = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_cv = image_array
            
            # パラメータ1による処理例：明度調整
            if self.param1_value != 0:
                image_cv = self._adjust_brightness(image_cv, self.param1_value)
            
            # パラメータ2による処理例：ブラー
            if self.param2_value > 0:
                kernel_size = int(self.param2_value / 10) * 2 + 1  # 奇数にする
                image_cv = cv2.GaussianBlur(image_cv, (kernel_size, kernel_size), 0)
            
            # 特殊処理例：エッジ検出
            if self.param3_enabled:
                image_cv = self._apply_edge_detection(image_cv)
                self.param3_enabled = False  # 一度だけ実行
            
            # OpenCV -> PIL変換
            if len(image_cv.shape) == 3:
                image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image_cv
            
            result_image = Image.fromarray(image_rgb)
            
            logger.debug(f"{self.get_display_name()}: 画像処理完了")
            return result_image
            
        except Exception as e:
            logger.error(f"{self.get_display_name()}: 画像処理エラー: {e}")
            return image  # エラー時は元画像を返す
    
    def _adjust_brightness(self, image: np.ndarray, brightness: int) -> np.ndarray:
        """明度調整処理"""
        return cv2.add(image, np.ones(image.shape, dtype=np.uint8) * brightness)
    
    def _apply_edge_detection(self, image: np.ndarray) -> np.ndarray:
        """エッジ検出処理"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    def get_parameters(self) -> dict:
        """現在のパラメータを取得"""
        return {
            'param1_value': self.param1_value,
            'param2_value': self.param2_value,
            'param3_enabled': self.param3_enabled
        }
    
    def reset_parameters(self) -> None:
        """パラメータをリセット"""
        self.param1_value = 0
        self.param2_value = 50.0
        self.param3_enabled = False
        
        # UI要素の更新
        if 'param1' in self._sliders:
            self._sliders['param1'].set(0)
        if 'param2' in self._sliders:
            self._sliders['param2'].set(50.0)
        
        logger.info(f"{self.get_display_name()}: パラメータをリセットしました")
        self._on_parameter_change()
```

#### __init__.pyファイル

**ファイル**: `__init__.py`

```python
from .your_plugin_name_plugin import YourPluginNamePlugin

__all__ = ['YourPluginNamePlugin']
```

### プラグインのメインアプリへの統合

**ファイル**: `src/main_plugin.py`の修正

```python
# インポート追加
from plugins.your_plugin_name import YourPluginNamePlugin

class AdvancedImageEditor:
    def setup_plugins(self):
        """プラグインの初期化と登録"""
        # 既存のプラグイン...
        
        # 新しいプラグインを追加
        your_plugin = YourPluginNamePlugin()
        your_plugin.set_parameter_change_callback(self.on_plugin_parameter_change)
        self.plugin_manager.register_plugin(your_plugin)
        
        logger.info("すべてのプラグインを登録しました")
    
    def create_plugin_tabs(self, tabview: ctk.CTkTabview):
        """プラグインタブの作成"""
        plugin_tabs = {
            "basic_adjustment": "基本調整",
            "density_adjustment": "濃度調整", 
            "filter_processing": "フィルター",
            "image_analysis": "画像解析",
            "your_plugin_name": "あなたのプラグイン"  # 追加
        }
        
        # 既存の実装...
```

### 高度なプラグイン機能

#### カスタムUI要素の作成

```python
def create_advanced_ui(self, parent: ctk.CTkFrame):
    """より複雑なUI要素の作成例"""
    
    # フレームによるセクション分け
    section_frame = ctk.CTkFrame(parent)
    section_frame.pack(fill="x", padx=5, pady=5)
    
    # セクションタイトル
    title_label = ctk.CTkLabel(section_frame, text="高度な設定", font=("Arial", 14, "bold"))
    title_label.pack(pady=(10, 5))
    
    # チェックボックス
    self.enable_advanced = ctk.CTkCheckBox(
        section_frame,
        text="高度な処理を有効化",
        command=self._on_advanced_toggle
    )
    self.enable_advanced.pack(pady=5)
    
    # オプションメニュー
    self.processing_mode = ctk.CTkOptionMenu(
        section_frame,
        values=["モード1", "モード2", "モード3"],
        command=self._on_mode_change
    )
    self.processing_mode.pack(pady=5)
    
    # プログレスバー
    self.progress_bar = ctk.CTkProgressBar(section_frame)
    self.progress_bar.pack(fill="x", padx=10, pady=5)
    self.progress_bar.set(0)
```

#### 非同期処理の実装

```python
import threading
from typing import Callable

def process_image_async(self, image: Image.Image, callback: Callable) -> None:
    """重い処理を非同期で実行"""
    
    def _process():
        try:
            # 重い画像処理
            result = self._heavy_processing(image)
            # メインスレッドでコールバック実行
            self.root.after(0, lambda: callback(result))
        except Exception as e:
            logger.error(f"非同期処理エラー: {e}")
            self.root.after(0, lambda: callback(image))  # エラー時は元画像
    
    # バックグラウンドスレッドで実行
    thread = threading.Thread(target=_process)
    thread.daemon = True
    thread.start()
```

### プラグインAPI詳細

#### 必須実装メソッド

| メソッド | 戻り値型 | 説明 |
|----------|----------|------|
| `get_display_name()` | `str` | UI表示用プラグイン名 |
| `get_description()` | `str` | プラグインの説明文 |
| `create_ui(parent)` | `None` | UI要素の作成 |
| `process_image(image, **params)` | `Image.Image` | 画像処理の実行 |

#### オプション実装メソッド

| メソッド | 戻り値型 | 説明 |
|----------|----------|------|
| `get_parameters()` | `dict` | 現在のパラメータ取得 |
| `reset_parameters()` | `None` | パラメータリセット |
| `get_version()` | `str` | プラグインバージョン |
| `validate_image(image)` | `bool` | 画像の前処理チェック |

#### ヘルパークラス利用

```python
from core.plugin_base import PluginUIHelper

# スライダーの作成
slider, label = PluginUIHelper.create_slider_with_label(
    parent=parent,
    text="パラメータ名",
    from_=0,
    to=100,
    default_value=50,
    command=callback_function,
    value_format="{:.1f}",  # 小数点1桁表示
    width=200              # スライダー幅
)

# ボタンの作成
button = PluginUIHelper.create_button(
    parent=parent,
    text="実行",
    command=button_callback,
    width=120,
    height=32
)

# ラベルの作成
label = PluginUIHelper.create_label(
    parent=parent,
    text="説明テキスト",
    font=("Arial", 12)
)
```

## テスト

### テスト環境のセットアップ

```bash
# テスト用依存関係インストール
pip install -e .[dev]

# テストディレクトリ作成
mkdir -p tests/plugins/test_your_plugin
```

### プラグインテストの作成

**ファイル**: `tests/plugins/test_your_plugin/test_your_plugin_name.py`

```python
import unittest
from unittest.mock import Mock, patch
from PIL import Image
import numpy as np

# プロジェクトパスを追加
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.plugins.your_plugin_name import YourPluginNamePlugin

class TestYourPluginNamePlugin(unittest.TestCase):
    
    def setUp(self):
        """テスト前の準備"""
        self.plugin = YourPluginNamePlugin()
        
        # テスト用画像作成
        self.test_image = Image.new('RGB', (100, 100), color='white')
    
    def test_plugin_initialization(self):
        """プラグイン初期化のテスト"""
        self.assertEqual(self.plugin.plugin_id, "your_plugin_name")
        self.assertEqual(self.plugin.version, "1.0.0")
        self.assertEqual(self.plugin.param1_value, 0)
        self.assertEqual(self.plugin.param2_value, 50)
    
    def test_display_name(self):
        """表示名のテスト"""
        self.assertEqual(self.plugin.get_display_name(), "あなたのプラグイン")
    
    def test_description(self):
        """説明文のテスト"""
        description = self.plugin.get_description()
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
    
    def test_process_image_no_change(self):
        """パラメータ初期値での画像処理テスト"""
        result = self.plugin.process_image(self.test_image)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.test_image.size)
    
    def test_process_image_with_params(self):
        """パラメータ変更後の画像処理テスト"""
        self.plugin.param1_value = 50
        self.plugin.param2_value = 10
        
        result = self.plugin.process_image(self.test_image)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, self.test_image.size)
    
    def test_parameter_change_callback(self):
        """パラメータ変更コールバックのテスト"""
        callback_mock = Mock()
        self.plugin.set_parameter_change_callback(callback_mock)
        
        self.plugin._on_param1_change(25)
        callback_mock.assert_called_once()
    
    def test_reset_parameters(self):
        """パラメータリセットのテスト"""
        # パラメータを変更
        self.plugin.param1_value = 75
        self.plugin.param2_value = 25
        
        # リセット実行
        self.plugin.reset_parameters()
        
        # 初期値に戻ったか確認
        self.assertEqual(self.plugin.param1_value, 0)
        self.assertEqual(self.plugin.param2_value, 50.0)
    
    def test_get_parameters(self):
        """パラメータ取得のテスト"""
        params = self.plugin.get_parameters()
        
        self.assertIsInstance(params, dict)
        self.assertIn('param1_value', params)
        self.assertIn('param2_value', params)
    
    @patch('customtkinter.CTkFrame')
    def test_create_ui(self, mock_frame):
        """UI作成のテスト"""
        mock_parent = Mock()
        
        # UI作成実行（例外が発生しないことを確認）
        try:
            self.plugin.create_ui(mock_parent)
        except Exception as e:
            self.fail(f"create_ui()で例外が発生: {e}")

if __name__ == '__main__':
    unittest.main()
```

### テストの実行

```bash
# 単体テスト実行
python -m pytest tests/plugins/test_your_plugin/ -v

# 全テスト実行
python -m pytest tests/ -v

# カバレッジ付きテスト
python -m pytest tests/ --cov=src --cov-report=html
```

## コントリビューション

### コントリビューションガイドライン

1. **Issue作成**: バグ報告や機能要求は必ずIssueを作成
2. **ブランチ戦略**: `feature/`、`bugfix/`、`hotfix/`プレフィックス使用
3. **コミットメッセージ**: 従来形式（Conventional Commits）に準拠
4. **プルリクエスト**: テンプレートに従った詳細な説明を記載

### 開発フロー

```bash
# 1. リポジトリをフォーク
# GitHub上でフォークボタンをクリック

# 2. ローカルにクローン
git clone https://github.com/your-username/advanced-image-editor.git
cd advanced-image-editor

# 3. 上流リポジトリを追加
git remote add upstream https://github.com/TITManagement/advanced-image-editor.git

# 4. 開発ブランチ作成
git checkout -b feature/your-feature-name

# 5. 開発・テスト
# ... コード変更 ...

# 6. コミット
git add .
git commit -m "feat: 新機能の追加"

# 7. プッシュ
git push origin feature/your-feature-name

# 8. プルリクエスト作成
# GitHub上でPull Requestを作成
```

### コードスタイル

#### フォーマット

```bash
# Black（コードフォーマッター）
black src/ tests/

# isort（import文ソート）
isort src/ tests/

# flake8（コード品質チェック）
flake8 src/ tests/
```

#### 推奨コーディング規約

- **PEP 8**準拠
- **型ヒント**の使用推奨
- **docstring**の記載（Google style）
- **変数名**は英語（UI表示は日本語可）

#### サンプルコード規約

```python
from typing import Optional, Dict, Any
from PIL import Image

class ExamplePlugin(ImageProcessorPlugin):
    """
    プラグインの例クラス
    
    このクラスは画像処理プラグインの実装例を示します。
    新しいプラグインを作成する際の参考にしてください。
    
    Attributes:
        parameter_value (int): 主要パラメータの値
        is_enabled (bool): プラグインの有効/無効状態
    """
    
    def __init__(self) -> None:
        """プラグインの初期化"""
        super().__init__("example_plugin", "1.0.0")
        self.parameter_value: int = 0
        self.is_enabled: bool = True
    
    def process_image(self, image: Image.Image, **params: Any) -> Image.Image:
        """
        画像処理を実行
        
        Args:
            image: 処理対象の画像
            **params: 追加パラメータ
            
        Returns:
            処理済みの画像
            
        Raises:
            ValueError: 無効な画像が渡された場合
        """
        if not isinstance(image, Image.Image):
            raise ValueError("無効な画像オブジェクトです")
        
        # 処理実装
        return image
```

## ビルドとデプロイ

### ビルドスクリプト

```bash
# ビルドスクリプト実行
python scripts/build_distribution.py

# 生成物確認
ls dist/
```

### パッケージ化

```bash
# pyproject.tomlを使用したビルド
python -m build

# wheelパッケージ作成
python setup.py bdist_wheel

# ソース配布パッケージ作成
python setup.py sdist
```

### 継続的インテグレーション

`.github/workflows/ci.yml`の例：

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev]
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --cov=src
    
    - name: Check code style
      run: |
        black --check src/ tests/
        flake8 src/ tests/
```

---

このガイドに従って、高品質なプラグインを開発し、Advanced Image Editorプロジェクトに貢献してください！

**ナビゲーション**:
- 🏠 [メインハブに戻る](../README.md)
- 📖 [ユーザー機能を理解する](USER_GUIDE.md)
- 🏗️ [システム設計を深く学ぶ](ARCHITECTURE.md)
- ⚡ [技術的な課題と解決策](TECHNICAL_NOTES.md)