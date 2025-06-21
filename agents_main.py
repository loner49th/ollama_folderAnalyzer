import argparse
import asyncio
import os
from pathlib import Path
from agents_file_analyzer import FileAnalyzerAgent


def print_setup_instructions():
    """セットアップ手順を表示"""
    print("""
=== OpenAI API セットアップ手順 ===

1. OpenAI APIキーの取得:
   - https://platform.openai.com/api-keys にアクセス
   - 新しいAPIキーを作成

2. 環境変数の設定:
   export OPENAI_API_KEY="your-api-key"

   または .envファイルに記載:
   OPENAI_API_KEY=your-api-key

3. 依存関係のインストール:
   uv sync

4. 実行:
   python agents_main.py /path/to/folder
""")


async def main_async():
    """非同期メイン関数"""
    parser = argparse.ArgumentParser(
        description="OpenAI Agents SDKを使用したファイル分析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python agents_main.py /path/to/folder
  python agents_main.py /path/to/folder --days 7 --output report.json
  python agents_main.py --test-connection
  python agents_main.py --setup
        """
    )
    
    parser.add_argument("folder", nargs="?", help="分析対象のフォルダパス")
    parser.add_argument("--days", type=int, default=30, help="分析期間（日数、デフォルト：30日）")
    parser.add_argument("--output", help="結果を保存するJSONファイルパス")
    parser.add_argument("--test-connection", action="store_true", help="OpenAI APIへの接続テスト")
    parser.add_argument("--setup", action="store_true", help="セットアップ手順を表示")
    parser.add_argument("--sync", action="store_true", help="同期実行モードを使用")
    
    args = parser.parse_args()
    
    # セットアップ手順の表示
    if args.setup:
        print_setup_instructions()
        return
    
    # 接続テスト
    if args.test_connection:
        print("OpenAI APIへの接続をテスト中...")
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY環境変数が設定されていません。")
                print("💡 --setup オプションでセットアップ手順を確認してください。")
                return
            
            print(f"設定確認:")
            print(f"  APIキー: {'*' * (len(api_key) - 8) + api_key[-8:] if len(api_key) > 8 else '*' * len(api_key)}")
            
            analyzer = FileAnalyzerAgent()
            if analyzer.verify_connection():
                print("✅ 接続テスト成功！OpenAI APIに正常に接続できます。")
            else:
                print("❌ 接続テスト失敗。設定を確認してください。")
        except Exception as e:
            print(f"❌ 接続テストでエラーが発生: {str(e)}")
            print("\n💡 --setup オプションでセットアップ手順を確認してください。")
        return
    
    # フォルダパスの確認
    if not args.folder:
        print("エラー: フォルダパスが指定されていません。")
        print("使用方法: python agents_main.py /path/to/folder")
        print("詳細は --help オプションを参照してください。")
        return
    
    print(f"フォルダ「{args.folder}」の最新{args.days}日間のファイルをOpenAI APIで分析中...")
    print("🔄 OpenAI API + OpenAI Agents SDKを使用しています...")
    
    try:
        analyzer = FileAnalyzerAgent()
        
        if args.sync:
            # 同期実行
            result = analyzer.analyze_folder_sync(
                folder_path=args.folder,
                days=args.days,
                output_path=args.output
            )
        else:
            # 非同期実行
            result = await analyzer.analyze_folder(
                folder_path=args.folder,
                days=args.days,
                output_path=args.output
            )
        
        print("\n" + "="*50)
        print("🤖 OpenAI AIエージェント分析結果")
        print("="*50)
        print(result)
        
        if args.output:
            print(f"\n📄 詳細レポートは {args.output} に保存されました。")
        
    except ValueError as e:
        print(f"❌ 設定エラー: {str(e)}")
        print("💡 --setup オプションでセットアップ手順を確認してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        print("\n考えられる原因:")
        print("- OpenAI APIキーが正しく設定されていない")
        print("- 指定されたフォルダが存在しない")
        print("- ネットワーク接続の問題")
        print("- OpenAI APIの利用制限に達している")
        print("\n💡 --test-connection オプションで接続を確認してください。")


def main():
    """メイン関数（同期版）"""
    parser = argparse.ArgumentParser(
        description="OpenAI Agents SDKを使用したファイル分析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python agents_main.py /path/to/folder
  python agents_main.py /path/to/folder --days 7 --output report.json
  python agents_main.py --test-connection
  python agents_main.py --setup
        """
    )
    
    parser.add_argument("folder", nargs="?", help="分析対象のフォルダパス")
    parser.add_argument("--days", type=int, default=30, help="分析期間（日数、デフォルト：30日）")
    parser.add_argument("--output", help="結果を保存するJSONファイルパス")
    parser.add_argument("--test-connection", action="store_true", help="OpenAI APIへの接続テスト")
    parser.add_argument("--setup", action="store_true", help="セットアップ手順を表示")
    
    args = parser.parse_args()
    
    # セットアップ手順の表示
    if args.setup:
        print_setup_instructions()
        return
    
    # 接続テスト
    if args.test_connection:
        print("OpenAI APIへの接続をテスト中...")
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OPENAI_API_KEY環境変数が設定されていません。")
                print("💡 --setup オプションでセットアップ手順を確認してください。")
                return
            
            print(f"設定確認:")
            print(f"  APIキー: {'*' * (len(api_key) - 8) + api_key[-8:] if len(api_key) > 8 else '*' * len(api_key)}")
            
            analyzer = FileAnalyzerAgent()
            if analyzer.verify_connection():
                print("✅ 接続テスト成功！OpenAI APIに正常に接続できます。")
            else:
                print("❌ 接続テスト失敗。設定を確認してください。")
        except Exception as e:
            print(f"❌ 接続テストでエラーが発生: {str(e)}")
            print("\n💡 --setup オプションでセットアップ手順を確認してください。")
        return
    
    # フォルダパスの確認
    if not args.folder:
        print("エラー: フォルダパスが指定されていません。")
        print("使用方法: python agents_main.py /path/to/folder")
        print("詳細は --help オプションを参照してください。")
        return
    
    print(f"フォルダ「{args.folder}」の最新{args.days}日間のファイルをOpenAI APIで分析中...")
    print("🔄 OpenAI API + OpenAI Agents SDKを使用しています...")
    
    try:
        analyzer = FileAnalyzerAgent()
        
        # 同期実行
        result = analyzer.analyze_folder_sync(
            folder_path=args.folder,
            days=args.days,
            output_path=args.output
        )
        
        print("\n" + "="*50)
        print("🤖 OpenAI AIエージェント分析結果")
        print("="*50)
        print(result)
        
        if args.output:
            print(f"\n📄 詳細レポートは {args.output} に保存されました。")
        
    except ValueError as e:
        print(f"❌ 設定エラー: {str(e)}")
        print("💡 --setup オプションでセットアップ手順を確認してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        print("\n考えられる原因:")
        print("- OpenAI APIキーが正しく設定されていない")
        print("- 指定されたフォルダが存在しない")
        print("- ネットワーク接続の問題")
        print("- OpenAI APIの利用制限に達している")
        print("\n💡 --test-connection オプションで接続を確認してください。")


if __name__ == "__main__":
    import sys
    
    # 非同期実行を希望する場合
    if "--async" in sys.argv:
        sys.argv.remove("--async")
        asyncio.run(main_async())
    else:
        # デフォルトは同期実行
        main()