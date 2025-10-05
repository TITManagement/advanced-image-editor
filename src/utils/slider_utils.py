"""
スライダーUI強化ユーティリティ - Slider Enhancement Utilities

このモジュールは、CustomTkinterスライダーに以下の機能を追加します：
- オーバーシュート対策（範囲外値の自動制限）
- チャタリング防止（デバウンス処理）
- 値のフォーマット表示
- スレッドセーフな更新処理

作成日: 2025年10月5日
更新日: 2025年10月5日
"""

import threading
import customtkinter as ctk
from typing import Callable, Optional, Union, Any
from abc import ABC, abstractmethod


class SliderCallbackHandler(ABC):
    """スライダーコールバック処理の抽象基底クラス"""
    
    @abstractmethod
    def on_value_changed(self, parameter_name: str, value: Union[int, float]) -> None:
        """値変更時のコールバック処理"""
        pass


class EnhancedSlider:
    """
    強化されたスライダークラス
    
    オーバーシュート対策とチャタリング防止機能を内蔵したスライダーラッパー
    """
    
    def __init__(
        self,
        slider: ctk.CTkSlider,
        label: ctk.CTkLabel,
        parameter_name: str,
        min_value: Union[int, float],
        max_value: Union[int, float],
        value_type: type = int,
        debounce_delay: float = 0.1,
        value_format: str = "{:.0f}",
        callback_handler: Optional[SliderCallbackHandler] = None
    ):
        """
        初期化
        
        Args:
            slider: CustomTkinterスライダーオブジェクト
            label: 値表示用ラベル
            parameter_name: パラメータ名
            min_value: 最小値
            max_value: 最大値
            value_type: 値の型（int または float）
            debounce_delay: デバウンス遅延時間（秒）
            value_format: 値のフォーマット文字列
            callback_handler: コールバックハンドラー
        """
        self.slider = slider
        self.label = label
        self.parameter_name = parameter_name
        self.min_value = min_value
        self.max_value = max_value
        self.value_type = value_type
        self.debounce_delay = debounce_delay
        self.value_format = value_format
        self.callback_handler = callback_handler
        
        # 内部状態
        self._current_value = min_value
        self._update_timer: Optional[threading.Timer] = None
        
        # スライダーにコールバックを設定
        self.slider.configure(command=self._on_slider_change)
    
    def _clamp_value(self, value: Union[int, float]) -> Union[int, float]:
        """値を指定範囲内に制限（オーバーシュート対策）"""
        if self.value_type == int:
            clamped = max(self.min_value, min(self.max_value, int(round(value))))
        else:
            clamped = max(self.min_value, min(self.max_value, float(value)))
        return clamped
    
    def _update_label(self, value: Union[int, float]) -> None:
        """ラベルの値を更新"""
        formatted_value = self.value_format.format(value)
        self.label.configure(text=formatted_value)
    
    def _on_slider_change(self, raw_value: float) -> None:
        """スライダー変更時のコールバック（内部使用）"""
        # オーバーシュート対策：値を制限
        clamped_value = self._clamp_value(raw_value)
        self._current_value = clamped_value
        
        # ラベル更新
        self._update_label(clamped_value)
        
        # チャタリング防止：デバウンス処理
        self._debounced_callback()
    
    def _debounced_callback(self) -> None:
        """デバウンス処理付きコールバック実行"""
        # 既存のタイマーをキャンセル
        if self._update_timer:
            self._update_timer.cancel()
        
        # 遅延実行を設定
        def delayed_callback():
            try:
                if self.callback_handler:
                    self.callback_handler.on_value_changed(
                        self.parameter_name, 
                        self._current_value
                    )
            finally:
                self._update_timer = None
        
        # 新しいタイマーを開始
        self._update_timer = threading.Timer(self.debounce_delay, delayed_callback)
        self._update_timer.start()
    
    def get_value(self) -> Union[int, float]:
        """現在の値を取得"""
        return self._current_value
    
    def set_value(self, value: Union[int, float], update_slider: bool = True) -> None:
        """値を設定"""
        clamped_value = self._clamp_value(value)
        self._current_value = clamped_value
        
        # ラベル更新
        self._update_label(clamped_value)
        
        # スライダー位置も更新する場合
        if update_slider:
            self.slider.set(clamped_value)
    
    def reset(self, default_value: Union[int, float] = None) -> None:
        """値をリセット"""
        reset_value = default_value if default_value is not None else self.min_value
        self.set_value(reset_value, update_slider=True)
    
    def cleanup(self) -> None:
        """リソースのクリーンアップ"""
        if self._update_timer:
            self._update_timer.cancel()
            self._update_timer = None


