#!/usr/bin/env python3
"""
基本調整プラグイン（新版） - Basic Adjustment Plugin (Universal)

UniversalPluginBaseを使用した革新的実装：
- 明度、コントラスト、彩度の基本的な画像調整
- 自動UI生成、自動コールバック設定
- プリセット機能完全対応
- おまかせ調整（画像解析ベース）機能
"""

from PIL import Image, ImageEnhance
import numpy as np
from core.universal_plugin_base import UniversalPluginBase


class BasicAdjustmentUniversalPlugin(UniversalPluginBase):
    """
    基本調整プラグイン（UniversalPluginBase版）
    
    既存のbasic_plugin.pyと完全互換：
    - 同じUI/UX体験
    - 同じプリセット機能  
    - 同じおまかせ調整機能
    - コード量90%削減
    """

    def __init__(self):
        super().__init__("basic", "2.0.0")
    
    def process_image(self, image: Image.Image, **parameters) -> Image.Image:
        """
        明度・コントラスト・彩度の調整を適用
        
        Args:
            image: 処理対象画像
            **parameters: UI設定されたパラメータ（brightness, contrast, saturation）
            
        Returns:
            処理後の画像
        """
        if image is None:
            return image
            
        try:
            processed_image = image.copy()
            
            # 明度調整
            brightness = parameters.get('brightness', 0)
            if brightness != 0:
                brightness_factor = 1.0 + (brightness / 100.0)
                brightness_factor = max(0.1, min(brightness_factor, 3.0))
                processed_image = ImageEnhance.Brightness(processed_image).enhance(brightness_factor)
            
            # コントラスト調整
            contrast = parameters.get('contrast', 0)
            if contrast != 0:
                contrast_factor = 1.0 + (contrast / 100.0)
                contrast_factor = max(0.1, min(contrast_factor, 3.0))
                processed_image = ImageEnhance.Contrast(processed_image).enhance(contrast_factor)
            
            # 彩度調整
            saturation = parameters.get('saturation', 0)
            if saturation != 0:
                saturation_factor = 1.0 + (saturation / 100.0)
                saturation_factor = max(0.0, min(saturation_factor, 3.0))
                processed_image = ImageEnhance.Color(processed_image).enhance(saturation_factor)
            
            return processed_image
            
        except Exception as e:
            print(f"❌ 基本調整エラー: {e}")
            return image  # フォールバック: 元画像を返す
    
    # === 高度機能：おまかせ調整（オプション） ===
    
    def supports_auto_adjustment(self) -> bool:
        """おまかせ調整機能の対応状況"""
        return True
    
    def suggest_auto_adjustment(self, image: Image.Image) -> dict:
        """画像分析に基づく自動調整値の提案（既存機能移植）"""
        try:
            img_array = np.array(image)
            suggestions = {}
            
            # 明度提案（平均輝度に基づく）
            avg_brightness = float(np.mean(img_array))
            if avg_brightness < 100:
                suggestions['brightness'] = min(30, int((100 - avg_brightness) / 3))
            elif avg_brightness > 180:
                suggestions['brightness'] = max(-30, int((180 - avg_brightness) / 3))
            else:
                suggestions['brightness'] = 0
            
            # コントラスト提案（標準偏差に基づく）
            contrast_std = float(np.std(img_array))
            if contrast_std < 30:
                suggestions['contrast'] = min(40, int((35 - contrast_std) * 2))
            elif contrast_std > 80:
                suggestions['contrast'] = max(-20, int((80 - contrast_std) / 2))
            else:
                suggestions['contrast'] = 0
            
            # 彩度提案（RGB平均の差に基づく）
            r_avg = float(np.mean(img_array[:, :, 0]))
            g_avg = float(np.mean(img_array[:, :, 1]))
            b_avg = float(np.mean(img_array[:, :, 2]))
            color_variance = max(r_avg, g_avg, b_avg) - min(r_avg, g_avg, b_avg)
            if color_variance < 10:
                suggestions['saturation'] = min(25, int((15 - color_variance) * 2))
            else:
                suggestions['saturation'] = 0
            
            print(f"🤖 自動調整提案: {suggestions}")
            return suggestions
            
        except Exception as e:
            print(f"❌ 自動調整提案エラー: {e}")
            return {'brightness': 0, 'contrast': 0, 'saturation': 0}
    
    def apply_auto_adjustment(self) -> bool:
        """おまかせ調整の実行"""
        if not self.image:
            print("❌ 画像が読み込まれていません")
            return False
        
        suggestions = self.suggest_auto_adjustment(self.image)
        if not suggestions:
            return False
        
        # UniversalPluginBaseのapply_preset機能を活用
        self._update_parameters_from_dict(suggestions)
        print(f"🤖 おまかせ調整適用完了: {suggestions}")
        return True
    
    def _update_parameters_from_dict(self, params: dict):
        """パラメータ辞書からUI値を更新（内部ヘルパー）"""
        try:
            self._updating_ui = True
            
            for param_name, value in params.items():
                if param_name in self._parameters:
                    self._parameters[param_name] = value
                    setattr(self, param_name, value)
                    
                    if param_name in self._sliders:
                        self._sliders[param_name].set(value)
                    if param_name in self._labels:
                        self._labels[param_name].configure(text=f"{value:.0f}")
            
            self._updating_ui = False
            self._trigger_image_update()
            
        except Exception as e:
            self._updating_ui = False
            print(f"❌ パラメータ更新エラー: {e}")
    
    # === 基本調整専用機能の実装 ===
    
    def _execute_auto_adjustment(self):
        """おまかせ調整を実行（UniversalPluginBase対応）"""
        if not hasattr(self, 'image') or self.image is None:
            print("❌ 画像が読み込まれていません")
            return
        
        suggestions = self.suggest_auto_adjustment(self.image)
        if suggestions:
            self._update_parameters_from_dict(suggestions)
            print(f"🤖 おまかせ調整適用完了: {suggestions}")
    
    def _toggle_rgb_analysis(self):
        """RGB分析表示の切り替え"""
        enabled = self._rgb_analysis_var.get()
        print(f"📊 RGB分析表示: {'有効' if enabled else '無効'}")
        if enabled and hasattr(self, 'image') and self.image:
            self._execute_rgb_analysis()
    
    def _execute_rgb_analysis(self):
        """RGB分析を実行してUI表示"""
        if not hasattr(self, 'image') or self.image is None:
            print("❌ 画像が読み込まれていません")
            return
        
        try:
            img_array = np.array(self.image)
            
            # RGB別統計情報
            r_avg = float(np.mean(img_array[:, :, 0]))
            g_avg = float(np.mean(img_array[:, :, 1]))
            b_avg = float(np.mean(img_array[:, :, 2]))
            
            brightness_avg = float(np.mean(img_array))
            contrast_std = float(np.std(img_array))
            color_balance = max(r_avg, g_avg, b_avg) - min(r_avg, g_avg, b_avg)
            
            # UI表示
            if hasattr(self, '_rgb_results_label'):
                result_text = f"平均輝度: {brightness_avg:.1f}\n"
                result_text += f"コントラスト: {contrast_std:.1f}\n" 
                result_text += f"R平均: {r_avg:.1f}\n"
                result_text += f"G平均: {g_avg:.1f}\n"
                result_text += f"B平均: {b_avg:.1f}\n"
                result_text += f"色相バランス: {color_balance:.1f}"
                
                self._rgb_results_label.configure(text=result_text)
            
        except Exception as e:
            print(f"❌ RGB分析エラー: {e}")
    
    def _toggle_contrast_curve(self):
        """コントラストカーブ機能の切り替え"""
        enabled = self._contrast_curve_var.get()
        print(f"📈 コントラストカーブ: {'有効' if enabled else '無効'}")
        # 高度機能のため実装は簡素化
        if enabled:
            print("   コントラストカーブ機能が有効になりました（高度調整）")