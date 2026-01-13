import glob
import os

def check_length():
    memo_files = glob.glob("*.memo")
    failed = False
    for f in memo_files:
        with open(f, "r", encoding="utf-8") as file:
            content = file.read().strip()
            length = len(content)
            if not (65 <= length <= 80):
                print(f"FAIL: {f.replace('.memo', '')} (Len: {length})")
                failed = True
    
    if failed:
        exit(1)
    else:
        print("All checks passed!")
        exit(0)

if __name__ == "__main__":
    check_length()
