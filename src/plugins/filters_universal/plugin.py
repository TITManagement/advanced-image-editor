#!/usr/bin/env python3
"""
Universal Filters Plugin - UniversalPluginBase使用

KISS原則に従った簡潔な実装
"""

import numpy as np
import cv2
from PIL import Image, ImageFilter
from typing import Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.universal_plugin_base import UniversalPluginBase


class UniversalFiltersPlugin(UniversalPluginBase):
    """Universal Filters Plugin - フィルター処理機能を提供"""
    
    def __init__(self):
        super().__init__("filters", "1.0.0")
    
    def apply_filter(self, image: Image.Image, filter_type: str, **kwargs) -> Image.Image:
        """フィルター処理のメイン実装"""
        if not image:
            return image
            
        try:
            if filter_type == "denoise":
                return self._apply_denoise_filter(image)
            elif filter_type == "emboss":
                return self._apply_emboss_filter(image)
            elif filter_type == "edge":
                return self._apply_edge_filter(image)
            elif filter_type in ["erosion", "dilation", "opening", "closing"]:
                return self._apply_morphology_filter(image, filter_type)
            elif filter_type == "contour":
                return self._apply_contour_filter(image)
            else:
                return image
                
        except Exception as e:
            print(f"❌ フィルター処理エラー ({filter_type}): {e}")
            return image
    
    def process_image(self, image: Image.Image, **parameters) -> Image.Image:
        """基本パラメータによる画像処理"""
        if not image:
            return image
            
        try:
            processed = image.copy()
            
            # ガウシアンブラーの適用
            blur_strength = parameters.get('blur_strength', self._parameters.get('blur_strength', 0))
            if blur_strength > 0:
                processed = self._apply_gaussian_blur(processed, blur_strength)
            
            # シャープニングの適用
            sharpen_strength = parameters.get('sharpen_strength', self._parameters.get('sharpen_strength', 0))
            if sharpen_strength > 0:
                processed = self._apply_sharpening(processed, sharpen_strength)
            
            return processed
            
        except Exception as e:
            print(f"❌ 画像処理エラー: {e}")
            return image
    
    def _apply_gaussian_blur(self, image: Image.Image, strength: int) -> Image.Image:
        """ガウシアンブラー適用"""
        try:
            kernel_size = int(strength * 2) + 1
            kernel_size = max(1, min(kernel_size, 51))
            
            if kernel_size <= 1:
                return image
            
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            blurred = cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
            return Image.fromarray(cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB))
            
        except Exception as e:
            print(f"❌ ガウシアンブラーエラー: {e}")
            return image
    
    def _apply_sharpening(self, image: Image.Image, strength: float) -> Image.Image:
        """シャープニング適用"""
        try:
            if strength <= 5:
                # 軽度シャープニング
                radius = min(2 + int(strength / 3), 5)
                percent = int((1.0 + strength / 2.0) * 150)
                threshold = max(0, int(strength / 5))
                return image.filter(ImageFilter.UnsharpMask(
                    radius=radius, percent=percent, threshold=threshold
                ))
            else:
                # 強度シャープニング
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                normalized_strength = (strength - 5) / 5.0
                kernel = np.array([
                    [-1, -1, -1],
                    [-1, 9 + normalized_strength * 8, -1],
                    [-1, -1, -1]
                ], dtype=np.float32)
                sharpened = cv2.filter2D(cv_image, -1, kernel)
                return Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
                
        except Exception as e:
            print(f"❌ シャープニングエラー: {e}")
            return image
    
    def _apply_denoise_filter(self, image: Image.Image) -> Image.Image:
        """ノイズ除去フィルター"""
        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            denoised = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
            return Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"❌ ノイズ除去エラー: {e}")
            return image
    
    def _apply_emboss_filter(self, image: Image.Image) -> Image.Image:
        """エンボスフィルター"""
        try:
            return image.filter(ImageFilter.EMBOSS)
        except Exception as e:
            print(f"❌ エンボスエラー: {e}")
            return image
    
    def _apply_edge_filter(self, image: Image.Image) -> Image.Image:
        """エッジ検出フィルター"""
        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(cv_image, 100, 200)
            edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
            return Image.fromarray(edges_rgb)
        except Exception as e:
            print(f"❌ エッジ検出エラー: {e}")
            return image
    
    def _apply_morphology_filter(self, image: Image.Image, operation: str) -> Image.Image:
        """モルフォロジー演算フィルター"""
        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            kernel_size = self._parameters.get('morph_kernel_size', 5)
            kernel = np.ones((kernel_size, kernel_size), np.uint8)
            
            if operation == "erosion":
                result = cv2.erode(gray_image, kernel, iterations=1)
            elif operation == "dilation":
                result = cv2.dilate(gray_image, kernel, iterations=1)
            elif operation == "opening":
                result = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
            elif operation == "closing":
                result = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
            else:
                result = gray_image
            
            result_rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            return Image.fromarray(result_rgb)
            
        except Exception as e:
            print(f"❌ モルフォロジー演算エラー ({operation}): {e}")
            return image
    
    def _apply_contour_filter(self, image: Image.Image) -> Image.Image:
        """輪郭検出フィルター"""
        try:
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # 小さい輪郭をフィルタリング
            filtered_contours = [c for c in contours if cv2.contourArea(c) > 100]
            
            result_image = cv_image.copy()
            cv2.drawContours(result_image, filtered_contours, -1, (0, 255, 0), 1)
            
            result_rgb = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
            return Image.fromarray(result_rgb)
            
        except Exception as e:
            print(f"❌ 輪郭検出エラー: {e}")
            return image