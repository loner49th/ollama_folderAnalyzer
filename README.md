# Ollama File Analyzer

特定フォルダの最新ファイルを分析し、Ollamaを使って更新点をまとめるツールです。

## 機能

- 指定フォルダから最新N日間に更新されたファイルを自動検索
- ファイル内容をOllamaで分析し、変更点や傾向を日本語でまとめ
- 分析結果をコンソール表示またはJSON形式で保存

## 前提条件

- Python 3.8以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- [Ollama](https://ollama.ai/) がローカルで実行されていること

## インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd ollama_agent
```

2. 依存関係をインストール
```bash
uv sync
```

## 使用方法

### 基本的な使用方法
```bash
uv run python main.py /path/to/target/folder
```

### オプション付きの使用例
```bash
# 7日間のファイルを分析
uv run python main.py /path/to/folder --days 7

# 特定のモデルを使用
uv run python main.py /path/to/folder --model llama3.1

# 結果をJSONファイルに保存
uv run python main.py /path/to/folder --output report.json

# 全オプション指定
uv run python main.py /path/to/folder --days 14 --model llama3.2 --output analysis_report.json
```

## コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `folder` | 分析対象のフォルダパス（必須） | - |
| `--days` | 分析期間（日数） | 30 |
| `--model` | 使用するOllamaモデル | llama3.2 |
| `--output` | 結果を保存するJSONファイルパス | なし（コンソール出力のみ） |

## 出力例

```
フォルダ「/home/user/project」の最新30日間のファイルを分析中...

=== 分析結果 ===
対象フォルダ: /home/user/project
分析期間: 30日間
更新されたファイル数: 15個

=== 更新ファイル一覧 ===
- /home/user/project/src/main.py (2024-01-15T10:30:00)
- /home/user/project/README.md (2024-01-14T16:45:00)
- /home/user/project/config.json (2024-01-13T09:20:00)
... 他12個のファイル

=== AI分析結果 ===
このプロジェクトでは主にPythonファイルとドキュメントファイルが更新されています。
最近の変更点として、メイン機能の改善とREADMEの更新が行われており、
アクティブな開発が継続されていることが確認できます...
```

## 設定

### Ollamaの設定
デフォルトでは `http://localhost:11434` でOllamaに接続します。
異なるホストやポートを使用する場合は、`file_analyzer.py` の `OllamaClient` クラスを編集してください。

### 対応ファイル形式
- UTF-8エンコーディングのテキストファイル
- Obsidianで生成されたMarkdownファイル（.md）
  - 内部リンク記法 `[[リンク名]]`
  - タグ記法 `#タグ名`
  - ブロック参照 `^ブロックID`
- その他のテキストファイル（.txt, .json, .csv, .html, .xml, .js, .ts, .py, .css, .yaml, .yml）
- UTF-8以外のエンコーディング（Shift_JIS、CP932等）も自動判定して読み込み

## トラブルシューティング

### Ollamaに接続できない場合
```bash
# Ollamaが起動しているか確認
ollama list

# モデルが利用可能か確認
ollama run llama3.2
```

### 文字化けする場合
ファイルのエンコーディングを確認し、必要に応じて `file_analyzer.py` の `read_file_content` メソッドを調整してください。

## ライセンス

MIT License