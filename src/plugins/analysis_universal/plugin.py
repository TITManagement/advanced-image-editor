#!/usr/bin/env python3
"""
Universal Analysis Plugin - UniversalPluginBase使用

KISS原則に従った簡潔な実装
"""

import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.universal_plugin_base import UniversalPluginBase


class UniversalAnalysisPlugin(UniversalPluginBase):
    """Universal Analysis Plugin - 画像解析機能を提供"""
    
    def __init__(self):
        super().__init__("analysis", "1.0.0")
    
    def apply_filter(self, image: Image.Image, filter_type: str, **kwargs) -> Image.Image:
        """解析処理のメイン実装"""
        if not image:
            return image
            
        try:
            if filter_type == "histogram":
                return self._apply_histogram_analysis(image)
            elif filter_type == "rgb_histogram":
                return self._apply_rgb_histogram_analysis(image)
            elif filter_type == "sift":
                return self._apply_feature_detection(image, "sift")
            elif filter_type == "orb":
                return self._apply_feature_detection(image, "orb")
            elif filter_type == "dct":
                return self._apply_frequency_analysis(image, "dct")
            elif filter_type == "fft":
                return self._apply_frequency_analysis(image, "fft")
            elif filter_type == "noise":
                return self._apply_noise_analysis(image)
            elif filter_type == "blur":
                return self._apply_blur_analysis(image)
            else:
                return image
                
        except Exception as e:
            print(f"❌ 解析処理エラー ({filter_type}): {e}")
            return image
    
    def process_image(self, image: Image.Image) -> Image.Image:
        """基本パラメータによる画像処理（解析は個別ボタンのみ）"""
        return image
    
    def _apply_histogram_analysis(self, image: Image.Image) -> Image.Image:
        """ヒストグラム解析（OpenCV完全版）"""
        try:
            print("📊 ヒストグラム解析開始")
            img_array = np.array(image)
            
            # グレースケール変換
            if img_array.ndim == 3:
                img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                img_gray = img_array
            
            # ヒストグラム計算
            hist = cv2.calcHist([img_gray], [0], None, [256], [0,256])
            
            # ヒストグラム画像生成（元の実装と同じ）
            hist_img = np.full((100, 256, 3), 255, np.uint8)
            cv2.normalize(hist, hist, 0, 100, cv2.NORM_MINMAX)
            for x, y in enumerate(hist):
                cv2.line(hist_img, (x, 100), (x, 100-int(y)), (0,0,0), 1)
            
            print("✅ ヒストグラム解析完了")
            return Image.fromarray(hist_img)
        except Exception as e:
            print(f"❌ ヒストグラム解析エラー: {e}")
            return image
    
    def _apply_rgb_histogram_analysis(self, image: Image.Image) -> Image.Image:
        """RGBヒストグラム解析（OpenCV完全版）"""
        try:
            print("🌈 RGBヒストグラム解析開始")
            img_array = np.array(image)
            
            # RGB別ヒストグラム画像生成（元の実装と同じ）
            hist_img = np.full((100, 256, 3), 255, np.uint8)
            colors = [(255,0,0), (0,255,0), (0,0,255)]  # BGR順
            
            for i, col in enumerate(colors):
                hist = cv2.calcHist([img_array], [i], None, [256], [0,256])
                cv2.normalize(hist, hist, 0, 100, cv2.NORM_MINMAX)
                for x, y in enumerate(hist):
                    cv2.line(hist_img, (x, 100), (x, 100-int(y)), col, 1)
            
            print("✅ RGBヒストグラム解析完了")
            return Image.fromarray(hist_img)
        except Exception as e:
            print(f"❌ RGBヒストグラム解析エラー: {e}")
            return image
    
    def _apply_frequency_analysis(self, image: Image.Image, analysis_type: str) -> Image.Image:
        """周波数解析（OpenCV完全版）"""
        try:
            print(f"📈 {analysis_type.upper()}解析開始")
            img_gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            if analysis_type == 'dct':
                # DCT（元の実装と同じ）
                img_float = np.float32(img_gray) / 255.0
                original_shape = img_float.shape
                
                # 奇数サイズの場合、偶数サイズにパディング
                h, w = img_float.shape  # type: ignore
                new_h = h if h % 2 == 0 else h + 1
                new_w = w if w % 2 == 0 else w + 1
                
                if new_h != h or new_w != w:
                    padded_img = np.zeros((new_h, new_w), dtype=np.float32)  # type: ignore
                    padded_img[:h, :w] = img_float  # type: ignore
                    img_float = padded_img
                
                dct = cv2.dct(img_float)  # type: ignore
                dct_log = np.log(np.abs(dct) + 1e-5)  # type: ignore
                dct_norm = cv2.normalize(dct_log, None, 0, 255, cv2.NORM_MINMAX)  # type: ignore
                dct_img = np.uint8(dct_norm)  # type: ignore
                
                # 元のサイズに戻す
                if new_h != original_shape[0] or new_w != original_shape[1]:  # type: ignore
                    dct_img = dct_img[:original_shape[0], :original_shape[1]]  # type: ignore
                
                result = cv2.cvtColor(dct_img, cv2.COLOR_GRAY2RGB)  # type: ignore
                print("✅ DCT解析完了")
                return Image.fromarray(result)
                
            elif analysis_type == 'fft':
                # FFT（元の実装と同じ）
                f = np.fft.fft2(img_gray)  # type: ignore
                fshift = np.fft.fftshift(f)  # type: ignore
                magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-5)  # type: ignore
                mag_norm = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX)  # type: ignore
                mag_img = np.uint8(mag_norm)  # type: ignore
                result = cv2.cvtColor(mag_img, cv2.COLOR_GRAY2RGB)  # type: ignore
                print("✅ FFT解析完了")
                return Image.fromarray(result)
                
        except Exception as e:
            print(f"❌ {analysis_type.upper()}解析エラー: {e}")
        return image
    
    def _apply_noise_analysis(self, image: Image.Image) -> Image.Image:
        """ノイズ解析（OpenCV完全版）"""
        try:
            print("🔍 ノイズ解析開始")
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # ノイズレベル計算（元の実装と同じ）
            noise_level = np.std(gray.astype(np.float32))
            status = "高" if noise_level > 50 else "中" if noise_level > 25 else "低"
            color = (255,0,0) if noise_level > 50 else (255,255,0) if noise_level > 25 else (0,255,0)
            
            # 結果画像に情報描画
            result = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result, f"Noise: {status} ({noise_level:.1f})", (10,30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            print("✅ ノイズ解析完了")
            return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"❌ ノイズ解析エラー: {e}")
            return image
    
    def _apply_blur_analysis(self, image: Image.Image) -> Image.Image:
        """ブラー解析（OpenCV完全版）"""
        try:
            print("💫 ブラー解析開始")
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # ブラー度計算（元の実装と同じ）
            blur_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            status = "強" if blur_var < 50 else "中" if blur_var < 150 else "弱"
            color = (255,0,0) if blur_var < 50 else (255,255,0) if blur_var < 150 else (0,255,0)
            
            # 結果画像に情報描画
            result = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            cv2.putText(result, f"Blur: {status} ({blur_var:.1f})", (10,30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            print("✅ ブラー解析完了")
            return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"❌ ブラー解析エラー: {e}")
            return image
    
    def _apply_feature_detection(self, image: Image.Image, feature_type: str) -> Image.Image:
        """特徴点検出（OpenCV完全版）"""
        try:
            print(f"🎯 {feature_type.upper()}特徴点検出開始")
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            keypoints = []
            
            # 特徴点検出（元の実装と同じ）
            if feature_type == "sift" and hasattr(cv2, "SIFT_create"):
                sift = cv2.SIFT_create()  # type: ignore
                keypoints = sift.detect(gray, None)  # type: ignore
            elif feature_type == "orb" and hasattr(cv2, "ORB_create"):
                orb = cv2.ORB_create()  # type: ignore
                keypoints = orb.detect(gray, None)  # type: ignore
            
            if keypoints:
                result = np.array(image)
                color = (0,255,0) if feature_type == "sift" else (255,0,0)
                
                # キーポイント描画
                for kp in keypoints:
                    x, y = int(kp.pt[0]), int(kp.pt[1])
                    radius = int(max(10, kp.size / 2))
                    cv2.circle(result, (x, y), radius, color, 2)
                
                print(f"✅ {feature_type.upper()}特徴点検出完了: {len(keypoints)}個")
                return Image.fromarray(result)
            else:
                print(f"⚠️ {feature_type.upper()}特徴点が見つかりませんでした")
                
        except Exception as e:
            print(f"❌ {feature_type.upper()}特徴点検出エラー: {e}")
        
        return image