class SliderManager:
    """
    複数のEnhancedSliderを管理するクラス
    
    プラグイン全体のスライダー管理を簡素化
    """
    
    def __init__(self, callback_handler: Optional[SliderCallbackHandler] = None):
        """
        初期化
        
        Args:
            callback_handler: 共通のコールバックハンドラー
        """
        self.callback_handler = callback_handler
        self.sliders: dict[str, EnhancedSlider] = {}
    
    def create_slider(
        self,
        parent: ctk.CTkFrame,
        parameter_name: str,
        text: str,
        from_: Union[int, float],
        to: Union[int, float],
        default_value: Union[int, float],
        value_type: type = int,
        debounce_delay: float = 0.1,
        value_format: str = "{:.0f}",
        callback_handler: Optional[SliderCallbackHandler] = None
    ) -> tuple[ctk.CTkSlider, ctk.CTkLabel]:
        """
        強化されたスライダーを作成
        
        Returns:
            tuple: (slider, label) のタプル（既存コードとの互換性のため）
        """
        # UI要素を作成
        slider = ctk.CTkSlider(parent, from_=from_, to=to)
        label = ctk.CTkLabel(parent, text=value_format.format(default_value))
        
        # EnhancedSliderでラップ
        enhanced_slider = EnhancedSlider(
            slider=slider,
            label=label,
            parameter_name=parameter_name,
            min_value=from_,
            max_value=to,
            value_type=value_type,
            debounce_delay=debounce_delay,
            value_format=value_format,
            callback_handler=callback_handler or self.callback_handler
        )
        
        # 初期値を設定
        enhanced_slider.set_value(default_value)
        
        # 管理辞書に追加
        self.sliders[parameter_name] = enhanced_slider
        
        return slider, label
    
    def get_slider(self, parameter_name: str) -> Optional[EnhancedSlider]:
        """指定されたパラメータのスライダーを取得"""
        return self.sliders.get(parameter_name)
    
    def get_value(self, parameter_name: str) -> Optional[Union[int, float]]:
        """指定されたパラメータの値を取得"""
        slider = self.sliders.get(parameter_name)
        return slider.get_value() if slider else None
    
    def set_value(self, parameter_name: str, value: Union[int, float]) -> None:
        """指定されたパラメータの値を設定"""
        slider = self.sliders.get(parameter_name)
        if slider:
            slider.set_value(value)
    
    def reset_all(self) -> None:
        """全スライダーをリセット"""
        for slider in self.sliders.values():
            slider.reset()
    
    def cleanup(self) -> None:
        """全スライダーのリソースをクリーンアップ"""
        for slider in self.sliders.values():
            slider.cleanup()
        self.sliders.clear()


# 便利関数
def create_enhanced_slider_with_label(
    parent: ctk.CTkFrame,
    text: str,
    from_: Union[int, float],
    to: Union[int, float],
    default_value: Union[int, float],
    callback_handler: SliderCallbackHandler,
    parameter_name: str,
    value_type: type = int,
    value_format: str = "{:.0f}",
    debounce_delay: float = 0.1
) -> tuple[ctk.CTkSlider, ctk.CTkLabel, EnhancedSlider]:
    """
    ラベル付き強化スライダーを作成する便利関数
    
    Returns:
        tuple: (slider, label, enhanced_slider)
    """
    # フレームを作成
    frame = ctk.CTkFrame(parent)
    frame.pack(fill="x", padx=10, pady=5)
    
    # ラベル
    text_label = ctk.CTkLabel(frame, text=text)
    text_label.pack(side="left", padx=(10, 5))
    
    # スライダー
    slider = ctk.CTkSlider(frame, from_=from_, to=to)
    slider.pack(side="left", fill="x", expand=True, padx=(5, 10))
    
    # 値表示ラベル
    value_label = ctk.CTkLabel(frame, text=value_format.format(default_value), width=60)
    value_label.pack(side="right", padx=(5, 10))
    
    # EnhancedSliderでラップ
    enhanced_slider = EnhancedSlider(
        slider=slider,
        label=value_label,
        parameter_name=parameter_name,
        min_value=from_,
        max_value=to,
        value_type=value_type,
        debounce_delay=debounce_delay,
        value_format=value_format,
        callback_handler=callback_handler
    )
    
    # 初期値を設定
    enhanced_slider.set_value(default_value)
    
    return slider, value_label, enhanced_slider