"""
GUI Framework - Cross-Platform Compatible Version
Advanced Image Editor用のクロスプラットフォーム対応GUIフレームワーク
"""

__version__ = "1.0.0"
__author__ = "TITManagement"

from .core import FontManager, StyleManager, ImageUtils
from .widgets import ScalableLabel, StyledButton
from .layouts import TabLayout

__all__ = [
    'FontManager', 'StyleManager', 'ImageUtils',
    'ScalableLabel', 'StyledButton', 'TabLayout'
]