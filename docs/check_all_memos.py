import os
import subprocess

def check_all_memos(start_dir):
    failed = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.memo'):
                memo_path = os.path.join(root, file)
                result = subprocess.run(['python', 'check_memo_length.py', memo_path], capture_output=True, text=True)
                if "FAIL" in result.stdout:
                    failed.append((memo_path, result.stdout.strip()))
    return failed

if __name__ == "__main__":
    failed_memos = check_all_memos('.')
    if failed_memos:
        for path, msg in failed_memos:
            print(msg)
    else:
        print("All memos passed.")
