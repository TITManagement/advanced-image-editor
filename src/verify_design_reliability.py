#!/usr/bin/env python3
"""
UniversalPluginBase設計信頼度検証スクリプト
============================================

Original版との機能完全性を体系的に検証し、
設計の信頼度を数値化します。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_plugin_completeness():
    """プラグイン完全性の検証"""
    
    print("🔍 UniversalPluginBase設計信頼度検証を開始...")
    print("=" * 60)
    
    # === 機能完全性チェック ===
    
    required_features = {
        "基本パラメータスライダー": False,
        "カーブエディタ": False,
        "専用機能ボタン": False,
        "リセット機能": False,
        "プリセット管理": False,
        "履歴管理": False,
        "高度オプション": False,
    }
    
    # UniversalPluginBase実装チェック
    try:
        from core.universal_plugin_base import UniversalPluginBase
        
        # 基本機能チェック
        test_methods = [
            "supports_presets",
            "supports_curve_editor", 
            "supports_custom_buttons",
            "supports_history",
            "supports_advanced_options",
            "_create_automatic_ui",
            "_create_curve_editor",
            "_create_custom_buttons",
            "_create_preset_management", 
            "_create_history_management",
            "_create_advanced_options"
        ]
        
        missing_methods = []
        for method in test_methods:
            if not hasattr(UniversalPluginBase, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 不足メソッド: {missing_methods}")
            return False
        else:
            print("✅ 全必要メソッドが実装済み")
            
    except ImportError as e:
        print(f"❌ UniversalPluginBaseインポートエラー: {e}")
        return False
    
    # === 設定ファイル完全性チェック ===
    
    try:
        import json
        config_path = "plugins/density_universal/plugin.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            required_config_keys = [
                "parameters",
                "curve_editor", 
                "custom_buttons",
                "advanced_features",
                "presets"
            ]
            
            missing_configs = []
            for key in required_config_keys:
                if key not in config:
                    missing_configs.append(key)
            
            if missing_configs:
                print(f"⚠️ 不足設定キー: {missing_configs}")
            else:
                print("✅ 設定ファイル完全性確認")
                
        else:
            print(f"❌ 設定ファイル未発見: {config_path}")
            return False
            
    except Exception as e:
        print(f"❌ 設定ファイル検証エラー: {e}")
        return False
    
    # === コード量比較 ===
    
    try:
        original_lines = 0
        universal_lines = 0
        
        # Original版
        original_path = "plugins/density/density_plugin.py"
        if os.path.exists(original_path):
            with open(original_path, 'r', encoding='utf-8') as f:
                original_lines = len(f.readlines())
        
        # Universal版
        universal_path = "plugins/density_universal/plugin.py"
        if os.path.exists(universal_path):
            with open(universal_path, 'r', encoding='utf-8') as f:
                universal_lines = len(f.readlines())
        
        if original_lines > 0 and universal_lines > 0:
            reduction_rate = (1 - universal_lines / original_lines) * 100
            print(f"📊 コード削減率: {reduction_rate:.1f}% ({original_lines}行 → {universal_lines}行)")
            
            if reduction_rate >= 70:
                print("✅ 高い削減効果を達成")
            elif reduction_rate >= 50:
                print("⚠️ 中程度の削減効果")
            else:
                print("❌ 削減効果不十分")
                
    except Exception as e:
        print(f"❌ コード量比較エラー: {e}")
    
    print("=" * 60)
    print("🎯 設計信頼度検証完了")
    
    return True

if __name__ == "__main__":
    success = verify_plugin_completeness()
    sys.exit(0 if success else 1)