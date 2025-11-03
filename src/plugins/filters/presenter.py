#!/usr/bin/env python3
"""
Filter Processing Presenter

フィルタープラグインの UI を生成・管理し、ボタン状態の更新も引き受ける。
"""

from __future__ import annotations

from typing import Dict, Any, Optional
import customtkinter as ctk

from core.plugin_base import PluginUIHelper

if False:
    from .filters_plugin import FilterProcessingPlugin  # for type checking


class FilterProcessingPresenter:
    """フィルター処理プラグインの UI を構築する Presenter"""

    def __init__(self, plugin: "FilterProcessingPlugin") -> None:
        """Presenter を初期化し、UI ウィジェット参照の辞書を準備する。"""
        self.plugin = plugin
        self.sliders: Dict[str, Any] = {}
        self.labels: Dict[str, Any] = {}
        self.buttons: Dict[str, Any] = {}
        self.selectors: Dict[str, Any] = {}
        self._container: Optional[ctk.CTkFrame] = None
        self._after_target: Optional[Any] = None
        self.status_label: Optional[ctk.CTkLabel] = None

    def build(self, parent: ctk.CTkFrame) -> None:
        """
        タブ内にフィルター操作 UI を構築し、作成したウィジェットをプラグインへ渡す。
        """
        self.sliders.clear()
        self.labels.clear()
        self.buttons.clear()
        self.selectors.clear()
        self._container = parent
        self._after_target = parent  # CTkFrame は after を継承している

        # ブラー強度（1行配置）
        blur_slider, blur_label = PluginUIHelper.create_slider_row(
            parent=parent,
            text="ガウシアンブラー",
            from_=0,
            to=25,
            default_value=0,
            command=self.plugin._on_blur_change,
            value_format="{:.0f}",
            value_type=int
        )
        self.sliders['blur'] = blur_slider
        self.labels['blur'] = blur_label

        # シャープニング強度（1行配置）
        sharp_slider, sharp_label = PluginUIHelper.create_slider_row(
            parent=parent,
            text="シャープニング強度",
            from_=0.0,
            to=10.0,
            default_value=0.0,
            command=self.plugin._on_sharpen_change,
            value_format="{:.1f}",
            value_type=float
        )
        self.sliders['sharpen'] = sharp_slider
        self.labels['sharpen'] = sharp_label

        # 特殊フィルターセクション
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(filter_frame, text="特殊フィルター", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))

        denoise_section = ctk.CTkFrame(filter_frame)
        denoise_section.pack(fill="x", padx=5, pady=3)
        self._create_special_filter_buttons(denoise_section, [
            ("denoise", "ノイズ除去"),
            ("emboss", "エンボス"),
            ("edge", "エッジ検出"),
            ("opencv_dnn_sr", "OpenCV DNN超解像"),
            ("real_esrgan_sr", "Real-ESRGAN"),
        ])

        # 超解像設定
        sr_config_frame = ctk.CTkFrame(parent)
        sr_config_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(sr_config_frame, text="超解像設定", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))

        # OpenCV DNN 設定
        opencv_frame = ctk.CTkFrame(sr_config_frame)
        opencv_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(opencv_frame, text="OpenCV DNN", font=("Arial", 10)).pack(anchor="w", padx=3, pady=(3, 0))

        opencv_model_row = ctk.CTkFrame(opencv_frame)
        opencv_model_row.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(opencv_model_row, text="モデル", width=80, anchor="w").pack(side="left", padx=(0, 8))
        opencv_models = ["EDSR", "FSRCNN", "LapSRN", "ESPCN"]
        opencv_model_menu = ctk.CTkOptionMenu(
            opencv_model_row,
            values=opencv_models,
            command=self.plugin._on_opencv_model_change,
            width=140,
        )
        opencv_model_menu.pack(side="left", fill="x", expand=True)
        opencv_model_menu.set(self.plugin._opencv_sr_model_name.upper())
        self.selectors["opencv_model"] = opencv_model_menu

        opencv_scale_slider, opencv_scale_label = PluginUIHelper.create_slider_row(
            parent=opencv_frame,
            text="スケール",
            from_=1,
            to=4,
            default_value=self.plugin._opencv_sr_scale,
            command=self.plugin._on_opencv_scale_change,
            value_format="{:.0f}",
            value_type=int,
        )
        self.sliders["opencv_scale"] = opencv_scale_slider
        self.labels["opencv_scale"] = opencv_scale_label

        opencv_tile_slider, opencv_tile_label = PluginUIHelper.create_slider_row(
            parent=opencv_frame,
            text="タイルサイズ (CPU)",
            from_=0,
            to=512,
            default_value=self.plugin._opencv_sr_tile_size,
            command=self.plugin._on_opencv_tile_change,
            value_format="{:.0f}",
            value_type=int,
        )
        self.sliders["opencv_tile"] = opencv_tile_slider
        self.labels["opencv_tile"] = opencv_tile_label

        # Real-ESRGAN 設定
        realesr_frame = ctk.CTkFrame(sr_config_frame)
        realesr_frame.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(realesr_frame, text="Real-ESRGAN", font=("Arial", 10)).pack(anchor="w", padx=3, pady=(3, 0))

        real_model_row = ctk.CTkFrame(realesr_frame)
        real_model_row.pack(fill="x", padx=5, pady=3)
        ctk.CTkLabel(real_model_row, text="モデル", width=80, anchor="w").pack(side="left", padx=(0, 8))
        real_models = [
            "RealESRGAN_x4plus",
            "RealESRGAN_x4plus_anime_6B",
            "RealESRGAN_x2plus",
            "RealESRNet_x4plus",
        ]
        real_model_menu = ctk.CTkOptionMenu(
            real_model_row,
            values=real_models,
            command=self.plugin._on_real_esrgan_model_change,
            width=200,
        )
        real_model_menu.pack(side="left", fill="x", expand=True)
        real_model_menu.set(self.plugin._real_esrgan_model_name)
        self.selectors["real_esr_model"] = real_model_menu

        real_scale_slider, real_scale_label = PluginUIHelper.create_slider_row(
            parent=realesr_frame,
            text="スケール",
            from_=1,
            to=4,
            default_value=self.plugin._real_esrgan_scale,
            command=self.plugin._on_real_esrgan_scale_change,
            value_format="{:.0f}",
            value_type=int,
        )
        self.sliders["real_esr_scale"] = real_scale_slider
        self.labels["real_esr_scale"] = real_scale_label

        real_tile_slider, real_tile_label = PluginUIHelper.create_slider_row(
            parent=realesr_frame,
            text="タイルサイズ (CPU)",
            from_=0,
            to=512,
            default_value=self.plugin._real_esrgan_tile_size,
            command=self.plugin._on_real_esrgan_tile_change,
            value_format="{:.0f}",
            value_type=int,
        )
        self.sliders["real_esr_tile"] = real_tile_slider
        self.labels["real_esr_tile"] = real_tile_label

        # モルフォロジー演算
        morph_frame = ctk.CTkFrame(parent)
        morph_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(morph_frame, text="モルフォロジー演算", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))

        morph_slider, morph_label = PluginUIHelper.create_slider_row(
            parent=morph_frame,
            text="カーネルサイズ",
            from_=3,
            to=15,
            default_value=5,
            command=self.plugin._on_kernel_change,
            value_format="{:.0f}",
            value_type=int
        )
        self.sliders['kernel'] = morph_slider
        self.labels['kernel'] = morph_label

        morph_buttons_frame = ctk.CTkFrame(morph_frame)
        morph_buttons_frame.pack(fill="x", padx=5, pady=5)

        morph_ops_frame = ctk.CTkFrame(morph_buttons_frame)
        morph_ops_frame.pack(fill="x", pady=(0, 3))
        for morph_type, text in [
            ("erosion", "侵食"),
            ("dilation", "膨張"),
            ("opening", "開放"),
            ("closing", "閉鎖"),
        ]:
            btn = PluginUIHelper.create_button(
                morph_ops_frame,
                text=text,
                command=lambda mt=morph_type: self.plugin._apply_morphology(mt),
                width=80,
                auto_pack=False
            )
            btn.pack(side="left", padx=2, pady=3)
            self.buttons[morph_type] = btn

        morph_undo_frame = ctk.CTkFrame(morph_buttons_frame)
        morph_undo_frame.pack(fill="x")
        undo_morph = PluginUIHelper.create_button(
            morph_undo_frame,
            text="🔄 モルフォロジー取消",
            command=self.plugin._undo_morphology,
            width=180,
            auto_pack=False
        )
        undo_morph.pack(anchor="w", padx=5, pady=3)
        undo_morph.configure(state=ctk.DISABLED)
        self.buttons['undo_morphology'] = undo_morph

        # 輪郭検出
        contour_frame = ctk.CTkFrame(parent)
        contour_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(contour_frame, text="輪郭検出", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))

        contour_section = ctk.CTkFrame(contour_frame)
        contour_section.pack(fill="x", padx=5, pady=3)

        contour_btn = PluginUIHelper.create_button(
            contour_section,
            text="輪郭検出",
            command=self.plugin._apply_contour_detection,
            width=100,
            auto_pack=False
        )
        contour_btn.pack(side="left", padx=(0, 5), pady=3)
        self.buttons['contour'] = contour_btn

        undo_contour = PluginUIHelper.create_button(
            contour_section,
            text="🔄 取消",
            command=self.plugin._undo_contour,
            width=60,
            auto_pack=False
        )
        undo_contour.pack(side="left", pady=3)
        undo_contour.configure(state=ctk.DISABLED)
        self.buttons['undo_contour'] = undo_contour

        # ステータスメッセージ表示
        self.status_label = ctk.CTkLabel(
            parent,
            text="準備完了",
            anchor="w",
            text_color=("gray70", "gray40"),
        )
        self.status_label.pack(fill="x", padx=5, pady=(8, 0))

        # プラグインに UI 要素を引き渡す
        self.plugin.attach_ui(self.sliders, self.labels, self.buttons, self.selectors)

    def _create_special_filter_buttons(self, parent: ctk.CTkFrame, filters: list[tuple[str, str]]) -> None:
        """特殊フィルター用の適用・取消ボタン行を生成する。"""
        for filter_type, text in filters:
            row = ctk.CTkFrame(parent)
            row.pack(fill="x", padx=5, pady=2)

            if filter_type == "opencv_dnn_sr":
                apply_btn = PluginUIHelper.create_button(
                    row,
                    text=text,
                    command=self.plugin._apply_opencv_dnn_sr,
                    width=100,
                    auto_pack=False
                )
            elif filter_type == "real_esrgan_sr":
                apply_btn = PluginUIHelper.create_button(
                    row,
                    text=text,
                    command=self.plugin._apply_real_esrgan_sr,
                    width=100,
                    auto_pack=False
                )
            else:
                apply_btn = PluginUIHelper.create_button(
                    row,
                    text=text,
                    command=lambda ft=filter_type: self.plugin._apply_special_filter(ft),
                    width=100,
                    auto_pack=False
                )
            apply_btn.pack(side="left", padx=(0, 5), pady=3)
            self.buttons[filter_type] = apply_btn

            undo_btn = PluginUIHelper.create_button(
                row,
                text="🔄 取消",
                command=lambda ft=filter_type: self.plugin._undo_special_filter(ft),
                width=60,
                auto_pack=False
            )
            undo_btn.pack(side="left", pady=3)
            undo_btn.configure(state=ctk.DISABLED)
            self.buttons[f"undo_{filter_type}"] = undo_btn

    def set_status(self, message: str, state: str = "info") -> None:
        """
        ステータスラベルにメッセージを表示。

        Args:
            message: 表示するテキスト
            state: 表示状態 (idle/info/processing/success/error)
        """
        if not self.status_label:
            return

        palette = {
            "idle": ("gray70", "gray40"),
            "info": ("gray70", "gray40"),
            "processing": ("#fcd37d", "#ffb347"),
            "success": ("#72c472", "#4caf50"),
            "error": ("#f28b82", "#e57373"),
        }
        text_color = palette.get(state, palette["info"])
        try:
            self.status_label.configure(text=message, text_color=text_color)
            if hasattr(self.status_label, "update_idletasks"):
                self.status_label.update_idletasks()
        except Exception as exc:
            print(f"[DEBUG] ステータス更新失敗: {message} ({state}), error={exc}")

    def set_button_state(self, button_name: str, desired_state: str) -> bool:
        """
        指定されたボタンの state を UI スレッドで更新する。

        Returns:
            更新に成功した場合は True、ボタン未検出などで適用できなかった場合は False。
        """
        button = self.buttons.get(button_name)
        if not button:
            print(f"[DEBUG] presenter側でボタン未検出: {button_name}, keys={list(self.buttons.keys())}")
            return False

        def apply_state():
            before_state = getattr(button, "cget", lambda x: None)("state")
            command_attr = getattr(button, "_command", None)
            try:
                button.configure(state=desired_state)
                if hasattr(button, "update_idletasks"):
                    button.update_idletasks()
                elif hasattr(button, "update"):
                    button.update()
            except Exception as exc:
                print(f"[DEBUG] presenterでボタン状態更新失敗: {button_name} -> {desired_state}, error={exc}")
                return
            after_state = getattr(button, "cget", lambda x: None)("state")
            print(f"[DEBUG] presenterボタン状態更新: {button_name} {before_state} -> {after_state}, command={command_attr}")

        target = self._after_target or button
        try:
            if hasattr(target, "after"):
                target.after(0, apply_state)
                return True
        except Exception as exc:
            print(f"[DEBUG] presenter.after呼び出し失敗: {exc}")

        # after が利用できない場合はフォールバックとして直接実行
        try:
            apply_state()
            return True
        except Exception as exc:
            print(f"[DEBUG] presenter直接更新失敗: {button_name} -> {desired_state}, error={exc}")
            return False
