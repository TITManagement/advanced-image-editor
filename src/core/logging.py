#!/usr/bin/env python3
"""
Advanced Image Editor - Logging System Module
高度な画像編集アプリケーション用ログシステム

## 概要

アプリケーション全体で使用する統一されたログシステムを提供します。
5段階のログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）により、
開発・デバッグ・本番運用での適切な情報出力を実現します。

## 使用方法

```python
from core.logging import LogLevel, set_log_level, debug_print, info_print, warning_print, error_print, critical_print

# ログレベルの設定
set_log_level(LogLevel.DEBUG)

# 各レベルでの出力
debug_print("デバッグ情報")
info_print("一般情報")
warning_print("警告メッセージ")
error_print("エラーメッセージ")
critical_print("致命的エラー")
```

【作成者】GitHub Copilot
【バージョン】1.0.0
【最終更新】2025年9月15日
"""

from enum import IntEnum
from typing import Any, Optional

class LogLevel(IntEnum):
    """ログレベル定義
    
    数値が大きいほど重要度が高い。
    現在のログレベル以上のメッセージのみが出力される。
    """
    DEBUG = 10      # デバッグ情報（開発時のみ）
    INFO = 20       # 一般情報（通常の動作状況）
    WARNING = 30    # 警告（問題の可能性があるが継続可能）
    ERROR = 40      # エラー（機能の一部が失敗）
    CRITICAL = 50   # 致命的エラー（アプリケーションの継続困難）

# 現在のログレベル（デフォルトはINFO）
_current_log_level: LogLevel = LogLevel.INFO

def set_log_level(level: LogLevel) -> None:
    """グローバルログレベルを設定
    
    Args:
        level: 設定するログレベル
    """
    global _current_log_level
    _current_log_level = level

def get_log_level() -> LogLevel:
    """現在のログレベルを取得
    
    Returns:
        現在のログレベル
    """
    return _current_log_level

def log_print(level: LogLevel, *args: Any, **kwargs: Any) -> None:
    """ログレベルに基づいて出力する関数
    
    現在のログレベル以上の重要度を持つメッセージのみが出力される。
    各ログレベルには視覚的に分かりやすいプレフィックスが付与される。
    
    Args:
        level: メッセージのログレベル
        *args: print関数に渡される引数
        **kwargs: print関数に渡されるキーワード引数
    """
    if level >= _current_log_level:
        # ログレベルに応じたプレフィックスを追加
        level_prefixes = {
            LogLevel.DEBUG: "🔍 [DEBUG]",
            LogLevel.INFO: "ℹ️ [INFO]",
            LogLevel.WARNING: "⚠️ [WARNING]",
            LogLevel.ERROR: "❌ [ERROR]",
            LogLevel.CRITICAL: "🚨 [CRITICAL]"
        }
        prefix = level_prefixes.get(level, "")
        if prefix and args:
            print(f"{prefix} {args[0]}", *args[1:], **kwargs)
        else:
            print(*args, **kwargs)

def debug_print(*args: Any, **kwargs: Any) -> None:
    """デバッグレベルメッセージを出力
    
    開発時のデバッグ情報や詳細な動作状況の出力に使用。
    本番環境では通常非表示。
    
    Args:
        *args: print関数に渡される引数
        **kwargs: print関数に渡されるキーワード引数
    """
    log_print(LogLevel.DEBUG, *args, **kwargs)

def info_print(*args: Any, **kwargs: Any) -> None:
    """情報レベルメッセージを出力
    
    一般的な動作状況や重要でない情報の出力に使用。
    通常の操作では表示される。
    
    Args:
        *args: print関数に渡される引数
        **kwargs: print関数に渡されるキーワード引数
    """
    log_print(LogLevel.INFO, *args, **kwargs)

def warning_print(*args: Any, **kwargs: Any) -> None:
    """警告レベルメッセージを出力
    
    問題の可能性があるが処理を継続できる状況の出力に使用。
    ユーザーの注意を喚起する。
    
    Args:
        *args: print関数に渡される引数
        **kwargs: print関数に渡されるキーワード引数
    """
    log_print(LogLevel.WARNING, *args, **kwargs)

def error_print(*args: Any, **kwargs: Any) -> None:
    """エラーレベルメッセージを出力
    
    機能の一部が失敗したが、アプリケーション全体は継続可能な
    エラー状況の出力に使用。
    
    Args:
        *args: print関数に渡される引数
        **kwargs: print関数に渡されるキーワード引数
    """
    log_print(LogLevel.ERROR, *args, **kwargs)

def critical_print(*args: Any, **kwargs: Any) -> None:
    """致命的エラーレベルメッセージを出力
    
    アプリケーションの継続が困難な重大なエラー状況の出力に使用。
    通常、このレベルのエラー後はアプリケーションが終了する。
    
    Args:
        *args: print関数に渡される引数
        **kwargs: print関数に渡されるキーワード引数
    """
    log_print(LogLevel.CRITICAL, *args, **kwargs)

# 後方互換性のためのエイリアス
DEBUG_MODE = False  # 旧式のデバッグフラグ（非推奨）

def set_debug_mode(enabled: bool) -> None:
    """旧式のデバッグモード設定（後方互換性のため）
    
    非推奨: set_log_level(LogLevel.DEBUG)の使用を推奨
    
    Args:
        enabled: デバッグモードを有効にするかどうか
    """
    global DEBUG_MODE
    DEBUG_MODE = enabled
    if enabled:
        set_log_level(LogLevel.DEBUG)
    else:
        set_log_level(LogLevel.INFO)

# モジュール初期化時の情報出力
if __name__ == "__main__":
    # テスト用のコード
    print("=== Logging System Test ===")
    
    # 全レベルでのテスト出力
    set_log_level(LogLevel.DEBUG)
    debug_print("This is a debug message")
    info_print("This is an info message")
    warning_print("This is a warning message")
    error_print("This is an error message")
    critical_print("This is a critical message")
    
    print("\n--- Setting log level to WARNING ---")
    set_log_level(LogLevel.WARNING)
    debug_print("This debug message should not appear")
    info_print("This info message should not appear")
    warning_print("This warning message should appear")
    error_print("This error message should appear")
    critical_print("This critical message should appear")