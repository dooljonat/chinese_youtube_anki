import csv
import re
import sys

def is_word_or_short_compound(text):
    # Must contain at least one Chinese character
    if not re.search(r'[\u4e00-\u9fff]', text):
        return False
    # Must not contain English letters (excludes English questions/sentences)
    if re.search(r'[a-zA-Z]', text):
        return False
    # Must not end with sentence-ending punctuation (excludes full sentences)
    if re.search(r'[？！。…]', text):
        return False
    # Keep it short: 6 Chinese characters or fewer (excludes long phrases/sentences)
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) > 6:
        return False
    return True

def convert(input_file, output_file):
    words = []
    with open(input_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("Front\t"):
                continue
            front = line.split("\t")[0].strip()
            if front and is_word_or_short_compound(front):
                words.append(front)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["word"])
        for word in words:
            writer.writerow([word])

    print(f"Wrote {len(words)} words to {output_file}")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "Chinese_Vocab_Custom.txt"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "Chinese_Vocab_Custom.csv"
    convert(input_file, output_file)
