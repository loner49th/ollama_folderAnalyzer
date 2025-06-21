import argparse
import json
from file_analyzer import FileAnalyzer


def main():
    parser = argparse.ArgumentParser(description="特定フォルダの最新ファイルを分析するツール")
    parser.add_argument("folder", help="分析対象のフォルダパス")
    parser.add_argument("--days", type=int, default=30, help="分析期間（日数、デフォルト：30日）")
    parser.add_argument("--model", default="llama3.2", help="使用するOllamaモデル（デフォルト：llama3.2）")
    parser.add_argument("--output", help="結果を保存するJSONファイルパス")
    
    args = parser.parse_args()
    
    print(f"フォルダ「{args.folder}」の最新{args.days}日間のファイルを分析中...")
    
    analyzer = FileAnalyzer(ollama_model=args.model)
    report = analyzer.generate_report(args.folder, args.days)
    
    if "error" in report:
        print(f"エラー: {report['error']}")
        return
    
    print(f"\n=== 分析結果 ===")
    print(f"対象フォルダ: {report['folder_path']}")
    print(f"分析期間: {report['analysis_period_days']}日間")
    print(f"更新されたファイル数: {report['total_files_found']}個")
    print(f"\n=== 更新ファイル一覧 ===")
    
    for file_info in report['files'][:5]:  # 最新5ファイル表示
        print(f"- {file_info['path']} ({file_info['modified']})")
    
    if len(report['files']) > 5:
        print(f"... 他{len(report['files'])-5}個のファイル")
    
    print(f"\n=== AI分析結果 ===")
    print(report['analysis'])
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n結果を {args.output} に保存しました。")


if __name__ == "__main__":
    main()
