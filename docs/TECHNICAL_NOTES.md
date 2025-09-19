# 技術ノート - Advanced Image Editor

> 🏠 **メインハブ**: [README](../README.md) へ戻る | **関連ドキュメント**: [ユーザーガイド](USER_GUIDE.md) | [開発者ガイド](DEVELOPER_GUIDE.md) | [アーキテクチャ](ARCHITECTURE.md)

## 目次
- [UIソリューション](#UIソリューション)
- [パフォーマンス最適化](#パフォーマンス最適化)
- [クロスプラットフォーム対応](#クロスプラットフォーム対応)
- [メモリ管理](#メモリ管理)
- [エラーハンドリング](#エラーハンドリング)
- [ログシステム](#ログシステム)

## UIソリューション

### CustomTkinterスライダー問題と解決策

リアルタイム画像処理アプリケーションにおいて、CustomTkinterスライダーの特有の問題を解決しました。

#### 🔧 **解決した技術的問題**

##### 1. 二重コールバック問題
**問題**: スライダーのドラッグ操作中に、値変更コールバックが期待以上に頻繁に呼び出される
```python
# 問題のあるコード例
def create_slider(self, parent, command):
    slider = ctk.CTkSlider(parent, command=command)
    # ドラッグ中に command が異常な頻度で呼び出される
```

**解決策**: 統一コールバックシステムと範囲値チェック
```python
def create_slider_with_label(self, parent, text, from_, to, default_value, command, value_format="{:.0f}"):
    """統一スライダー作成メソッド（問題解決済み）"""
    
    def slider_command(value):
        # 範囲値チェックによる値正規化
        normalized_value = max(from_, min(to, float(value)))
        
        # ラベル更新
        value_label.configure(text=value_format.format(normalized_value))
        
        # 統一コールバック実行
        command(normalized_value)
    
    def on_mouse_release(event):
        """マウスリリース時の明示的処理"""
        current_value = slider.get()
        normalized_value = max(from_, min(to, float(current_value)))
        command(normalized_value)
    
    # スライダー作成
    slider = ctk.CTkSlider(
        parent,
        from_=from_,
        to=to,
        command=slider_command
    )
    slider.set(default_value)
    
    # マウスリリースイベントの明示的バインド
    slider.bind("<ButtonRelease-1>", on_mouse_release)
    
    return slider, value_label
```

##### 2. 値オーバーシュート問題
**問題**: ドラッグ操作中にスライダーの値が設定範囲を超える値を渡すことがある

**解決策**: 確実な範囲チェッククランプ処理
```python
def safe_value_clamp(value: float, min_val: float, max_val: float) -> float:
    """
    値の安全な範囲制限
    
    Args:
        value: チェック対象の値
        min_val: 最小値
        max_val: 最大値
    
    Returns:
        範囲内に制限された値
    """
    return max(min_val, min(max_val, float(value)))

# プラグイン内での適用例
def _on_brightness_change(self, value: float) -> None:
    """明度変更時の安全な処理"""
    # 範囲チェック（-100 ～ +100）
    safe_value = safe_value_clamp(value, -100.0, 100.0)
    
    if safe_value != value:
        logger.warning(f"値が範囲外のため修正: {value} → {safe_value}")
    
    self.brightness_value = int(safe_value)
    self._on_parameter_change()
```

##### 3. マウスリリースタイミング問題
**問題**: マウスリリース時とドラッグ中の値処理が不整合

**解決策**: 明示的なマウスイベント処理
```python
class EnhancedSliderHandler:
    """拡張スライダーハンドラー"""
    
    def __init__(self, slider: ctk.CTkSlider, callback: Callable):
        self.slider = slider
        self.callback = callback
        self._dragging = False
        self._last_value = None
        
        # イベントバインド
        self.slider.bind("<Button-1>", self._on_mouse_down)
        self.slider.bind("<B1-Motion>", self._on_mouse_drag)
        self.slider.bind("<ButtonRelease-1>", self._on_mouse_release)
    
    def _on_mouse_down(self, event):
        """マウス押下時"""
        self._dragging = True
        logger.debug("スライダードラッグ開始")
    
    def _on_mouse_drag(self, event):
        """ドラッグ中"""
        if self._dragging:
            current_value = self.slider.get()
            if self._last_value != current_value:
                self._last_value = current_value
                self.callback(current_value)
    
    def _on_mouse_release(self, event):
        """マウスリリース時"""
        if self._dragging:
            self._dragging = False
            final_value = self.slider.get()
            logger.debug(f"スライダードラッグ終了: 最終値={final_value}")
            
            # 最終値での確実な処理実行
            self.callback(final_value)
```

##### 4. UI競合状態問題
**問題**: 複数のUI要素（スライダー、ラベル）の同期更新で競合状態が発生

**解決策**: UI更新の順序制御とロック機構
```python
import threading
from typing import Optional

class UIUpdateManager:
    """UI更新の順序制御"""
    
    def __init__(self):
        self._update_lock = threading.Lock()
        self._pending_updates = {}
    
    def schedule_ui_update(self, element_id: str, update_func: Callable, *args, **kwargs):
        """UI更新のスケジュール"""
        with self._update_lock:
            # 既存の更新をキャンセル
            if element_id in self._pending_updates:
                self._pending_updates[element_id].cancel()
            
            # 新しい更新をスケジュール
            timer = threading.Timer(0.05, update_func, args, kwargs)  # 50ms後に実行
            self._pending_updates[element_id] = timer
            timer.start()
    
    def immediate_ui_update(self, update_func: Callable, *args, **kwargs):
        """即座のUI更新（緊急時用）"""
        with self._update_lock:
            update_func(*args, **kwargs)

# プラグインでの使用例
class OptimizedBasicPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("optimized_basic", "1.0.0")
        self.ui_manager = UIUpdateManager()
    
    def _on_brightness_change(self, value: float):
        """最適化された明度変更処理"""
        # 即座に内部値を更新
        self.brightness_value = int(value)
        
        # UI更新はスケジュール
        self.ui_manager.schedule_ui_update(
            "brightness_label",
            self._update_brightness_label,
            value
        )
        
        # 画像処理はコールバック
        self._on_parameter_change()
```

### レスポンシブUI設計

#### 動的レイアウト管理
```python
class ResponsiveLayoutManager:
    """レスポンシブなレイアウト管理"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self._layout_breakpoints = {
            'small': 800,
            'medium': 1200,
            'large': 1600
        }
    
    def adapt_layout(self, width: int, height: int):
        """ウィンドウサイズに応じたレイアウト調整"""
        if width < self._layout_breakpoints['small']:
            self._apply_compact_layout()
        elif width < self._layout_breakpoints['medium']:
            self._apply_standard_layout()
        else:
            self._apply_expanded_layout()
    
    def _apply_compact_layout(self):
        """コンパクトレイアウト（狭い画面）"""
        # プラグインタブを垂直配置
        # コントロールパネルを折りたたみ式に
        pass
    
    def _apply_standard_layout(self):
        """標準レイアウト"""
        # デフォルトの横並び配置
        pass
    
    def _apply_expanded_layout(self):
        """拡張レイアウト（広い画面）"""
        # 追加情報パネルの表示
        # より詳細なコントロールの展開
        pass
```

## パフォーマンス最適化

### 画像処理最適化戦略

#### 1. 遅延評価システム
```python
import time
from typing import Callable, Any
from dataclasses import dataclass

@dataclass
class ProcessingTask:
    """処理タスクの定義"""
    task_id: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    created_at: float = 0.0

class LazyEvaluationEngine:
    """遅延評価エンジン"""
    
    def __init__(self, delay_ms: int = 300):
        self.delay_ms = delay_ms
        self._pending_tasks = {}
        self._timers = {}
    
    def schedule_task(self, task_id: str, function: Callable, *args, **kwargs):
        """タスクの遅延実行スケジュール"""
        # 既存タスクのキャンセル
        if task_id in self._timers:
            self._timers[task_id].cancel()
        
        # 新しいタスクのスケジュール
        task = ProcessingTask(
            task_id=task_id,
            function=function,
            args=args,
            kwargs=kwargs,
            created_at=time.time()
        )
        
        timer = threading.Timer(
            self.delay_ms / 1000.0,
            self._execute_task,
            (task,)
        )
        
        self._pending_tasks[task_id] = task
        self._timers[task_id] = timer
        timer.start()
    
    def _execute_task(self, task: ProcessingTask):
        """タスクの実行"""
        try:
            logger.debug(f"遅延タスク実行: {task.task_id}")
            result = task.function(*task.args, **task.kwargs)
            return result
        except Exception as e:
            logger.error(f"遅延タスク実行エラー {task.task_id}: {e}")
        finally:
            # クリーンアップ
            self._pending_tasks.pop(task.task_id, None)
            self._timers.pop(task.task_id, None)

# プラグインでの使用例
class PerformantPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("performant", "1.0.0")
        self.lazy_engine = LazyEvaluationEngine(delay_ms=200)
    
    def _on_parameter_change(self):
        """パラメータ変更時の最適化処理"""
        # 遅延評価でコールバック実行
        self.lazy_engine.schedule_task(
            "image_update",
            self._parameter_change_callback
        )
```

#### 2. 画像処理キャッシュシステム
```python
import hashlib
from typing import Optional, Tuple
from PIL import Image
import pickle

class ImageProcessingCache:
    """画像処理結果のキャッシュ"""
    
    def __init__(self, max_cache_size: int = 50):
        self.max_cache_size = max_cache_size
        self._cache = {}
        self._access_order = []
    
    def get_cache_key(self, image: Image.Image, parameters: dict) -> str:
        """キャッシュキーの生成"""
        # 画像のハッシュ
        image_hash = hashlib.md5(image.tobytes()).hexdigest()
        
        # パラメータのハッシュ
        param_str = str(sorted(parameters.items()))
        param_hash = hashlib.md5(param_str.encode()).hexdigest()
        
        return f"{image_hash}_{param_hash}"
    
    def get(self, image: Image.Image, parameters: dict) -> Optional[Image.Image]:
        """キャッシュから結果を取得"""
        cache_key = self.get_cache_key(image, parameters)
        
        if cache_key in self._cache:
            # アクセス順序の更新（LRU）
            self._access_order.remove(cache_key)
            self._access_order.append(cache_key)
            
            logger.debug(f"キャッシュヒット: {cache_key[:8]}...")
            return self._cache[cache_key]
        
        return None
    
    def put(self, image: Image.Image, parameters: dict, result: Image.Image):
        """結果をキャッシュに保存"""
        cache_key = self.get_cache_key(image, parameters)
        
        # キャッシュサイズ制限
        if len(self._cache) >= self.max_cache_size:
            # LRUで古いエントリを削除
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        self._cache[cache_key] = result.copy()
        self._access_order.append(cache_key)
        
        logger.debug(f"キャッシュ保存: {cache_key[:8]}...")

# プラグインでのキャッシュ利用
class CachedPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("cached", "1.0.0")
        self.cache = ImageProcessingCache(max_cache_size=30)
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """キャッシュ機能付き画像処理"""
        current_params = self.get_parameters()
        
        # キャッシュから検索
        cached_result = self.cache.get(image, current_params)
        if cached_result:
            return cached_result
        
        # 処理実行
        result = self._perform_actual_processing(image)
        
        # 結果をキャッシュに保存
        self.cache.put(image, current_params, result)
        
        return result
```

#### 3. マルチスレッド処理
```python
import concurrent.futures
from typing import List, Callable
import numpy as np

class ParallelImageProcessor:
    """並列画像処理エンジン"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or os.cpu_count()
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        )
    
    def process_image_parallel(self, 
                             image: Image.Image, 
                             processors: List[Callable],
                             combine_func: Callable = None) -> Image.Image:
        """画像の並列処理"""
        
        # 画像を複数の処理に分散
        futures = []
        for processor in processors:
            future = self.executor.submit(processor, image)
            futures.append(future)
        
        # 結果の収集
        results = []
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result(timeout=30)  # 30秒タイムアウト
                results.append(result)
            except Exception as e:
                logger.error(f"並列処理エラー: {e}")
                results.append(image)  # エラー時は元画像
        
        # 結果の統合
        if combine_func:
            return combine_func(results)
        else:
            return results[0] if results else image
    
    def process_large_image_chunks(self, 
                                 image: Image.Image, 
                                 processor: Callable,
                                 chunk_size: int = 1000) -> Image.Image:
        """大きな画像の分割並列処理"""
        width, height = image.size
        
        if width <= chunk_size and height <= chunk_size:
            # 小さい画像はそのまま処理
            return processor(image)
        
        # チャンクに分割
        chunks = self._split_image_to_chunks(image, chunk_size)
        
        # 各チャンクを並列処理
        processed_chunks = []
        futures = []
        
        for chunk in chunks:
            future = self.executor.submit(processor, chunk['image'])
            futures.append((future, chunk['position']))
        
        # 結果の収集
        for future, position in futures:
            try:
                processed_chunk = future.result(timeout=60)
                processed_chunks.append({
                    'image': processed_chunk,
                    'position': position
                })
            except Exception as e:
                logger.error(f"チャンク処理エラー: {e}")
        
        # チャンクを結合
        return self._combine_chunks(processed_chunks, image.size)
```

### メモリ最適化

#### ガベージコレクション制御
```python
import gc
import psutil
import os
from typing import Optional

class MemoryManager:
    """メモリ使用量の監視と最適化"""
    
    def __init__(self, warning_threshold: float = 0.8, critical_threshold: float = 0.9):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self._last_gc_time = time.time()
        self._gc_interval = 30  # 30秒間隔
    
    def get_memory_usage(self) -> dict:
        """現在のメモリ使用量を取得"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # システム全体のメモリ情報
        system_memory = psutil.virtual_memory()
        
        return {
            'process_memory_mb': memory_info.rss / 1024 / 1024,
            'system_memory_percent': system_memory.percent / 100,
            'available_memory_mb': system_memory.available / 1024 / 1024
        }
    
    def check_memory_pressure(self) -> str:
        """メモリ圧迫状況をチェック"""
        usage = self.get_memory_usage()
        memory_percent = usage['system_memory_percent']
        
        if memory_percent >= self.critical_threshold:
            return 'critical'
        elif memory_percent >= self.warning_threshold:
            return 'warning'
        else:
            return 'normal'
    
    def force_garbage_collection(self):
        """強制ガベージコレクション"""
        logger.debug("強制ガベージコレクション実行")
        
        # 各世代のGC実行
        collected = []
        for generation in range(3):
            count = gc.collect(generation)
            collected.append(count)
        
        self._last_gc_time = time.time()
        logger.debug(f"GC完了: 回収オブジェクト数 = {collected}")
    
    def auto_memory_management(self):
        """自動メモリ管理"""
        current_time = time.time()
        
        # 定期的なGC
        if current_time - self._last_gc_time > self._gc_interval:
            pressure = self.check_memory_pressure()
            
            if pressure == 'critical':
                logger.warning("メモリ圧迫状態 - 強制GC実行")
                self.force_garbage_collection()
            elif pressure == 'warning':
                logger.info("メモリ使用量注意 - 軽量GC実行")
                gc.collect(0)  # 第0世代のみ
                self._last_gc_time = current_time

# プラグインでのメモリ管理
class MemoryOptimizedPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("memory_optimized", "1.0.0")
        self.memory_manager = MemoryManager()
    
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """メモリ最適化された画像処理"""
        # 処理前のメモリチェック
        self.memory_manager.auto_memory_management()
        
        try:
            # 画像処理実行
            result = self._perform_processing(image)
            
            # 大きな中間オブジェクトの明示的削除
            if hasattr(self, '_temp_arrays'):
                del self._temp_arrays
            
            return result
        
        except MemoryError:
            logger.error("メモリ不足 - 処理を中断")
            self.memory_manager.force_garbage_collection()
            return image  # 元画像を返す
```

## クロスプラットフォーム対応

### プラットフォーム固有処理の抽象化

```python
import platform
import sys
from typing import Any, Dict, Optional
from pathlib import Path

class PlatformAdapter:
    """プラットフォーム固有処理の抽象化"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_macos = self.platform == 'darwin'
        self.is_linux = self.platform == 'linux'
    
    def get_default_font(self) -> tuple:
        """プラットフォーム別デフォルトフォント"""
        if self.is_windows:
            return ("Segoe UI", 10)
        elif self.is_macos:
            return ("SF Pro Display", 10)
        else:  # Linux
            return ("Ubuntu", 10)
    
    def get_file_dialog_options(self) -> Dict[str, Any]:
        """ファイルダイアログオプション"""
        base_options = {
            'title': '画像ファイルを選択',
            'filetypes': [
                ('画像ファイル', '*.jpg;*.jpeg;*.png;*.bmp;*.tiff'),
                ('すべてのファイル', '*.*')
            ]
        }
        
        if self.is_macos:
            # macOS特有のオプション
            base_options['message'] = '編集する画像を選択してください'
        
        return base_options
    
    def get_temp_directory(self) -> Path:
        """一時ディレクトリの取得"""
        if self.is_windows:
            return Path(os.environ.get('TEMP', 'C:\\temp'))
        else:
            return Path('/tmp')
    
    def get_app_data_directory(self) -> Path:
        """アプリケーションデータディレクトリ"""
        app_name = "AdvancedImageEditor"
        
        if self.is_windows:
            base = Path(os.environ.get('APPDATA', ''))
            return base / app_name
        elif self.is_macos:
            base = Path.home() / 'Library' / 'Application Support'
            return base / app_name
        else:  # Linux
            base = Path.home() / '.local' / 'share'
            return base / app_name.lower()
    
    def optimize_for_platform(self, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """プラットフォーム固有の最適化"""
        if self.is_macos:
            # macOSでのボタンスタイル調整
            if 'button_color' in widget_config:
                widget_config['button_color'] = '#007AFF'  # macOSブルー
        elif self.is_windows:
            # Windowsでのフォントサイズ調整
            if 'font_size' in widget_config:
                widget_config['font_size'] = max(9, widget_config['font_size'])
        
        return widget_config

# 使用例
platform_adapter = PlatformAdapter()

class CrossPlatformUI:
    def __init__(self):
        self.adapter = platform_adapter
    
    def create_optimized_button(self, parent, text: str, command: Callable) -> ctk.CTkButton:
        """プラットフォーム最適化ボタン"""
        config = {
            'text': text,
            'command': command,
            'font': self.adapter.get_default_font(),
            'button_color': '#1f538d'
        }
        
        # プラットフォーム固有最適化
        config = self.adapter.optimize_for_platform(config)
        
        return ctk.CTkButton(parent, **config)
```

### ファイルパス処理の統一

```python
from pathlib import Path
import os
from typing import Union, List

class UnifiedPathManager:
    """統一ファイルパス管理"""
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """パスの正規化（プラットフォーム非依存）"""
        return Path(path).resolve()
    
    @staticmethod
    def safe_join(*paths) -> Path:
        """安全なパス結合（ディレクトリトラバーサル対策）"""
        base_path = Path(paths[0]).resolve()
        
        for path_part in paths[1:]:
            # 相対パスのみ許可
            if Path(path_part).is_absolute():
                raise ValueError(f"絶対パスは許可されていません: {path_part}")
            
            # '..' によるディレクトリ遡上をチェック
            normalized = (base_path / path_part).resolve()
            if not str(normalized).startswith(str(base_path)):
                raise ValueError(f"ディレクトリトラバーサルが検出されました: {path_part}")
            
            base_path = normalized
        
        return base_path
    
    @staticmethod
    def get_relative_path(target: Union[str, Path], base: Union[str, Path]) -> Path:
        """基準パスからの相対パスを取得"""
        target_path = Path(target).resolve()
        base_path = Path(base).resolve()
        
        try:
            return target_path.relative_to(base_path)
        except ValueError:
            # 相対パスが作成できない場合は絶対パスを返す
            return target_path
    
    @staticmethod
    def ensure_directory_exists(path: Union[str, Path]) -> Path:
        """ディレクトリの存在確認と作成"""
        dir_path = Path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    @staticmethod
    def find_files_by_pattern(directory: Union[str, Path], 
                            pattern: str, 
                            recursive: bool = True) -> List[Path]:
        """パターンによるファイル検索"""
        dir_path = Path(directory)
        
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
```

## エラーハンドリング

### 階層化エラーハンドリングシステム

```python
import traceback
import sys
from typing import Optional, Callable, Any
from enum import Enum

class ErrorSeverity(Enum):
    """エラーの重要度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ApplicationError(Exception):
    """アプリケーション共通エラークラス"""
    
    def __init__(self, 
                 message: str, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 error_code: Optional[str] = None,
                 original_exception: Optional[Exception] = None):
        super().__init__(message)
        self.severity = severity
        self.error_code = error_code
        self.original_exception = original_exception
        self.timestamp = time.time()

class PluginError(ApplicationError):
    """プラグイン関連エラー"""
    
    def __init__(self, plugin_id: str, message: str, **kwargs):
        self.plugin_id = plugin_id
        super().__init__(f"Plugin '{plugin_id}': {message}", **kwargs)

class ImageProcessingError(ApplicationError):
    """画像処理関連エラー"""
    
    def __init__(self, operation: str, message: str, **kwargs):
        self.operation = operation
        super().__init__(f"Image processing '{operation}': {message}", **kwargs)

class ErrorHandler:
    """統一エラーハンドリングシステム"""
    
    def __init__(self):
        self._error_callbacks: Dict[ErrorSeverity, List[Callable]] = {
            severity: [] for severity in ErrorSeverity
        }
        self._error_history: List[ApplicationError] = []
        self._max_history = 100
    
    def register_error_callback(self, severity: ErrorSeverity, callback: Callable):
        """エラー処理コールバックの登録"""
        self._error_callbacks[severity].append(callback)
    
    def handle_error(self, error: ApplicationError) -> bool:
        """エラーの処理実行"""
        try:
            # エラー履歴に追加
            self._error_history.append(error)
            if len(self._error_history) > self._max_history:
                self._error_history.pop(0)
            
            # ログ出力
            self._log_error(error)
            
            # 重要度別処理
            callbacks = self._error_callbacks.get(error.severity, [])
            for callback in callbacks:
                try:
                    callback(error)
                except Exception as e:
                    logger.error(f"エラーコールバック実行失敗: {e}")
            
            # 重要度による処理分岐
            if error.severity == ErrorSeverity.CRITICAL:
                return self._handle_critical_error(error)
            elif error.severity == ErrorSeverity.HIGH:
                return self._handle_high_error(error)
            
            return True
            
        except Exception as e:
            logger.critical(f"エラーハンドラー自体でエラー: {e}")
            return False
    
    def _log_error(self, error: ApplicationError):
        """エラーのログ出力"""
        log_message = f"[{error.severity.value.upper()}] {error}"
        
        if error.error_code:
            log_message += f" (Code: {error.error_code})"
        
        if error.original_exception:
            log_message += f"\n原因: {error.original_exception}"
            log_message += f"\nトレースバック:\n{traceback.format_exc()}"
        
        # 重要度に応じたログレベル
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _handle_critical_error(self, error: ApplicationError) -> bool:
        """重要なエラーの処理"""
        logger.critical("アプリケーションの緊急停止が必要な可能性があります")
        
        # ユーザーに通知
        try:
            self._show_error_dialog(
                "重要なエラー",
                f"重要なエラーが発生しました:\n{error}\n\nアプリケーションを再起動することをお勧めします。",
                error_type="critical"
            )
        except:
            pass  # UI表示に失敗してもログは残す
        
        return False  # 処理継続不可
    
    def _handle_high_error(self, error: ApplicationError) -> bool:
        """高重要度エラーの処理"""
        # ユーザーに警告
        try:
            self._show_error_dialog(
                "エラー",
                f"エラーが発生しました:\n{error}\n\n操作を再試行してください。",
                error_type="warning"
            )
        except:
            pass
        
        return True  # 処理継続可能

# デコレータによるエラーハンドリング
def handle_errors(error_handler: ErrorHandler, 
                 default_severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """エラーハンドリングデコレータ"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except ApplicationError as e:
                error_handler.handle_error(e)
                return None
            except Exception as e:
                # 予期しない例外をApplicationErrorに変換
                app_error = ApplicationError(
                    f"予期しないエラー in {func.__name__}: {str(e)}",
                    severity=default_severity,
                    original_exception=e
                )
                error_handler.handle_error(app_error)
                return None
        return wrapper
    return decorator

# 使用例
error_handler = ErrorHandler()

class SafePlugin(ImageProcessorPlugin):
    @handle_errors(error_handler, ErrorSeverity.HIGH)
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """安全な画像処理"""
        if not isinstance(image, Image.Image):
            raise ImageProcessingError(
                "validation",
                "無効な画像オブジェクトが渡されました",
                severity=ErrorSeverity.HIGH
            )
        
        try:
            return self._perform_processing(image)
        except Exception as e:
            raise ImageProcessingError(
                "processing",
                f"画像処理中にエラーが発生: {str(e)}",
                original_exception=e,
                severity=ErrorSeverity.MEDIUM
            )
```

## ログシステム

### 高度なログ管理システム

```python
import logging
import logging.handlers
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import threading
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON形式のログフォーマッター"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # 例外情報の追加
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # カスタム属性の追加
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated', 
                          'thread', 'threadName', 'processName', 'process',
                          'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)

class AdvancedLogManager:
    """高度なログ管理システム"""
    
    def __init__(self, 
                 app_name: str = "AdvancedImageEditor",
                 log_directory: Optional[Path] = None):
        self.app_name = app_name
        self.log_directory = log_directory or self._get_default_log_directory()
        self.log_directory.mkdir(parents=True, exist_ok=True)
        
        self._loggers: Dict[str, logging.Logger] = {}
        self._setup_root_logger()
    
    def _get_default_log_directory(self) -> Path:
        """デフォルトログディレクトリの取得"""
        platform_adapter = PlatformAdapter()
        app_data = platform_adapter.get_app_data_directory()
        return app_data / "logs"
    
    def _setup_root_logger(self):
        """ルートロガーのセットアップ"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # ファイルハンドラー（ローテーション付き）
        log_file = self.log_directory / f"{self.app_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """名前付きロガーの取得"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def add_performance_handler(self):
        """パフォーマンス専用ログハンドラーの追加"""
        perf_file = self.log_directory / "performance.log"
        perf_handler = logging.handlers.TimedRotatingFileHandler(
            perf_file,
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(JSONFormatter())
        
        # パフォーマンス専用ロガー
        perf_logger = logging.getLogger('performance')
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.INFO)
        
        return perf_logger
    
    def configure_plugin_logger(self, plugin_id: str) -> logging.Logger:
        """プラグイン専用ロガーの設定"""
        logger_name = f"plugin.{plugin_id}"
        plugin_logger = self.get_logger(logger_name)
        
        # プラグイン専用ファイルハンドラー
        plugin_log_file = self.log_directory / "plugins" / f"{plugin_id}.log"
        plugin_log_file.parent.mkdir(exist_ok=True)
        
        plugin_handler = logging.handlers.RotatingFileHandler(
            plugin_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        plugin_handler.setLevel(logging.DEBUG)
        plugin_handler.setFormatter(JSONFormatter())
        
        plugin_logger.addHandler(plugin_handler)
        return plugin_logger

# パフォーマンス測定デコレータ
def log_performance(logger: logging.Logger):
    """パフォーマンス測定ログデコレータ"""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.info(
                    "Function execution completed",
                    extra={
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': True,
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    "Function execution failed",
                    extra={
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': False,
                        'error': str(e),
                        'args_count': len(args),
                        'kwargs_count': len(kwargs)
                    }
                )
                raise
        return wrapper
    return decorator

# 使用例
log_manager = AdvancedLogManager()
performance_logger = log_manager.add_performance_handler()

class LoggedPlugin(ImageProcessorPlugin):
    def __init__(self, plugin_id: str):
        super().__init__(plugin_id, "1.0.0")
        self.logger = log_manager.configure_plugin_logger(plugin_id)
    
    @log_performance(performance_logger)
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """ログ付き画像処理"""
        self.logger.info(
            "Starting image processing",
            extra={
                'image_size': image.size,
                'image_mode': image.mode,
                'parameters': params
            }
        )
        
        try:
            result = self._perform_processing(image)
            
            self.logger.info(
                "Image processing completed successfully",
                extra={
                    'input_size': image.size,
                    'output_size': result.size
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Image processing failed",
                extra={
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                },
                exc_info=True
            )
            raise
```

---

これらの技術ノートにより、Advanced Image Editorの技術的な問題解決と最適化戦略を詳細に文書化しました。

**ナビゲーション**:
- 🏠 [メインハブに戻る](../README.md)
- 📖 [エンドユーザー向けガイド](USER_GUIDE.md)
- 👨‍💻 [開発者向け実装手順](DEVELOPER_GUIDE.md)
- 🏗️ [システム全体の設計思想](ARCHITECTURE.md)