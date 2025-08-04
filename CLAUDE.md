# CLAUDE.md

日本語で対応

## 概要

PAGENERATOR は Markdown ファイルから Web ページを生成するシンプルなツールです。単一ファイル変換と再帰的ディレクトリ変換をサポートし、ブレッドクラム機能も提供します。

## 主要コマンド

### ビルドとリント

```bash
# 全体的なタスク（フォーマット → リント → テスト）
task

# フォーマット
task format
# または
ruff format --respect-gitignore
ruff check --fix
pnpm format

# リント
task lint
# または
ruff check --respect-gitignore
ruff format --check
pnpm lint
yamllint *.yml *.yaml

# テスト（現在は no-op）
pnpm test
```

### 依存関係管理

```bash
# Python 依存関係（uv 使用）
uv add <package>
uv sync

# Node.js 依存関係（pnpm 使用、npm 禁止）
pnpm install
pnpm add <package>
```

### アプリケーション実行

```bash
# 基本的な変換
pagenerator -i source.md -t template.html -o output.html

# 再帰的変換
pagenerator -i ./source_dir -o ./out_dir -t ./template.html -R

# ブレッドクラム付き再帰変換
pagenerator -i ./source_dir -o ./out_dir -t ./template.html -R --breads sub/

# 強制生成
pagenerator -i source.md -t template.html -o output.html -f
```

## アーキテクチャ

### 言語とツール

- **Python**: メインアプリケーション（Python 3.13+）
- **Node.js**: 開発ツール（pnpm 必須、npm 禁止）
- **Task**: ビルドタスクランナー（Taskfile.yml）

### コア構造

- `pagenerator/cli.py`: メインエントリポイントとコマンドライン処理
- `pagenerator/__init__.py`: パッケージ初期化（現在は空）

### 主要機能

1. **Markdown → HTML 変換**: `markdown` ライブラリを使用、コードブロック・表・脚注をサポート
2. **テンプレートシステム**: Python の `string.Template` を使用した変数置換
3. **ブレッドクラム生成**: 指定されたディレクトリパスに対する階層ナビゲーション
4. **スマート更新**: ファイルの更新時刻を比較して不要な再生成を回避

### 重要な設計パターン

- `index.md` ファイルが最初に処理され、ディレクトリのタイトルとして使用される
- ブレッドクラムは Schema.org の構造化データ形式で生成
- テンプレート変数: `$content`（HTML）、`$title`（ページタイトル）、`$bread`（ブレッドクラム）

### 開発環境設定

- **Python**: pyproject.toml で管理、uv をパッケージマネージャーとして使用
- **JavaScript/CSS**: package.json で開発ツールを管理
- **型チェック**: pyright 設定済み
- **コードフォーマット**: ruff（行長120文字）
- **リント**: markdownlint、yamllint、taplo（TOML）、ruff
