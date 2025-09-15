#!/usr/bin/env python3
"""
Advanced Image Editor - クロスプラットフォーム配布スクリプト
Windows, macOS, Linux での配布パッケージ作成

【機能】
- ワンクリックインストーラー生成
- OS別バイナリパッケージ作成
- 依存関係バンドリング
- 自動配布
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Optional

class DistributionBuilder:
    """配布パッケージビルダー"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.system = platform.system()
        self.machine = platform.machine()
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
        # OS固有設定
        self.build_config = self._get_build_config()
    
    def _get_build_config(self) -> Dict[str, any]:
        """OS別ビルド設定"""
        base_config = {
            'app_name': 'AdvancedImageEditor',
            'version': '1.0.0',
            'author': 'TITManagement',
            'description': 'Advanced Image Editor with Plugin System',
        }
        
        if self.system == 'Windows':
            base_config.update({
                'executable_name': 'AdvancedImageEditor.exe',
                'installer_name': 'AdvancedImageEditor-Setup.exe',
                'icon_file': 'assets/icon.ico',
                'installer_type': 'nsis',
            })
        elif self.system == 'Darwin':  # macOS
            base_config.update({
                'app_bundle': 'AdvancedImageEditor.app',
                'dmg_name': 'AdvancedImageEditor.dmg',
                'icon_file': 'assets/icon.icns',
                'installer_type': 'dmg',
            })
        else:  # Linux
            base_config.update({
                'executable_name': 'advanced-image-editor',
                'package_name': 'advanced-image-editor',
                'icon_file': 'assets/icon.png',
                'installer_type': 'appimage',
            })
        
        return base_config
    
    def build_standalone_executable(self):
        """スタンドアロン実行ファイル作成"""
        print(f"🔨 {self.system} 用スタンドアロン実行ファイルを作成中...")
        
        # PyInstaller設定
        pyinstaller_args = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', self.build_config['app_name'],
            '--distpath', str(self.dist_dir),
            '--workpath', str(self.build_dir),
            str(self.project_root / 'src' / 'main_plugin.py')
        ]
        
        # OS固有のオプション追加
        if self.system == 'Windows':
            pyinstaller_args.extend([
                '--add-data', f'{self.project_root}/src;src',
                '--hidden-import', 'customtkinter',
                '--hidden-import', 'cv2',
                '--hidden-import', 'PIL',
            ])
            if (self.project_root / self.build_config['icon_file']).exists():
                pyinstaller_args.extend(['--icon', self.build_config['icon_file']])
        
        elif self.system == 'Darwin':  # macOS
            pyinstaller_args.extend([
                '--add-data', f'{self.project_root}/src:src',
                '--osx-bundle-identifier', 'com.titmanagement.advancedimageeditor',
            ])
            if (self.project_root / self.build_config['icon_file']).exists():
                pyinstaller_args.extend(['--icon', self.build_config['icon_file']])
        
        else:  # Linux
            pyinstaller_args.extend([
                '--add-data', f'{self.project_root}/src:src',
            ])
        
        # ビルド実行
        try:
            subprocess.run(pyinstaller_args, check=True, cwd=self.project_root)
            print(f"✅ スタンドアロン実行ファイル作成完了")
        except subprocess.CalledProcessError as e:
            print(f"❌ ビルドエラー: {e}")
            raise
    
    def create_installer(self):
        """インストーラー作成"""
        print(f"📦 {self.system} 用インストーラーを作成中...")
        
        if self.system == 'Windows':
            self._create_windows_installer()
        elif self.system == 'Darwin':
            self._create_macos_installer()
        else:  # Linux
            self._create_linux_installer()
    
    def _create_windows_installer(self):
        """Windows NSIS インストーラー作成"""
        nsis_script = self._generate_nsis_script()
        nsis_file = self.project_root / "installer.nsi"
        
        with open(nsis_file, 'w', encoding='utf-8') as f:
            f.write(nsis_script)
        
        try:
            subprocess.run(['makensis', str(nsis_file)], check=True)
            print("✅ Windows インストーラー作成完了")
        except FileNotFoundError:
            print("⚠️  NSIS が見つかりません。手動でインストーラーを作成してください。")
        except subprocess.CalledProcessError as e:
            print(f"❌ インストーラー作成エラー: {e}")
    
    def _create_macos_installer(self):
        """macOS DMG インストーラー作成"""
        app_path = self.dist_dir / self.build_config['app_bundle']
        dmg_path = self.dist_dir / self.build_config['dmg_name']
        
        if not app_path.exists():
            print("❌ .app バンドルが見つかりません")
            return
        
        try:
            # DMG作成
            subprocess.run([
                'hdiutil', 'create',
                '-volname', self.build_config['app_name'],
                '-srcfolder', str(app_path),
                '-ov', '-format', 'UDZO',
                str(dmg_path)
            ], check=True)
            print("✅ macOS DMG インストーラー作成完了")
        except subprocess.CalledProcessError as e:
            print(f"❌ DMG作成エラー: {e}")
    
    def _create_linux_installer(self):
        """Linux AppImage インストーラー作成"""
        print("ℹ️  Linux 用 AppImage 作成は手動で行ってください")
        print("参考: https://appimage.org/")
        
        # .desktop ファイル作成
        desktop_content = f"""[Desktop Entry]
Name={self.build_config['app_name']}
Exec={self.build_config['executable_name']}
Icon={self.build_config['app_name']}
Type=Application
Categories=Graphics;Photography;
Comment={self.build_config['description']}
"""
        
        desktop_file = self.dist_dir / f"{self.build_config['package_name']}.desktop"
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        print(f"✅ .desktop ファイル作成: {desktop_file}")
    
    def _generate_nsis_script(self) -> str:
        """NSIS スクリプト生成"""
        return f'''
!define APP_NAME "{self.build_config['app_name']}"
!define APP_VERSION "{self.build_config['version']}"
!define APP_PUBLISHER "{self.build_config['author']}"
!define APP_EXE "{self.build_config['executable_name']}"

Name "${{APP_NAME}}"
OutFile "{self.build_config['installer_name']}"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"

Page directory
Page instfiles

Section "Main"
    SetOutPath "$INSTDIR"
    File /r "dist\\*"
    
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    RMDir /r "$INSTDIR"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
'''
    
    def create_portable_version(self):
        """ポータブル版作成"""
        print("💼 ポータブル版を作成中...")
        
        portable_dir = self.dist_dir / f"{self.build_config['app_name']}_Portable"
        portable_dir.mkdir(exist_ok=True)
        
        # 実行ファイルコピー
        if self.system == 'Windows':
            exe_file = self.dist_dir / self.build_config['executable_name']
            if exe_file.exists():
                shutil.copy2(exe_file, portable_dir)
        
        # 設定ファイル・ドキュメントコピー
        files_to_copy = [
            'README.md',
            'LICENSE',
        ]
        
        for file_name in files_to_copy:
            src_file = self.project_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, portable_dir)
        
        # ポータブル起動スクリプト作成
        if self.system == 'Windows':
            batch_content = f'''@echo off
cd /d "%~dp0"
{self.build_config['executable_name']}
'''
            with open(portable_dir / "start.bat", 'w') as f:
                f.write(batch_content)
        else:
            shell_content = f'''#!/bin/bash
cd "$(dirname "$0")"
./{self.build_config.get('executable_name', 'advanced-image-editor')}
'''
            start_script = portable_dir / "start.sh"
            with open(start_script, 'w') as f:
                f.write(shell_content)
            start_script.chmod(0o755)
        
        print(f"✅ ポータブル版作成完了: {portable_dir}")
    
    def create_all_distributions(self):
        """全配布形式を作成"""
        print("🚀 すべての配布形式を作成中...")
        
        # ディレクトリ準備
        self.dist_dir.mkdir(exist_ok=True)
        
        try:
            # 1. スタンドアロン実行ファイル
            self.build_standalone_executable()
            
            # 2. インストーラー
            self.create_installer()
            
            # 3. ポータブル版
            self.create_portable_version()
            
            print("\n🎉 すべての配布形式の作成が完了しました！")
            print(f"📁 配布ファイル: {self.dist_dir}")
            
        except Exception as e:
            print(f"❌ 配布作成エラー: {e}")
            raise

def main():
    """メイン関数"""
    try:
        builder = DistributionBuilder()
        
        # 引数に応じて実行
        if len(sys.argv) > 1:
            command = sys.argv[1]
            if command == "executable":
                builder.build_standalone_executable()
            elif command == "installer":
                builder.create_installer()
            elif command == "portable":
                builder.create_portable_version()
            else:
                print("使用方法: python build_distribution.py [executable|installer|portable]")
        else:
            builder.create_all_distributions()
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()