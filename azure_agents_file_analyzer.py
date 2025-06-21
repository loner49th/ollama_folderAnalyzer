import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, function_tool, Runner, set_tracing_disabled
from pydantic import BaseModel


# 環境変数を読み込み
load_dotenv()

# Azure OpenAI Service設定
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# トレーシングを無効化（Azure OpenAI Service使用時は必須）
set_tracing_disabled(disabled=True)


class AzureConfig(BaseModel):
    """Azure OpenAI Service設定クラス"""
    api_key: str
    api_version: str
    endpoint: str
    deployment: str
    
    @classmethod
    def from_env(cls) -> "AzureConfig":
        """環境変数から設定を読み込み"""
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        
        if not all([api_key, endpoint, deployment]):
            missing = []
            if not api_key:
                missing.append("AZURE_OPENAI_API_KEY")
            if not endpoint:
                missing.append("AZURE_OPENAI_ENDPOINT")
            if not deployment:
                missing.append("AZURE_OPENAI_DEPLOYMENT")
            
            raise ValueError(f"以下の環境変数が設定されていません: {', '.join(missing)}")
        
        return cls(
            api_key=api_key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            endpoint=endpoint,
            deployment=deployment
        )


@function_tool
def find_recent_files(folder_path: str, days: int = 30) -> str:
    """
    指定フォルダから最新N日以内のファイルを取得
    
    Args:
        folder_path: 分析対象のフォルダパス
        days: 分析期間（日数）
    
    Returns:
        最新ファイルのリスト
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise ValueError(f"フォルダが存在しません: {folder_path}")
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_files = []
    
    for file_path in folder.rglob("*"):
        if file_path.is_file():
            try:
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if modified_time > cutoff_date:
                    recent_files.append({
                        "path": str(file_path),
                        "modified": modified_time.isoformat(),
                        "size": file_path.stat().st_size
                    })
            except Exception:
                continue
    
    # 更新日時でソート
    recent_files.sort(key=lambda x: x["modified"], reverse=True)
    
    import json
    return json.dumps(recent_files, ensure_ascii=False, indent=2)


@function_tool
def read_file_content(file_path: str, max_chars: int = 2000) -> str:
    """
    ファイル内容を読み込み（Obsidian対応）
    
    Args:
        file_path: ファイルパス
        max_chars: 読み込む最大文字数
    
    Returns:
        ファイル内容
    """
    import re
    
    # Obsidianでサポートされるファイル拡張子
    obsidian_extensions = {'.md', '.txt', '.json', '.csv', '.html', '.xml', '.js', '.ts', '.py', '.css', '.yaml', '.yml'}
    
    file_ext = Path(file_path).suffix.lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 内容を制限
        if len(content) > max_chars:
            content = content[:max_chars] + "..."
            
        # Obsidianのマークダウンリンク記法を処理
        if file_ext == '.md':
            # Obsidianの内部リンク [[リンク名]] を処理
            content = re.sub(r'\[\[([^\]]+)\]\]', r'[[\1]]（Obsidianリンク）', content)
            
            # Obsidianのタグ #タグ名 を処理
            content = re.sub(r'#([a-zA-Z0-9_\-/]+)', r'#\1（Obsidianタグ）', content)
            
            # Obsidianのブロック参照 ^ブロックID を処理
            content = re.sub(r'\^([a-zA-Z0-9\-]+)', r'^\\1（ブロック参照）', content)
            
        return content
    except UnicodeDecodeError:
        # UTF-8で読めない場合、他のエンコーディングを試行
        encodings = ['shift_jis', 'cp932', 'latin1', 'utf-16']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                if len(content) > max_chars:
                    content = content[:max_chars] + "..."
                return f"[{encoding}エンコーディング] {content}"
            except Exception:
                continue
        return f"[読み込み不可能なエンコーディング: {file_path}]"
    except Exception as e:
        return f"[読み込みエラー: {str(e)}]"


@function_tool
def analyze_file_types(files_json: str) -> str:
    """
    ファイルタイプを分析
    
    Args:
        files_json: ファイル情報のリスト（JSON文字列）
    
    Returns:
        ファイルタイプの統計情報（JSON文字列）
    """
    import json
    
    try:
        files = json.loads(files_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON format"}, ensure_ascii=False)
    
    type_stats = {}
    total_size = 0
    
    for file_info in files:
        file_path = Path(file_info["path"])
        ext = file_path.suffix.lower() or "拡張子なし"
        
        if ext not in type_stats:
            type_stats[ext] = {"count": 0, "total_size": 0}
        
        type_stats[ext]["count"] += 1
        type_stats[ext]["total_size"] += file_info["size"]
        total_size += file_info["size"]
    
    result = {
        "file_types": type_stats,
        "total_files": len(files),
        "total_size": total_size
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@function_tool
def save_report(report_data: str, output_path: str) -> str:
    """
    レポートをJSONファイルに保存
    
    Args:
        report_data: レポートデータ（JSON文字列）
        output_path: 保存先パス
    
    Returns:
        保存結果メッセージ
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_data)
        return f"レポートを {output_path} に保存しました。"
    except Exception as e:
        return f"保存エラー: {str(e)}"


