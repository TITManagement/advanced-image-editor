#!/usr/bin/env python3
"""
ノイズ解析プラグイン - Noise Analysis Plugin

画像のノイズレベルを解析・表示
"""
import numpy as np
import cv2
from PIL import Image
import customtkinter as ctk
from typing import Dict, Any
from core.plugin_base import ImageProcessorPlugin

class NoiseAnalysisPlugin(ImageProcessorPlugin):
    def __init__(self):
        super().__init__("noise_analysis", "1.0.0")
        self.image = None
        self.noise_level = None
        self._buttons = {}
        self.display_image_callback = None

    def get_display_name(self) -> str:
        return "ノイズ解析"

    def get_description(self) -> str:
        return "画像のノイズレベルを解析・表示します"

    def setup_ui(self, parent: ctk.CTkFrame) -> None:
        """ノイズ解析UI生成"""
        noise_frame = ctk.CTkFrame(parent)
        noise_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(noise_frame, text="ノイズ解析", font=("Arial", 11)).pack(anchor="w", padx=3, pady=(5, 0))
        row_noise = ctk.CTkFrame(noise_frame)
        row_noise.pack(fill="x", padx=5, pady=2)
        self._buttons['noise'] = ctk.CTkButton(row_noise, text="ノイズ解析", command=self._on_noise_button)
        self._buttons['noise'].pack(side="left", padx=(0, 5))
        self._buttons['undo_noise'] = ctk.CTkButton(row_noise, text="🔄 取消", command=self._undo_noise)
        self._buttons['undo_noise'].pack(side="left")
        self._buttons['undo_noise'].configure(state="disabled")

    def set_image(self, image: Image.Image):
        self.image = image

    def set_display_image_callback(self, callback):
        self.display_image_callback = callback

    def _on_noise_button(self):
        print("[DEBUG] ノイズ解析ボタン押下")
        if self.image is not None:
            result_img = self.process_image(self.image)
            if self.display_image_callback:
                self.display_image_callback(result_img)
            self._buttons['undo_noise'].configure(state="normal")
        else:
            print("self.image is None, 処理をスキップ")

    def _undo_noise(self):
        print("[DEBUG] ノイズ解析取消ボタン押下")
        if self.image is not None and self.display_image_callback:
            self.display_image_callback(self.image)
        self._buttons['undo_noise'].configure(state="disabled")

    def process_image(self, image: Image.Image, **params) -> Image.Image:
        """ノイズ解析を実行"""
        try:
            print("📈 ノイズ解析開始")
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            noise_level = np.std(np.array(gray_image, dtype=np.float32))
            if noise_level > 50:
                noise_status = "高"
                color = (255, 0, 0)  # 赤
            elif noise_level > 25:
                noise_status = "中"
                color = (255, 255, 0)  # 黄
            else:
                noise_status = "低"
                color = (0, 255, 0)  # 緑
            result_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result_image, f"Noise Level: {noise_status} ({noise_level:.1f})", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            final_image = Image.fromarray(result_rgb)
            print(f"✅ ノイズ解析完了: レベル{noise_status} (標準偏差: {noise_level:.1f})")
            return final_image
        except Exception as e:
            print(f"❌ ノイズ解析エラー: {e}")
            return image

    def get_parameters(self) -> Dict[str, Any]:
        return {}
