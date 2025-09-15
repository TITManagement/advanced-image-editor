#!/usr/bin/env python3
"""
Advanced Image Editor - クロスプラットフォーム対応ユーティリティ
Windows, macOS, Linux での互換性を提供

【機能】
- OS固有のパス処理
- ファイルダイアログの最適化
- システム設定の取得
- パフォーマンス最適化
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import tkinter as tk
from tkinter import filedialog, messagebox

class PlatformManager:
    """クロスプラットフォーム対応管理クラス"""
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_mac = self.system == "Darwin"
        self.is_linux = self.system == "Linux"
        
        # OS固有の設定
        self.config = self._get_platform_config()
    
    def _get_platform_config(self) -> Dict[str, Any]:
        """OS固有の設定を取得"""
        base_config = {
            'default_image_dir': self.get_default_image_directory(),
            'temp_dir': self.get_temp_directory(),
            'config_dir': self.get_config_directory(),
            'file_extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'],
        }
        
        if self.is_windows:
            base_config.update({
                'path_separator': '\\',
                'line_ending': '\r\n',
                'font_scaling': 1.0,
                'dpi_aware': True,
            })
        elif self.is_mac:
            base_config.update({
                'path_separator': '/',
                'line_ending': '\n',
                'font_scaling': 1.0,
                'retina_support': True,
            })
        else:  # Linux
            base_config.update({
                'path_separator': '/',
                'line_ending': '\n',
                'font_scaling': self._get_linux_font_scaling(),
                'desktop_environment': os.environ.get('XDG_CURRENT_DESKTOP', 'unknown'),
            })
        
        return base_config
    
    def get_default_image_directory(self) -> Path:
        """OS別のデフォルト画像ディレクトリを取得"""
        if self.is_windows:
            return Path.home() / "Pictures"
        elif self.is_mac:
            return Path.home() / "Pictures"
        else:  # Linux
            # XDG Base Directory に従う
            pictures_dir = os.environ.get('XDG_PICTURES_DIR')
            if pictures_dir:
                return Path(pictures_dir)
            return Path.home() / "Pictures"
    
    def get_temp_directory(self) -> Path:
        """OS別の一時ディレクトリを取得"""
        import tempfile
        return Path(tempfile.gettempdir()) / "advanced_image_editor"
    
    def get_config_directory(self) -> Path:
        """OS別の設定ディレクトリを取得"""
        try:
            import platformdirs
            return Path(platformdirs.user_config_dir("advanced-image-editor", "TITManagement"))
        except ImportError:
            # fallback
            if self.is_windows:
                return Path.home() / "AppData" / "Roaming" / "AdvancedImageEditor"
            elif self.is_mac:
                return Path.home() / "Library" / "Application Support" / "AdvancedImageEditor"
            else:  # Linux
                return Path.home() / ".config" / "advanced-image-editor"
    
    def _get_linux_font_scaling(self) -> float:
        """Linux フォントスケーリング取得"""
        try:
            # GNOME/GTK の設定を確認
            import subprocess
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'text-scaling-factor'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        return 1.0
    
    def optimize_file_dialog(self, 
                           title: str = "ファイルを選択",
                           filetypes: Optional[list] = None,
                           initial_dir: Optional[Path] = None) -> Tuple[str, ...]:
        """OS最適化されたファイルダイアログ"""
        if filetypes is None:
            filetypes = [
                ("画像ファイル", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("すべてのファイル", "*.*")
            ]
        
        if initial_dir is None:
            initial_dir = self.get_default_image_directory()
        
        # OS固有の最適化
        if self.is_windows:
            # Windows: ネイティブダイアログ使用
            return filedialog.askopenfilenames(
                title=title,
                filetypes=filetypes,
                initialdir=str(initial_dir)
            )
        elif self.is_mac:
            # macOS: ネイティブダイアログ使用
            return filedialog.askopenfilenames(
                title=title,
                filetypes=filetypes,
                initialdir=str(initial_dir)
            )
        else:  # Linux
            # Linux: デスクトップ環境に応じた最適化
            return filedialog.askopenfilenames(
                title=title,
                filetypes=filetypes,
                initialdir=str(initial_dir)
            )
    
    def optimize_save_dialog(self,
                           title: str = "名前を付けて保存",
                           filetypes: Optional[list] = None,
                           initial_dir: Optional[Path] = None,
                           default_extension: str = ".jpg") -> Optional[str]:
        """OS最適化された保存ダイアログ"""
        if filetypes is None:
            filetypes = [
                ("JPEG", "*.jpg"),
                ("PNG", "*.png"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tiff")
            ]
        
        if initial_dir is None:
            initial_dir = self.get_default_image_directory()
        
        return filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            initialdir=str(initial_dir),
            defaultextension=default_extension
        )
    
    def show_platform_optimized_messagebox(self,
                                         title: str,
                                         message: str,
                                         type_: str = "info") -> str:
        """OS最適化されたメッセージボックス"""
        if type_ == "info":
            return messagebox.showinfo(title, message)
        elif type_ == "warning":
            return messagebox.showwarning(title, message)
        elif type_ == "error":
            return messagebox.showerror(title, message)
        elif type_ == "question":
            return messagebox.askquestion(title, message)
        else:
            return messagebox.showinfo(title, message)
    
    def get_system_dpi(self) -> float:
        """システムDPI取得"""
        try:
            if self.is_windows:
                import ctypes
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                dc = user32.GetDC(0)
                dpi = ctypes.windll.gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
                user32.ReleaseDC(0, dc)
                return dpi / 96.0
            elif self.is_mac:
                # macOS: Retinaディスプレイ対応
                import subprocess
                result = subprocess.run(
                    ['system_profiler', 'SPDisplaysDataType'],
                    capture_output=True, text=True
                )
                if "Retina" in result.stdout:
                    return 2.0
                return 1.0
            else:  # Linux
                # X11 DPI 取得
                try:
                    import subprocess
                    result = subprocess.run(
                        ['xdpyinfo'], capture_output=True, text=True
                    )
                    for line in result.stdout.split('\n'):
                        if 'resolution:' in line:
                            dpi_str = line.split('x')[0].split()[-1]
                            return float(dpi_str) / 96.0
                except Exception:
                    pass
        except Exception:
            pass
        return 1.0
    
    def create_directories(self):
        """必要なディレクトリを作成"""
        dirs_to_create = [
            self.config['temp_dir'],
            self.config['config_dir'],
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """メモリ使用量取得"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'rss_mb': 0, 'vms_mb': 0, 'percent': 0}
    
    def optimize_for_performance(self) -> Dict[str, Any]:
        """パフォーマンス最適化設定"""
        optimizations = {
            'thread_count': os.cpu_count() or 4,
            'memory_limit_mb': 512,
            'cache_size_mb': 128,
        }
        
        if self.is_windows:
            optimizations.update({
                'use_hardware_acceleration': True,
                'process_priority': 'normal',
            })
        elif self.is_mac:
            optimizations.update({
                'use_metal': True,
                'energy_efficient': True,
            })
        else:  # Linux
            optimizations.update({
                'use_opengl': True,
                'compositor_aware': True,
            })
        
        return optimizations

# グローバルインスタンス
platform_manager = PlatformManager()