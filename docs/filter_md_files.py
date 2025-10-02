
import os
import sys

def filter_md_files(base_dir):
    """
    Finds all .md files in base_dir and its subdirectories that do not have a corresponding .memo file.
    Returns a list of absolute paths to these .md files.
    """
    target_md_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".md"):
                md_path = os.path.join(root, file)
                memo_path = os.path.join(root, file.replace(".md", ".memo"))
                if not os.path.exists(memo_path):
                    target_md_files.append(md_path)
    return target_md_files

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python filter_md_files.py <base_directory>")
        sys.exit(1)

    base_directory = sys.argv[1]
    files_to_process = filter_md_files(base_directory)
    for f in files_to_process:
        print(f)
