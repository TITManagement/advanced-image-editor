#!/usr/bin/env python3
"""
ブラー解析プラグイン - Blur Analysis Plugin

画像のブラー（ぼかし）レベルを解析・表示
"""
import numpy as np
import cv2
from PIL import Image
import customtkinter as ctk
from typing import Dict, Any
from core.plugin_base import ImageProcessorPlugin, PluginUIHelper

class BlurAnalysisPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("blur_analysis", "1.0.0")
        self.image = None
        self.blur_level = None

    def get_display_name(self) -> str:
        return "ブラー解析"

    def get_description(self) -> str:
        return "画像のブラー（ぼかし）レベルを解析・表示します"

    def setup_ui(self, parent: ctk.CTkFrame) -> None:
        """ブラー解析UI生成"""
        self._buttons = {}
        blur_frame = ctk.CTkFrame(parent)
        blur_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(blur_frame, text="ブラー解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        row_blur = ctk.CTkFrame(blur_frame)
        row_blur.pack(fill="x", padx=5, pady=2)
        self._buttons['blur'] = ctk.CTkButton(row_blur, text="ブラー解析", command=self._on_blur_button)
        self._buttons['blur'].pack(side="left", padx=(0, 5))
        self._buttons['undo_blur'] = ctk.CTkButton(row_blur, text="🔄 取消", command=self._undo_blur)
        self._buttons['undo_blur'].pack(side="left")
        self._buttons['undo_blur'].configure(state="disabled")

    def set_image(self, image: Image.Image):
        self.image = image

    def _on_blur_button(self):
        print("[DEBUG] ブラー解析ボタン押下")
        if self.image is not None:
            result_img = self.process_image(self.image)
            if hasattr(self, 'display_image_callback'):
                self.display_image_callback(result_img)
            self._buttons['undo_blur'].configure(state="normal")
        else:
            print("self.image is None, 処理をスキップ")

    def _undo_blur(self):
        print("[DEBUG] ブラー解析取消ボタン押下")
        if self.image is not None and hasattr(self, 'display_image_callback'):
            self.display_image_callback(self.image)
        self._buttons['undo_blur'].configure(state="disabled")

    def set_display_image_callback(self, callback):
        self.display_image_callback = callback

    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """ブラー解析を実行"""
        try:
            print("📷 ブラー検出開始")
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
            laplacian_var = laplacian.var()
            if laplacian_var < 100:
                blur_level = "高"
                color = (255, 0, 0)  # 赤
            elif laplacian_var < 500:
                blur_level = "中"
                color = (255, 255, 0)  # 黄
            else:
                blur_level = "低"
                color = (0, 255, 0)  # 緑
            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result_image, f"Blur Level: {blur_level} ({laplacian_var:.1f})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            print(f"✅ ブラー検出完了: レベル{blur_level} (分散: {laplacian_var:.1f})")
            return final_image
        except Exception as e:
            print(f"❌ ブラー検出エラー: {e}")
            return image

    def get_parameters(self) -> Dict[str, Any]:
        return {}
