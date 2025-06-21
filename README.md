# AI File Analyzer

特定フォルダの最新ファイルを分析し、AIを使って更新点をまとめるツールです。

## 対応AI モデル

- **Azure OpenAI Service** (推奨・エンタープライズ向け)
- **OpenAI API** (標準版)
- **Ollama** (ローカル実行版)

## 機能

- 指定フォルダから最新N日間に更新されたファイルを自動検索
- AI エージェントによる高度なファイル内容分析
- OpenAI Agents SDK を使用したインテリジェントな分析
- 変更点や傾向を日本語でまとめ
- 分析結果をコンソール表示またはJSON形式で保存
- Obsidianノートの構造分析
- セキュリティとガバナンス提案

## 前提条件

- Python 3.8以上
- [uv](https://docs.astral.sh/uv/) パッケージマネージャー
- 以下のいずれか:
  - Azure OpenAI Service のアクセス権
  - OpenAI API キー
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

### Azure OpenAI Service版 (推奨)

#### 1. セットアップ
```bash
# セットアップ手順を表示
python azure_agents_main.py --setup

# 環境設定ファイルを作成
cp .env.template .env
# .envファイルを編集してAzure設定を入力
```

#### 2. 接続テスト
```bash
python azure_agents_main.py --test-connection
```

#### 3. 基本的な使用方法
```bash
python azure_agents_main.py /path/to/target/folder
```

#### 4. オプション付きの使用例
```bash
# 7日間のファイルを分析
python azure_agents_main.py /path/to/folder --days 7

# 結果をJSONファイルに保存
python azure_agents_main.py /path/to/folder --output report.json

# 非同期実行
python azure_agents_main.py /path/to/folder --async
```

### OpenAI API版

#### 1. セットアップ
```bash
# セットアップ手順を表示
python agents_main.py --setup

# 環境変数またはファイルでAPIキーを設定
export OPENAI_API_KEY="your-api-key"
# または .envファイルに OPENAI_API_KEY=your-api-key
```

#### 2. 接続テスト
```bash
python agents_main.py --test-connection
```

#### 3. 基本的な使用方法
```bash
python agents_main.py /path/to/target/folder
```

#### 4. オプション付きの使用例
```bash
# 7日間のファイルを分析
python agents_main.py /path/to/folder --days 7

# 結果をJSONファイルに保存
python agents_main.py /path/to/folder --output report.json

# 非同期実行
python agents_main.py /path/to/folder --async
```

### Ollama版 (ローカル実行)

```bash
# Ollamaが起動していることを確認
ollama list

# 実行
python main.py /path/to/target/folder --model llama3.2
```

## コマンドラインオプション

### 共通オプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `folder` | 分析対象のフォルダパス（必須） | - |
| `--days` | 分析期間（日数） | 30 |
| `--output` | 結果を保存するJSONファイルパス | なし（コンソール出力のみ） |

### Azure OpenAI Service版 専用オプション

| オプション | 説明 |
|-----------|------|
| `--setup` | セットアップ手順を表示 |
| `--test-connection` | Azure OpenAI Serviceへの接続テスト |
| `--async` | 非同期実行モード |
| `--sync` | 同期実行モード |

### OpenAI API版 専用オプション

| オプション | 説明 |
|-----------|------|
| `--setup` | セットアップ手順を表示 |
| `--test-connection` | OpenAI APIへの接続テスト |
| `--async` | 非同期実行モード |

### Ollama版 専用オプション

| オプション | 説明 | デフォルト値 |
|-----------|------|-------------|
| `--model` | 使用するOllamaモデル | llama3.2 |

## 出力例

### Azure OpenAI Service版
```
フォルダ「/home/user/project」の最新30日間のファイルをAzure OpenAI Serviceで分析中...
🔄 Azure OpenAI Service + OpenAI Agents SDKを使用しています...

==================================================
🤖 Azure AIエージェント分析結果
==================================================

## ファイル分析レポート

### 1. 更新されたファイルの概要
- 対象期間: 30日間
- 更新ファイル数: 15個
- 主要ファイルタイプ: Python (.py), Markdown (.md), JSON (.json)

### 2. 開発アクティビティの分析
このプロジェクトでは以下の特徴が見られます：
- AI エージェント機能の実装が活発
- Azure OpenAI Service統合の追加
- ドキュメントの充実化

### 3. 技術的特徴
- OpenAI Agents SDK の採用
- マルチプラットフォーム対応
- エンタープライズセキュリティの考慮

### 4. 改善提案
- CI/CD パイプラインの強化を推奨
- テストカバレッジの向上
- セキュリティ監査の実施

📄 詳細レポートは report.json に保存されました。
```

## 設定

### Azure OpenAI Service の設定

#### 環境変数
`.env`ファイルに以下の設定を記載：

```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

#### Azure設定値の取得方法
1. **Azure ポータル**にログイン
2. **Azure OpenAI Service リソース**を選択
3. **キーとエンドポイント**で API キーとエンドポイントを取得
4. **モデル デプロイ**でデプロイメント名を確認

### OpenAI API の設定

#### 環境変数
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

または `.env`ファイルに記載：
```env
OPENAI_API_KEY=your-openai-api-key
```

#### OpenAI APIキーの取得方法
1. **OpenAI Platform**にアクセス: https://platform.openai.com/api-keys
2. **Create new secret key**でAPIキーを作成
3. 作成されたAPIキーをコピーして環境変数に設定

### Ollama の設定
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

### Azure OpenAI Service関連

#### 接続エラーの場合
```bash
# 接続テストを実行
python azure_agents_main.py --test-connection

# 設定の確認
python azure_agents_main.py --setup
```

#### よくある問題と解決策
1. **環境変数が設定されていない**
   - `.env`ファイルが存在するか確認
   - Azure設定値が正しく入力されているか確認

2. **デプロイメントが見つからない**
   - Azure ポータルでデプロイメント名を確認
   - デプロイメントの状態が「成功」になっているか確認

3. **API バージョンエラー**
   - `2024-08-01-preview`を使用することを推奨

### OpenAI API関連

#### 接続エラーの場合
```bash
# 接続テストを実行
python agents_main.py --test-connection

# 設定の確認
python agents_main.py --setup
```

#### よくある問題と解決策
1. **環境変数が設定されていない**
   - APIキーが正しく設定されているか確認
   - `.env`ファイルが存在する場合は内容を確認

2. **APIの利用制限**
   - OpenAI Platformで使用量と制限を確認
   - 課金設定を確認

3. **APIキーの権限不足**
   - APIキーが有効か確認
   - 必要な権限が付与されているか確認

```bash
# API キーの確認
echo $OPENAI_API_KEY
```

### Ollama関連

```bash
# Ollamaが起動しているか確認
ollama list

# モデルが利用可能か確認
ollama run llama3.2
```

### 文字化けする場合
ファイルのエンコーディングを確認し、必要に応じて各分析クラスの `read_file_content` メソッドを調整してください。

## ファイル構成

```
ollama_folderAnalyzer/
├── README.md                     # このファイル
├── pyproject.toml               # プロジェクト設定
├── .env.template                # 環境変数テンプレート
├── file_analyzer.py             # Ollama版 (オリジナル)
├── main.py                      # Ollama版 メイン
├── agents_file_analyzer.py      # OpenAI API版
├── agents_main.py               # OpenAI API版 メイン
├── azure_agents_file_analyzer.py # Azure OpenAI版
└── azure_agents_main.py         # Azure OpenAI版 メイン
```

## ライセンス

MIT License