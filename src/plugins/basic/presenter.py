#!/usr/bin/env python3
"""
Basic Adjustment Presenter

UI 生成を担当し、BasicAdjustmentPlugin のロジックと CustomTkinter 依存を分離する
"""

from __future__ import annotations

from typing import Dict, Any
import customtkinter as ctk

from core.plugin_base import PluginUIHelper
from utils.smart_slider import SmartSlider

if False:
    # 型チェック用（循環参照を避ける）
    from .basic_plugin import BasicAdjustmentPlugin


class BasicAdjustmentPresenter:
    """基本調整プラグインの UI を構築する Presenter"""

    def __init__(self, plugin: "BasicAdjustmentPlugin") -> None:
        self.plugin = plugin
        self.sliders: Dict[str, Any] = {}
        self.labels: Dict[str, Any] = {}
        self.buttons: Dict[str, Any] = {}

    def build(self, parent: ctk.CTkFrame) -> None:
        """UI を構築"""
        self.sliders.clear()
        self.labels.clear()
        self.buttons.clear()

        # 明度・コントラスト・彩度スライダー
        for key, text, handler in [
            ("brightness", "明度調整", self.plugin._on_brightness_change),
            ("contrast", "コントラスト調整", self.plugin._on_contrast_change),
            ("saturation", "彩度調整", self.plugin._on_saturation_change),
        ]:
            slider, label, reset_btn = SmartSlider.create_with_reset(
                parent=parent,
                text=text,
                from_=-100,
                to=100,
                default_value=0,
                command=handler,
                value_format="{:.0f}",
                value_type=int
            )
            self.sliders[key] = slider
            self.labels[key] = label
            self.buttons[f"reset_{key}"] = reset_btn

        # Level 3: プリセットUI
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(preset_frame, text="基本調整プリセット", font=("Arial", 11, "bold")).pack(anchor="w", padx=3, pady=(5, 0))

        preset_select_frame = ctk.CTkFrame(preset_frame)
        preset_select_frame.pack(fill="x", padx=5, pady=2)

        self.plugin._preset_var = ctk.StringVar(value="おまかせ調整")
        self.plugin._preset_menu = ctk.CTkOptionMenu(
            preset_select_frame,
            variable=self.plugin._preset_var,
            values=list(self.plugin._presets.keys()),
            command=self.plugin._on_preset_selected
        )
        self.plugin._preset_menu.pack(side="left", padx=(0, 5))

        self.buttons['load_preset'] = PluginUIHelper.create_button(
            preset_select_frame, text="適用", command=self.plugin._load_selected_preset, width=60
        )
        self.buttons['load_preset'].pack(side="left", padx=2)

        # 追加のプリセット操作は必要に応じて Presenter 側で拡張する

        # プラグインに UI 要素を渡す
        self.plugin.attach_ui(self.sliders, self.labels, self.buttons)
