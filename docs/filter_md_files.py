import os

def get_md_files_to_process(root_dir):
    md_files_to_process = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".md"):
                md_file_path = os.path.join(dirpath, filename)
                memo_file_path = md_file_path.replace(".md", ".memo")
                if not os.path.exists(memo_file_path):
                    md_files_to_process.append(md_file_path)
    return md_files_to_process

if __name__ == "__main__":
    docs_dir = r"G:\repogitory\site_mkdoc_ai_news\docs"
    files = get_md_files_to_process(docs_dir)
    for f in files:
        print(f)