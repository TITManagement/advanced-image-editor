#!/usr/bin/env python3
"""
Density Adjustment Presenter

UI 構築を担当し、プラグインの処理ロジックから CustomTkinter 依存を分離する
"""

from __future__ import annotations

from typing import Dict, Any
import customtkinter as ctk

from core.plugin_base import PluginUIHelper
from utils.smart_slider import SmartSlider

if False:
    from .density_plugin import DensityAdjustmentPlugin  # 型チェック用

try:
    from ui.curve_editor import CurveEditor
except ImportError:
    CurveEditor = None  # type: ignore


class DensityAdjustmentPresenter:
    """濃度調整プラグイン用 Presenter"""

    def __init__(self, plugin: "DensityAdjustmentPlugin", curve_editor_available: bool) -> None:
        self.plugin = plugin
        self.curve_editor_available = curve_editor_available
        self.sliders: Dict[str, Any] = {}
        self.labels: Dict[str, Any] = {}
        self.buttons: Dict[str, Any] = {}

    def build(self, parent: ctk.CTkFrame) -> None:
        """UI を構築"""
        self.sliders.clear()
        self.labels.clear()
        self.buttons.clear()

        # カーブエディタ
        if self.curve_editor_available and CurveEditor is not None:
            self.plugin.gamma_curve_frame = ctk.CTkFrame(parent)
            self.plugin.gamma_curve_frame.pack(side="top", fill="x", padx=5, pady=2)
            self.plugin.curve_editor = CurveEditor(self.plugin.gamma_curve_frame)
            self.plugin.curve_editor.pack(fill="x", padx=5, pady=2)
            self.plugin.curve_editor.on_curve_change = self.plugin._on_curve_change

        # シャドウ・ハイライト・色温度スライダー
        for key, text, handler in [
            ("shadow", "シャドウ調整", self.plugin._on_shadow_change),
            ("highlight", "ハイライト調整", self.plugin._on_highlight_change),
            ("temperature", "色温度調整", self.plugin._on_temperature_change),
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

        # 2値化スライダー
        slider, label, reset_btn = SmartSlider.create_with_reset(
            parent=parent,
            text="2値化調整",
            from_=0,
            to=255,
            default_value=127,
            command=self.plugin._on_threshold_change,
            value_format="{:.0f}",
            value_type=int,
            reset_text="初期化"
        )
        self.sliders['threshold'] = slider
        self.labels['threshold'] = label
        self.buttons['reset_threshold'] = reset_btn

        binary_buttons = ctk.CTkFrame(parent)
        binary_buttons.pack(fill="x", padx=5, pady=(2, 4))
        binary_buttons.grid_columnconfigure(0, weight=1)

        binary_button = ctk.CTkButton(
            binary_buttons,
            text="2値化実行",
            command=self.plugin._on_apply_binary_threshold,
            width=120,
            font=("Arial", 11)
        )
        binary_button.grid(row=0, column=0, padx=(0, 6), pady=3, sticky="w")
        self.buttons['binary'] = binary_button

        undo_binary = ctk.CTkButton(
            binary_buttons,
            text="取消",
            command=self.plugin._on_undo_binary_threshold,
            width=80,
            font=("Arial", 11)
        )
        undo_binary.grid(row=0, column=1, padx=(0, 3), pady=3, sticky="w")
        undo_binary.configure(state=ctk.DISABLED)
        self.buttons['undo_binary'] = undo_binary

        # ヒストグラム均等化
        hist_row = ctk.CTkFrame(parent)
        hist_row.pack(fill="x", padx=5, pady=(10, 2))
        hist_row.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hist_row, text="ヒストグラム均等化", font=("Arial", 11)).grid(row=0, column=0, padx=(3, 8), pady=3, sticky="w")

        hist_button = ctk.CTkButton(
            hist_row,
            text="実行",
            command=self.plugin._on_histogram_equalization,
            width=80,
            font=("Arial", 11)
        )
        hist_button.grid(row=0, column=1, padx=(0, 5), pady=3, sticky="w")
        self.buttons['histogram'] = hist_button

        undo_hist = ctk.CTkButton(
            hist_row,
            text="取消",
            command=self.plugin._on_undo_histogram_equalization,
            width=80,
            font=("Arial", 11)
        )
        undo_hist.grid(row=0, column=2, padx=(0, 3), pady=3, sticky="w")
        undo_hist.configure(state=ctk.DISABLED)
        self.buttons['undo_histogram'] = undo_hist

        # 一括リセット
        ctk.CTkLabel(parent, text="一括操作", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(10, 0))
        row_reset = ctk.CTkFrame(parent)
        row_reset.pack(side="top", fill="x", padx=5, pady=2)
        reset_btn = PluginUIHelper.create_button(
            row_reset,
            text="全リセット",
            command=self.plugin.reset_parameters
        )
        self.buttons['reset'] = reset_btn

        # プリセット管理
        preset_frame = ctk.CTkFrame(parent)
        preset_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(preset_frame, text="プリセット管理 (Level 3)", font=("Arial", 11, "bold")).pack(anchor="w", padx=3, pady=(5, 0))

        preset_controls = ctk.CTkFrame(preset_frame)
        preset_controls.pack(fill="x", padx=5, pady=2)

        self.plugin._preset_entry = ctk.CTkEntry(preset_controls, placeholder_text="プリセット名")
        self.plugin._preset_entry.pack(side="left", padx=(0, 5))

        save_btn = PluginUIHelper.create_button(
            preset_controls, text="保存", command=self.plugin._save_current_preset, width=60
        )
        save_btn.pack(side="left", padx=2)
        self.buttons['save_preset'] = save_btn

        load_btn = PluginUIHelper.create_button(
            preset_controls, text="読込", command=self.plugin._load_selected_preset, width=60
        )
        load_btn.pack(side="left", padx=2)
        self.buttons['load_preset'] = load_btn

        # 履歴管理
        history_frame = ctk.CTkFrame(parent)
        history_frame.pack(fill="x", padx=5, pady=2)

        history_controls = ctk.CTkFrame(history_frame)
        history_controls.pack(fill="x", padx=5, pady=2)

        undo_btn = PluginUIHelper.create_button(
            history_controls, text="↶ Undo", command=self.plugin.undo_parameters, width=80
        )
        undo_btn.pack(side="left", padx=2)
        self.buttons['undo'] = undo_btn

        redo_btn = PluginUIHelper.create_button(
            history_controls, text="↷ Redo", command=self.plugin.redo_parameters, width=80
        )
        redo_btn.pack(side="left", padx=2)
        self.buttons['redo'] = redo_btn

        # 高度オプション
        advanced_frame = ctk.CTkFrame(parent)
        advanced_frame.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(advanced_frame, text="高度オプション", font=("Arial", 10)).pack(anchor="w", padx=3, pady=(2, 0))

        options_row = ctk.CTkFrame(advanced_frame)
        options_row.pack(fill="x", padx=5, pady=2)

        self.plugin._realtime_preview_var = ctk.BooleanVar(value=self.plugin._preview_enabled)
        self.plugin._realtime_checkbox = ctk.CTkCheckBox(
            options_row, text="リアルタイム", variable=self.plugin._realtime_preview_var,
            command=self.plugin._toggle_realtime_preview
        )
        self.plugin._realtime_checkbox.pack(side="left", padx=5)

        self.plugin._histogram_var = ctk.BooleanVar(value=self.plugin._show_histogram)
        self.plugin._histogram_checkbox = ctk.CTkCheckBox(
            options_row, text="ヒストグラム", variable=self.plugin._histogram_var,
            command=self.plugin._toggle_histogram_display
        )
        self.plugin._histogram_checkbox.pack(side="left", padx=5)

        manual_btn = PluginUIHelper.create_button(
            options_row, text="更新", command=self.plugin._manual_update, width=50
        )
        manual_btn.pack(side="left", padx=5)
        self.buttons['manual_update'] = manual_btn

        # ヒストグラム表示エリア
        self.plugin._create_histogram_display(parent)

        # UI 要素をプラグインへ渡す
        self.plugin.attach_ui(self.sliders, self.labels, self.buttons)

        # 初期状態を履歴へ保存
        self.plugin._save_parameter_state()
