import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, model: str, prompt: str) -> str:
        """Ollamaを使ってテキストを生成"""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"エラーが発生しました: {str(e)}"


class FileAnalyzer:
    def __init__(self, ollama_model: str = "llama3.2"):
        self.ollama = OllamaClient()
        self.model = ollama_model
    
    def find_recent_files(self, folder_path: str, days: int = 30) -> List[Dict[str, Any]]:
        """指定フォルダから最新N日以内のファイルを取得"""
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
        return recent_files
    
    def read_file_content(self, file_path: str) -> str:
        """ファイル内容を読み込み（Obsidian対応）"""
        # Obsidianでサポートされるファイル拡張子
        obsidian_extensions = {'.md', '.txt', '.json', '.csv', '.html', '.xml', '.js', '.ts', '.py', '.css', '.yaml', '.yml'}
        
        file_ext = Path(file_path).suffix.lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Obsidianのマークダウンリンク記法を処理
            if file_ext == '.md':
                content = self._process_obsidian_markdown(content)
                
            return content
        except UnicodeDecodeError:
            # UTF-8で読めない場合、他のエンコーディングを試行
            encodings = ['shift_jis', 'cp932', 'latin1', 'utf-16']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return f"[{encoding}エンコーディング] {content}"
                except Exception:
                    continue
            return f"[読み込み不可能なエンコーディング: {file_path}]"
        except Exception as e:
            return f"[読み込みエラー: {str(e)}]"
    
    def _process_obsidian_markdown(self, content: str) -> str:
        """Obsidianのマークダウン記法を処理"""
        import re
        
        # Obsidianの内部リンク [[リンク名]] を処理
        content = re.sub(r'\[\[([^\]]+)\]\]', r'[[\1]]（Obsidianリンク）', content)
        
        # Obsidianのタグ #タグ名 を処理
        content = re.sub(r'#([a-zA-Z0-9_\-/]+)', r'#\1（Obsidianタグ）', content)
        
        # Obsidianのブロック参照 ^ブロックID を処理
        content = re.sub(r'\^([a-zA-Z0-9\-]+)', r'^\\1（ブロック参照）', content)
        
        return content
    
    def analyze_file_changes(self, files: List[Dict[str, Any]]) -> str:
        """ファイルの変更点を分析してまとめる"""
        if not files:
            return "最新一か月で更新されたファイルはありません。"
        
        # ファイル情報をまとめる
        file_summary = []
        for file_info in files[:10]:  # 最新10ファイルまで分析
            content = self.read_file_content(file_info["path"])
            file_summary.append(f"ファイル: {file_info['path']}\n更新日時: {file_info['modified']}\n内容サンプル:\n{content[:500]}...\n")
        
        prompt = f"""
以下のファイルは最新一か月で更新されたファイルです。
これらのファイルの変更点や特徴を分析して、簡潔にまとめてください。

ファイル一覧と内容:
{chr(10).join(file_summary)}

分析してほしい点:
1. どのような種類のファイルが更新されているか
2. 主な変更内容の傾向
3. 開発やプロジェクトの進行状況
4. 注目すべき変更点
5. Obsidianのマークダウンファイル（.md）がある場合は、そのノート内容や構造の特徴

日本語で回答してください。
"""
        
        return self.ollama.generate(self.model, prompt)
    
    def generate_report(self, folder_path: str, days: int = 30) -> Dict[str, Any]:
        """フォルダの更新レポートを生成"""
        try:
            recent_files = self.find_recent_files(folder_path, days)
            analysis = self.analyze_file_changes(recent_files)
            
            return {
                "folder_path": folder_path,
                "analysis_period_days": days,
                "total_files_found": len(recent_files),
                "files": recent_files,
                "analysis": analysis,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": f"レポート生成中にエラーが発生しました: {str(e)}",
                "generated_at": datetime.now().isoformat()
            }