import os

def find_missing_memos(start_dir):
    missing = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                memo_path = os.path.join(root, file.replace('.md', '.memo'))
                if not os.path.exists(memo_path):
                    missing.append(md_path)
    return missing

if __name__ == "__main__":
    missing_files = find_missing_memos('.')
    if missing_files:
        for f in missing_files:
            print(f)
    else:
        print("No missing memos found.")
