#!/usr/bin/env python3
"""
Core Package - コアパッケージ

プラグインシステムの中核機能を提供
"""

from .plugin_base import ImageProcessorPlugin, PluginManager, PluginUIHelper

__all__ = [
    'ImageProcessorPlugin',
    'PluginManager', 
    'PluginUIHelper'
]