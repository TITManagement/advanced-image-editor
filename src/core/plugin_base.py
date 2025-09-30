#!/usr/bin/env python3
"""
プラグインシステム基底クラス - Plugin System Base Classes

画像処理プラグインの統一APIインターフェースを定義
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from PIL import Image
import customtkinter as ctk


class ImageProcessorPlugin(ABC):
    def setup_ui(self, parent):
        """UI未実装プラグイン用のダミー"""
        pass
    """
    画像処理プラグインの基底クラス
    全ての画像処理プラグインはこのクラスを継承する必要があります
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
        self._sliders = {}
        self._labels = {}
        self._buttons = {}
        # undo/バックアップ用属性（全プラグインで参照可能）
        self.special_filter_backup = None
        self.morphology_backup = None
        self.contour_backup = None
        self.features_backup = None
        self.frequency_backup = None
        self.blur_backup = None
        self.noise_backup = None
        self.histogram_backup = None
        
    @abstractmethod
    def get_display_name(self) -> str:
        """プラグインの表示名を返す"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """プラグインの説明を返す"""
        pass
    
    @abstractmethod
    def create_ui(self, parent: ctk.CTkFrame) -> None:
        """
        プラグインのUIコントロールを作成
        Args:
            parent: 親フレーム
        """
        pass
    
    @abstractmethod
    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """
        画像処理を実行
        Args:
            image: 入力画像
            **params: 処理パラメータ
        Returns:
            処理後の画像
        """
        pass
    
    def apply_special_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """
        特殊フィルターを適用（オプション）
        個別のプラグインで必要に応じてオーバーライドする
        
        Args:
            image: 入力画像
            filter_type: フィルターの種類
        Returns:
            処理後の画像（デフォルトでは入力画像をそのまま返す）
        """
        # デフォルト実装：何も処理せずに元の画像を返す
        return image
    
    def get_parameters(self) -> Dict[str, Any]:
        """現在のパラメータ値を取得"""
        params = {}
        for name, slider in self._sliders.items():
            params[name] = slider.get()
        return params
    
    def reset_parameters(self) -> None:
        """パラメータをデフォルト値にリセット"""
        for slider in self._sliders.values():
            default_value = slider.default_value if hasattr(slider, 'default_value') else 0
            slider.set(default_value)
            # スライダーのコールバックを明示的に呼び出して値を同期
            if hasattr(slider, 'command') and slider.command:
                try:
                    slider.command(default_value)
                except Exception as e:
                    print(f"⚠️ スライダーコールバックエラー: {e}")
    
    def set_parameter_change_callback(self, callback: Callable) -> None:
        """パラメータ変更時のコールバックを設定"""
        self.parameter_change_callback = callback
    
    def _on_parameter_change(self, value: Any = None) -> None:
        """パラメータ変更時の内部処理"""
        if hasattr(self, 'parameter_change_callback'):
            self.parameter_change_callback()
    
    def enable(self) -> None:
        """プラグインを有効にする"""
        self.enabled = True
    
    def disable(self) -> None:
        """プラグインを無効にする"""
        self.enabled = False
    
    def is_enabled(self) -> bool:
        """プラグインが有効かどうかを返す"""
        return self.enabled


class PluginManager:
    """
    プラグインマネージャー
    プラグインの登録、管理、実行を担当
    """
    
    def __init__(self):
        self.plugins: Dict[str, ImageProcessorPlugin] = {}
        self.plugin_order: List[str] = []
        
    def register_plugin(self, plugin: ImageProcessorPlugin) -> None:
        """
        プラグインを登録
        Args:
            plugin: 登録するプラグイン
        """
        self.plugins[plugin.name] = plugin
        if plugin.name not in self.plugin_order:
            self.plugin_order.append(plugin.name)
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """
        プラグインを登録解除
        Args:
            plugin_name: 解除するプラグイン名
        """
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
        if plugin_name in self.plugin_order:
            self.plugin_order.remove(plugin_name)
    
    def get_plugin(self, plugin_name: str) -> Optional[ImageProcessorPlugin]:
        """
        プラグインを取得
        Args:
            plugin_name: プラグイン名
        Returns:
            プラグインインスタンス（存在しない場合はNone）
        """
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[ImageProcessorPlugin]:
        """全プラグインのリストを取得"""
        return [self.plugins[name] for name in self.plugin_order if name in self.plugins]
    
    def get_enabled_plugins(self) -> List[ImageProcessorPlugin]:
        """有効なプラグインのリストを取得"""
        return [plugin for plugin in self.get_all_plugins() if plugin.is_enabled()]
    
    def process_image_with_plugin(self, plugin_name: str, image: Image.Image) -> Optional[Image.Image]:
        """
        指定されたプラグインで画像を処理
        Args:
            plugin_name: プラグイン名
            image: 入力画像
        Returns:
            処理後の画像（失敗時はNone）
        """
        plugin = self.get_plugin(plugin_name)
        if plugin and plugin.is_enabled():
            try:
                params = plugin.get_parameters()
                return plugin.process_image(image, **params)
            except Exception as e:
                print(f"❌ プラグイン '{plugin_name}' エラー: {e}")
                return None
        return None
    
    def process_image_with_all_plugins(self, image: Image.Image) -> Image.Image:
        """
        有効な全プラグインで順次画像を処理
        Args:
            image: 入力画像
        Returns:
            処理後の画像
        """
        result_image = image.copy()
        for plugin in self.get_enabled_plugins():
            try:
                params = plugin.get_parameters()
                result_image = plugin.process_image(result_image, **params)
            except Exception as e:
                print(f"❌ プラグイン '{plugin.name}' エラー: {e}")
                continue
        return result_image


class PluginUIHelper:
    """
    プラグインUI作成のヘルパークラス
    """
    
    @staticmethod
    def create_slider_with_label(
        parent: ctk.CTkFrame,
        text: str,
        from_: float,
        to: float,
        default_value: float,
        command: Optional[Callable] = None,
        value_format: str = "{:.1f}"
    ) -> Tuple[ctk.CTkSlider, ctk.CTkLabel]:
        """
        ラベル付きスライダーを作成（マウスリリース対応）
        Args:
            parent: 親フレーム
            text: ラベルテキスト
            from_: 最小値
            to: 最大値
            default_value: デフォルト値
            command: 値変更時のコールバック
            value_format: 値の表示フォーマット
        Returns:
            (スライダー, 値ラベル)のタプル
        """
        # ラベル
        label = ctk.CTkLabel(parent, text=text, font=("Arial", 11))
        label.pack(anchor="w", padx=3, pady=(5, 0))
        
        # 値表示ラベル
        value_label = ctk.CTkLabel(parent, text=value_format.format(default_value), font=("Arial", 9))
        value_label.pack(anchor="w", padx=3)
        
        # コールバック処理関数
        def handle_slider_change(value):
            # 【重要】CustomTkinterスライダーの値オーバーシュート対策
            # ドラッグ中に内部的に範囲外の値が渡される場合があるため、
            # 明示的に範囲チェックして正しい値に修正する
            clamped_value = max(from_, min(to, value))
            
            # 【UI応答性】値ラベルを即座に更新（範囲修正済みの値で）
            # ユーザーにリアルタイムフィードバックを提供
            value_label.configure(text=value_format.format(clamped_value))
            
            # 【デバッグ】値の変化を監視
            if abs(value - clamped_value) > 0.001:  # 値が範囲外の場合
                print(f"⚠️ スライダー値修正: {value:.3f} → {clamped_value:.3f} (範囲: {from_}〜{to})")
            
            # 【コールバック最適化】プラグインコールバックを呼び出し（範囲修正済みの値で）
            # 二重コールバック問題を回避し、正確な値のみを渡す
            if command:
                command(clamped_value)
        
        # スライダー作成
        slider = ctk.CTkSlider(
            parent,
            from_=from_,
            to=to,
            command=handle_slider_change
        )
        slider.set(default_value)
        
        # 【重要】CustomTkinterスライダーのマウスリリース対策
        # CustomTkinterではドラッグ中とマウスリリース後でイベント処理が異なる場合があり、
        # マウスリリース時に正確な最終値でコールバックを確実に実行する
        def on_mouse_release(event):
            if command:
                current_value = slider.get()
                # 【値精度保証】範囲チェック
                clamped_value = max(from_, min(to, current_value))
                print(f"🖱️ マウスリリース: 値={current_value:.3f}, 修正後={clamped_value:.3f}")
                # 【スライダー同期】修正された値でスライダーを再設定
                if abs(current_value - clamped_value) > 0.001:
                    slider.set(clamped_value)
                command(clamped_value)
        
        # 【イベントバインディング】マウスリリースイベントをバインド
        # CustomTkinterの内部実装によるイベントタイミング問題への対策
        slider.bind("<ButtonRelease-1>", on_mouse_release)
        
        # カスタム属性として保存
        setattr(slider, 'default_value', default_value)
        
        slider.pack(fill="x", padx=5, pady=3)
        
        return slider, value_label
    
    @staticmethod
    def create_button(
        parent: ctk.CTkFrame,
        text: str,
        command: Optional[Callable] = None,
        width: int = 120
    ) -> ctk.CTkButton:
        """
        ボタンを作成
        Args:
            parent: 親フレーム
            text: ボタンテキスト
            command: クリック時のコールバック
            width: ボタン幅
        Returns:
            ボタン
        """
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            font=("Arial", 11)
        )
        button.pack(padx=5, pady=3)
        return button