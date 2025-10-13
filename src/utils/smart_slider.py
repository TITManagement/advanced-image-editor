"""
SmartSlider - オーバーシュート対策とチャタリング防止を内蔵したスライダーパッケージ

使い方:
    from utils.smart_slider import SmartSlider
    
    slider, label = SmartSlider.create(
        parent=parent,
        text="明度",
        from_=-100,
        to=100,
        default_value=0,
        command=self._on_brightness_change
    )

特徴:
- オーバーシュート対策: 範囲外値の自動制限
- チャタリング防止: 100msデバウンス処理
- 既存APIとの互換性: PluginUIHelperと同じ戻り値

作成日: 2025年10月5日
"""

import threading
import customtkinter as ctk
from typing import Callable, Optional, Tuple, Union


class SmartSlider:
    """
    オーバーシュート対策とチャタリング防止を内蔵したスマートスライダー
    """
    
    # クラス変数: アクティブなインスタンスを管理（クリーンアップ用）
    _active_instances = []
    
    def __init__(
        self,
        slider: ctk.CTkSlider,
        label: ctk.CTkLabel,
        min_value: Union[int, float],
        max_value: Union[int, float],
        value_type: type = int,
        debounce_delay: float = 0.1,
        value_format: str = "{:.0f}",
        callback: Optional[Callable] = None
    ):
        self.slider = slider
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value_type = value_type
        self.debounce_delay = debounce_delay
        self.value_format = value_format
        self.callback = callback
        
        # 内部状態
        self._current_value = min_value
        self._update_timer: Optional[threading.Timer] = None
        
        # スライダーにコールバックを設定
        self.slider.configure(command=self._on_slider_change)
        
        # アクティブインスタンスリストに追加
        SmartSlider._active_instances.append(self)
    
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
        
        # ラベル更新（即座に反映）
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
                if self.callback:
                    self.callback(self._current_value)
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
    
    def cleanup(self) -> None:
        """リソースのクリーンアップ"""
        if self._update_timer:
            self._update_timer.cancel()
            self._update_timer = None
        
        # アクティブインスタンスリストから削除
        if self in SmartSlider._active_instances:
            SmartSlider._active_instances.remove(self)
    
    @staticmethod
    def create(
        parent: ctk.CTkFrame,
        text: str,
        from_: Union[int, float],
        to: Union[int, float],
        default_value: Union[int, float],
        command: Optional[Callable] = None,
        value_format: str = "{:.0f}",
        debounce_delay: float = 0.1,
        value_type: type = int
    ) -> Tuple[ctk.CTkSlider, ctk.CTkLabel]:
        """
        スマートスライダーを作成（PluginUIHelper.create_slider_with_label互換）
        
        Args:
            parent: 親フレーム
            text: ラベルテキスト
            from_: 最小値
            to: 最大値
            default_value: デフォルト値
            command: 値変更時のコールバック
            value_format: 値の表示フォーマット
            debounce_delay: デバウンス遅延時間（秒）
            value_type: 値の型（int または float）
            
        Returns:
            (スライダー, 値ラベル)のタプル（既存コードとの互換性）
        """
        # ラベル
        label = ctk.CTkLabel(parent, text=text, font=("Arial", 11))
        label.pack(anchor="w", padx=3, pady=(5, 0))
        
        # 値表示ラベル
        value_label = ctk.CTkLabel(parent, text=value_format.format(default_value), font=("Arial", 9))
        value_label.pack(anchor="w", padx=3)
        
        # スライダー
        slider = ctk.CTkSlider(
            parent,
            from_=int(from_) if isinstance(from_, float) and from_.is_integer() else from_,
            to=int(to) if isinstance(to, float) and to.is_integer() else to,
            width=250,
            height=20
        )
        slider.pack(fill="x", padx=10, pady=(2, 8))
        slider.set(default_value)
        
        # SmartSliderインスタンスを作成（内部でオーバーシュート対策・チャタリング防止を処理）
        smart_instance = SmartSlider(
            slider=slider,
            label=value_label,
            min_value=from_,
            max_value=to,
            value_type=value_type,
            debounce_delay=debounce_delay,
            value_format=value_format,
            callback=command
        )
        
        # 初期値を設定
        smart_instance.set_value(default_value)
        
        # 既存コードとの互換性のため、slider と label を返す
        return slider, value_label
    
    @staticmethod
    def create_with_reset(
        parent: ctk.CTkFrame,
        text: str,
        from_: Union[int, float],
        to: Union[int, float],
        default_value: Union[int, float],
        command: Optional[Callable[[Union[int, float]], None]] = None,
        value_format: str = "{:.0f}",
        debounce_delay: float = 0.1,
        value_type: type = int,
        reset_text: str = "🔄 取消",
        reset_width: int = 70,
        reset_callback: Optional[Callable[[], None]] = None,
    ) -> Tuple[ctk.CTkSlider, ctk.CTkLabel, ctk.CTkButton]:
        """
        タイトル・スライダー・値表示・取消ボタンを1行にまとめて生成するヘルパー
        
        Returns:
            (スライダー, 値ラベル, 取消ボタン)
        """
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", padx=5, pady=(5, 2))
        row_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(row_frame, text=text, font=("Arial", 11))
        title_label.grid(row=0, column=0, padx=(3, 8), pady=3, sticky="w")
        
        slider = ctk.CTkSlider(
            row_frame,
            from_=int(from_) if isinstance(from_, float) and from_.is_integer() else from_,
            to=int(to) if isinstance(to, float) and to.is_integer() else to,
            height=20
        )
        slider.grid(row=0, column=1, padx=(0, 8), pady=3, sticky="ew")
        slider.set(default_value)
        
        value_label = ctk.CTkLabel(
            row_frame,
            text=value_format.format(default_value),
            font=("Arial", 10),
            width=50,
            anchor="e"
        )
        value_label.grid(row=0, column=2, padx=(0, 8), pady=3, sticky="e")
        
        smart_instance = SmartSlider(
            slider=slider,
            label=value_label,
            min_value=from_,
            max_value=to,
            value_type=value_type,
            debounce_delay=debounce_delay,
            value_format=value_format,
            callback=command
        )
        smart_instance.set_value(default_value)
        setattr(slider, "default_value", default_value)
        
        def _reset_action():
            smart_instance.set_value(default_value)
            if smart_instance.callback:
                smart_instance.callback(default_value)
            if reset_callback:
                reset_callback()
        
        reset_button = ctk.CTkButton(
            row_frame,
            text=reset_text,
            command=_reset_action,
            width=reset_width,
            font=("Arial", 11)
        )
        reset_button.grid(row=0, column=3, padx=(0, 3), pady=3, sticky="e")
        
        return slider, value_label, reset_button
    
    @staticmethod
    def cleanup_all() -> None:
        """全てのSmartSliderインスタンスをクリーンアップ"""
        for instance in SmartSlider._active_instances[:]:  # コピーを作成してイテレート
            instance.cleanup()
        SmartSlider._active_instances.clear()


# 便利関数（従来のPluginUIHelperスタイル）
def create_smart_slider_with_label(
    parent: ctk.CTkFrame,
    text: str,
    from_: Union[int, float],
    to: Union[int, float],
    default_value: Union[int, float],
    command: Optional[Callable] = None,
    value_format: str = "{:.0f}",
    debounce_delay: float = 0.1,
    value_type: type = int
) -> Tuple[ctk.CTkSlider, ctk.CTkLabel]:
    """
    スマートスライダー作成の便利関数
    SmartSlider.create() のエイリアス
    """
    return SmartSlider.create(
        parent=parent,
        text=text,
        from_=from_,
        to=to,
        default_value=default_value,
        command=command,
        value_format=value_format,
        debounce_delay=debounce_delay,
        value_type=value_type
    )
