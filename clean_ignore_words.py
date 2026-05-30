#!/usr/bin/env python3
import csv

input_path = 'ignore_words.csv'
output_path = 'ignore_words.csv'

rows = []
with open(input_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row and row[0].strip():
            first = row[0].strip()
            if first != 'chinese':  # skip header row if present
                rows.append(first)

with open(output_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for word in rows:
        writer.writerow([word])

print(f"Done. Kept {len(rows)} words.")