class AzureFileAnalyzerAgent:
    """Azure OpenAI Service + OpenAI Agents SDKを使用したファイル分析エージェント"""
    
    def __init__(self, config: Optional[AzureConfig] = None):
        # 設定の初期化
        self.config = config or AzureConfig.from_env()
        
        # Azure OpenAI用のカスタムクライアントを作成
        self.custom_client = AsyncOpenAI(
            api_key=self.config.api_key,
            base_url=f"{self.config.endpoint}/openai/deployments/{self.config.deployment}",
            default_headers={"api-key": self.config.api_key},
            default_query={"api-version": self.config.api_version},
        )
        
        # ファイル分析エージェントの作成
        self.file_analyzer_agent = Agent(
            name="Azure ファイル分析エージェント",
            instructions="""
            あなたはAzure OpenAI Serviceを使用したファイル分析の専門家です。
            指定されたフォルダ内のファイルを分析し、以下の観点から詳細なレポートを作成してください：
            
            1. ファイルの種類と分布の分析
            2. 最近の更新傾向とパターン
            3. ファイル内容の特徴と構造
            4. 開発プロジェクトの進行状況の把握
            5. Obsidianノート（.mdファイル）の構造や内容の分析
            6. 注目すべき変更点や改善提案
            7. セキュリティ上の注意点（もしあれば）
            
            分析は日本語で行い、具体的で実用的な情報を提供してください。
            企業環境でのセキュリティとガバナンス要件を考慮した提案も含めてください。
            """,
            tools=[
                find_recent_files,
                read_file_content,
                analyze_file_types,
                save_report
            ]
        )
    
    async def analyze_folder(self, folder_path: str, days: int = 30, output_path: Optional[str] = None) -> str:
        """
        フォルダを分析してレポートを生成（非同期）
        
        Args:
            folder_path: 分析対象のフォルダパス
            days: 分析期間（日数）
            output_path: レポート保存先（オプション）
        
        Returns:
            分析結果
        """
        prompt = f"""
        フォルダ「{folder_path}」の最新{days}日間のファイルをAzure OpenAI Serviceで分析してください。
        
        以下の手順で詳細な分析を行ってください：
        1. find_recent_files関数を使って最新{days}日以内のファイルを取得（JSON文字列で返されます）
        2. analyze_file_types関数にファイルのJSON文字列を渡してファイルタイプの統計を取得
        3. 主要なファイル（最新10-15個程度）についてread_file_content関数で内容を確認
        4. 分析結果をまとめて詳細なレポートを作成
        {'5. save_report関数を使って結果を' + output_path + 'に保存' if output_path else ''}
        
        特に以下の点に注目して分析してください：
        - プロジェクトの開発状況と技術スタック
        - ファイルの更新パターンと開発アクティビティ
        - Obsidianノートの構造、内容、知識管理の状況
        - コードの品質と構造的な特徴
        - セキュリティ上の注意点や改善提案
        - 企業環境での利用を考慮したガバナンス提案
        
        Azure OpenAI Serviceの企業向け機能を活用した高度な分析を提供してください。
        """
        
        result = await Runner.run(
            self.file_analyzer_agent,
            prompt,
            client=self.custom_client
        )
        return result.final_output
    
    def analyze_folder_sync(self, folder_path: str, days: int = 30, output_path: Optional[str] = None) -> str:
        """
        フォルダを分析してレポートを生成（同期版）
        
        Args:
            folder_path: 分析対象のフォルダパス
            days: 分析期間（日数）
            output_path: レポート保存先（オプション）
        
        Returns:
            分析結果
        """
        return asyncio.run(self.analyze_folder(folder_path, days, output_path))
    
    def verify_connection(self) -> bool:
        """
        Azure OpenAI Serviceへの接続を確認
        
        Returns:
            接続可能かどうか
        """
        try:
            # 簡単なテスト用エージェント
            test_agent = Agent(
                name="接続テスト",
                instructions="「接続テスト成功」と短く回答してください。"
            )
            
            result = Runner.run_sync(
                test_agent,
                "接続テストを実行してください。",
                client=self.custom_client
            )
            
            return "接続テスト" in result.final_output
        except Exception as e:
            print(f"接続テストでエラーが発生: {str(e)}")
            return False