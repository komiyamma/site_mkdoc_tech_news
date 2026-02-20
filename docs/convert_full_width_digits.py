import os
import re

def convert_full_width_to_half_width(text):
    """
    全角数字（０-９）を半角数字（0-9）に変換する
    """
    # ０-９ (U+FF10 - U+FF19) を 0-9 (U+0030 - U+0039) に変換
    # ． (U+FF0E) を . (U+002E) に変換
    return text.translate(str.maketrans(
        '０１２３４５６７８９．',
        '0123456789.'
    ))

def process_memo_files(root_dir):
    """
    指定されたディレクトリ配下の *.memo ファイルを検索して置換処理を行う
    """
    count = 0
    modified_count = 0

    for root, dirs, files in os.walk(root_dir):
        # .venv などのディレクトリは除外
        if '.venv' in dirs:
            dirs.remove('.venv')
        
        for file in files:
            if file.endswith('.memo'):
                file_path = os.path.join(root, file)
                count += 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = convert_full_width_to_half_width(content)
                    
                    if content != new_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        modified_count += 1
                        print(f"Updated: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

    print(f"\nTotal .memo files found: {count}")
    print(f"Total files modified: {modified_count}")

if __name__ == "__main__":
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Scanning directory: {docs_dir}")
    process_memo_files(docs_dir)
