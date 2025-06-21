import argparse
import asyncio
import sys
from pathlib import Path
from azure_agents_file_analyzer import AzureFileAnalyzerAgent, AzureConfig


def print_setup_instructions():
    """セットアップ手順を表示"""
    print("""
=== Azure OpenAI Service セットアップ手順 ===

1. .envファイルの作成:
   cp .env.template .env

2. .envファイルの編集:
   以下の値を実際のAzure OpenAI Serviceの設定に置き換えてください:
   - AZURE_OPENAI_API_KEY=your_api_key
   - AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   - AZURE_OPENAI_DEPLOYMENT=your-deployment-name

3. Azure OpenAI Serviceの設定値の取得方法:
   - Azure ポータル > あなたのOpenAIリソース > キーとエンドポイント
   - Azure ポータル > あなたのOpenAIリソース > モデル デプロイ

4. 依存関係のインストール:
   uv sync

5. 実行:
   python azure_agents_main.py /path/to/folder
""")


async def main_async():
    """非同期メイン関数"""
    parser = argparse.ArgumentParser(
        description="Azure OpenAI Service + OpenAI Agents SDKを使用したファイル分析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python azure_agents_main.py /path/to/folder
  python azure_agents_main.py /path/to/folder --days 7 --output report.json
  python azure_agents_main.py --test-connection
  python azure_agents_main.py --setup
        """
    )
    
    parser.add_argument("folder", nargs="?", help="分析対象のフォルダパス")
    parser.add_argument("--days", type=int, default=30, help="分析期間（日数、デフォルト：30日）")
    parser.add_argument("--output", help="結果を保存するJSONファイルパス")
    parser.add_argument("--test-connection", action="store_true", help="Azure OpenAI Serviceへの接続テスト")
    parser.add_argument("--setup", action="store_true", help="セットアップ手順を表示")
    parser.add_argument("--sync", action="store_true", help="同期実行モードを使用")
    
    args = parser.parse_args()
    
    # セットアップ手順の表示
    if args.setup:
        print_setup_instructions()
        return
    
    # 接続テスト
    if args.test_connection:
        print("Azure OpenAI Serviceへの接続をテスト中...")
        try:
            config = AzureConfig.from_env()
            print(f"設定読み込み成功:")
            print(f"  エンドポイント: {config.endpoint}")
            print(f"  デプロイメント: {config.deployment}")
            print(f"  APIバージョン: {config.api_version}")
            
            analyzer = AzureFileAnalyzerAgent(config)
            if analyzer.verify_connection():
                print("✅ 接続テスト成功！Azure OpenAI Serviceに正常に接続できます。")
            else:
                print("❌ 接続テスト失敗。設定を確認してください。")
        except Exception as e:
            print(f"❌ 接続テストでエラーが発生: {str(e)}")
            print("\n💡 --setup オプションでセットアップ手順を確認してください。")
        return
    
    # フォルダパスの確認
    if not args.folder:
        print("エラー: フォルダパスが指定されていません。")
        print("使用方法: python azure_agents_main.py /path/to/folder")
        print("詳細は --help オプションを参照してください。")
        return
    
    # .envファイルの存在確認
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .envファイルが見つかりません。")
        print("💡 --setup オプションでセットアップ手順を確認してください。")
        return
    
    print(f"フォルダ「{args.folder}」の最新{args.days}日間のファイルをAzure OpenAI Serviceで分析中...")
    print("🔄 Azure OpenAI Service + OpenAI Agents SDKを使用しています...")
    
    try:
        # 設定の読み込み
        config = AzureConfig.from_env()
        analyzer = AzureFileAnalyzerAgent(config)
        
        # 分析の実行
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
        print("🤖 Azure AIエージェント分析結果")
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
        print("- Azure OpenAI Serviceの設定が正しくない")
        print("- 指定されたフォルダが存在しない") 
        print("- ネットワーク接続の問題")
        print("- デプロイメントが存在しないか、利用できない状態")
        print("\n💡 --test-connection オプションで接続を確認してください。")


def main():
    """メイン関数（同期版）"""
    parser = argparse.ArgumentParser(
        description="Azure OpenAI Service + OpenAI Agents SDKを使用したファイル分析ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python azure_agents_main.py /path/to/folder
  python azure_agents_main.py /path/to/folder --days 7 --output report.json
  python azure_agents_main.py --test-connection
  python azure_agents_main.py --setup
        """
    )
    
    parser.add_argument("folder", nargs="?", help="分析対象のフォルダパス")
    parser.add_argument("--days", type=int, default=30, help="分析期間（日数、デフォルト：30日）")
    parser.add_argument("--output", help="結果を保存するJSONファイルパス")
    parser.add_argument("--test-connection", action="store_true", help="Azure OpenAI Serviceへの接続テスト")
    parser.add_argument("--setup", action="store_true", help="セットアップ手順を表示")
    
    args = parser.parse_args()
    
    # セットアップ手順の表示
    if args.setup:
        print_setup_instructions()
        return
    
    # 接続テスト
    if args.test_connection:
        print("Azure OpenAI Serviceへの接続をテスト中...")
        try:
            config = AzureConfig.from_env()
            print(f"設定読み込み成功:")
            print(f"  エンドポイント: {config.endpoint}")
            print(f"  デプロイメント: {config.deployment}")
            print(f"  APIバージョン: {config.api_version}")
            
            analyzer = AzureFileAnalyzerAgent(config)
            if analyzer.verify_connection():
                print("✅ 接続テスト成功！Azure OpenAI Serviceに正常に接続できます。")
            else:
                print("❌ 接続テスト失敗。設定を確認してください。")
        except Exception as e:
            print(f"❌ 接続テストでエラーが発生: {str(e)}")
            print("\n💡 --setup オプションでセットアップ手順を確認してください。")
        return
    
    # フォルダパスの確認
    if not args.folder:
        print("エラー: フォルダパスが指定されていません。")
        print("使用方法: python azure_agents_main.py /path/to/folder")
        print("詳細は --help オプションを参照してください。")
        return
    
    # .envファイルの存在確認
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .envファイルが見つかりません。")
        print("💡 --setup オプションでセットアップ手順を確認してください。")
        return
    
    print(f"フォルダ「{args.folder}」の最新{args.days}日間のファイルをAzure OpenAI Serviceで分析中...")
    print("🔄 Azure OpenAI Service + OpenAI Agents SDKを使用しています...")
    
    try:
        # 設定の読み込み
        config = AzureConfig.from_env()
        analyzer = AzureFileAnalyzerAgent(config)
        
        # 同期実行
        result = analyzer.analyze_folder_sync(
            folder_path=args.folder,
            days=args.days,
            output_path=args.output
        )
        
        print("\n" + "="*50)
        print("🤖 Azure AIエージェント分析結果")
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
        print("- Azure OpenAI Serviceの設定が正しくない")
        print("- 指定されたフォルダが存在しない")
        print("- ネットワーク接続の問題")
        print("- デプロイメントが存在しないか、利用できない状態")
        print("\n💡 --test-connection オプションで接続を確認してください。")


if __name__ == "__main__":
    # 非同期実行を希望する場合
    if "--async" in sys.argv:
        sys.argv.remove("--async")
        asyncio.run(main_async())
    else:
        # デフォルトは同期実行
        main()