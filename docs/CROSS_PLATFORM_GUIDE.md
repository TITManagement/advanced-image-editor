# 🌍 **クロスプラットフォーム対応ガイド**

## Advanced Image Editor - Windows, macOS, Linux 完全対応

### 📋 **対応プラットフォーム**

| OS | バージョン | アーキテクチャ | 状態 |
|---|---|---|---|
| **Windows** | 10/11 | x64, ARM64 | ✅ 完全対応 |
| **macOS** | 10.15+ | Intel, Apple Silicon | ✅ 完全対応 |
| **Linux** | Ubuntu 20.04+ | x64, ARM64 | ✅ 完全対応 |

### 🚀 **インストール方法**

#### **Option 1: 自動環境構築（推奨）**
```bash
# リポジトリをクローン
git clone https://github.com/TITManagement/advanced-image-editor.git
cd advanced-image-editor

# クロスプラットフォーム対応セットアップ実行
python scripts/setup_dev_environment.py
```

#### **Option 2: 手動インストール**

**Windows:**
```cmd
# 仮想環境作成
python -m venv .venv
.venv\\Scripts\\activate

# 依存関係インストール
pip install -e .[windows]
```

**macOS:**
```bash
# 仮想環境作成
python3 -m venv .venv
source .venv/bin/activate

# 依存関係インストール  
pip install -e .[macos]
```

**Linux:**
```bash
# 必要なシステムパッケージ（Ubuntu/Debian）
sudo apt update
sudo apt install python3-tk python3-dev

# 仮想環境作成
python3 -m venv .venv
source .venv/bin/activate

# 依存関係インストール
pip install -e .[linux]
```

### 💻 **起動方法**

#### **コマンドラインから**
```bash
# エントリーポイント（推奨）
advanced-image-editor

# エイリアス
aie

# 直接実行
python src/main_plugin.py
```

#### **デスクトップから**
- **Windows**: スタートメニューから「Advanced Image Editor」
- **macOS**: Applications フォルダから「AdvancedImageEditor.app」
- **Linux**: アプリケーションメニューから「Advanced Image Editor」

### 🔧 **システム要件**

| 項目 | 最小要件 | 推奨 |
|---|---|---|
| **Python** | 3.8+ | 3.11+ |
| **メモリ** | 2GB | 8GB+ |
| **ストレージ** | 500MB | 2GB+ |
| **ディスプレイ** | 1024x768 | 1920x1080+ |

### 🏗️ **配布パッケージ作成**

#### **スタンドアロン実行ファイル**
```bash
# 現在のOSで実行ファイル作成
python scripts/build_distribution.py executable
```

#### **インストーラー作成**
```bash
# OS別インストーラー作成
python scripts/build_distribution.py installer
```

#### **ポータブル版作成**
```bash
# ポータブル版（USBメモリ等で持ち運び可能）
python scripts/build_distribution.py portable
```

### 📂 **OS固有の特徴**

#### **Windows 固有機能**
- ✅ Windows Defender 除外設定サポート
- ✅ レジストリー統合
- ✅ タスクバーピン留め対応
- ✅ ファイル関連付け自動設定

#### **macOS 固有機能**
- ✅ Retina ディスプレイ最適化
- ✅ Touch Bar サポート（対応機種）
- ✅ macOS ダークモード連携
- ✅ Finder 統合

#### **Linux 固有機能**
- ✅ 主要デスクトップ環境対応（GNOME, KDE, XFCE）
- ✅ X11/Wayland 両対応
- ✅ パッケージマネージャー自動検出
- ✅ XDG Base Directory 準拠

### 🎨 **カーブエディタ機能**

#### **2D ガンマ補正カーブ**
- **横軸**: 入力濃度（0-255）
- **縦軸**: 出力濃度（0-255）
- **操作**: マウスクリック・ドラッグで直感的な調整
- **リアルタイムプレビュー**: デバウンス最適化で快適な操作感

#### **マウス操作**
- **左クリック**: 制御点追加・選択・移動
- **右クリック**: 制御点削除
- **Ctrl+R**: カーブリセット（線形に戻す）

### 🔄 **プラグインシステム**

#### **4つの主要プラグイン**
1. **基本調整プラグイン**: 明度・コントラスト・彩度
2. **濃度調整プラグイン**: ガンマ・ヒストグラム・カーブ
3. **フィルタープラグイン**: ブラー・エッジ・ノイズ除去
4. **高度処理プラグイン**: シャープ・色空間変換

#### **プラグイン開発**
```python
from src.core.plugin_base import ImageProcessorPlugin

class MyPlugin(ImageProcessorPlugin):
    def get_plugin_name(self) -> str:
        return "My Custom Plugin"
    
    def process_image(self, image, **params):
        # 画像処理ロジック
        return processed_image
```

### 🛠️ **トラブルシューティング**

#### **共通問題**

**Q: アプリケーションが起動しない**
```bash
# 環境診断実行
python scripts/setup_dev_environment.py

# 依存関係確認
pip list | grep -E "(customtkinter|opencv|pillow)"
```

**Q: 画像処理が遅い**
- パフォーマンスパッケージインストール: `pip install -e .[performance]`
- メモリ使用量確認: アプリ内メニュー > ヘルプ > システム情報

#### **Windows 固有問題**

**Q: "DLL load failed" エラー**
```cmd
# Visual C++ Redistributable インストール
# https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
```

**Q: 管理者権限が必要と表示される**
```cmd
# 管理者として PowerShell 実行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **macOS 固有問題**

**Q: "開発元が未確認" エラー**
```bash
# Gatekeeper 一時解除
sudo spctl --master-disable
# アプリ起動後、再度有効化
sudo spctl --master-enable
```

**Q: Xcode Command Line Tools エラー**
```bash
xcode-select --install
```

#### **Linux 固有問題**

**Q: tkinter インポートエラー**
```bash
# Ubuntu/Debian
sudo apt install python3-tk python3-dev

# CentOS/RHEL
sudo yum install tkinter python3-devel

# Arch Linux
sudo pacman -S tk python-dev
```

### 📞 **サポート**

- **Issues**: [GitHub Issues](https://github.com/TITManagement/advanced-image-editor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/TITManagement/advanced-image-editor/discussions)
- **Email**: contact@titmanagement.com

### 📄 **ライセンス**

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

---

**🎉 Advanced Image Editor で、どのプラットフォームでも快適な画像編集を！**