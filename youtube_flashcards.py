#!/usr/bin/env python3

import sys
import csv
import re
import time
from pathlib import Path

import jieba
from pypinyin import pinyin, Style
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled
from deep_translator import GoogleTranslator


CHINESE_CODES = ['zh', 'zh-Hans', 'zh-CN', 'zh-TW', 'zh-Hant']


def extract_video_id(url: str) -> str:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")


def fetch_chinese_transcript(video_id: str) -> str:
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Prefer manually created transcripts, fall back to auto-generated
    for find in [
        lambda: transcript_list.find_manually_created_transcript(CHINESE_CODES),
        lambda: transcript_list.find_generated_transcript(CHINESE_CODES),
    ]:
        try:
            transcript = find()
            print(f"  Found transcript: {transcript.language} ({transcript.language_code})")
            entries = transcript.fetch()
            return ' '.join(entry['text'] for entry in entries)
        except Exception:
            continue

    available = [t.language_code for t in transcript_list]
    raise NoTranscriptFound(
        video_id,
        CHINESE_CODES,
        f"No Chinese transcript found. Available: {available}",
    )


def load_ignore_words(path: str) -> set:
    ignore = set()
    if not Path(path).exists():
        print(f"  No ignore file found at '{path}', skipping filter")
        return ignore
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            for word in row:
                word = word.strip()
                if word:
                    ignore.add(word)
    return ignore


def is_chinese(text: str) -> bool:
    return bool(re.search(r'[一-鿿]', text))


def segment_and_filter(text: str, ignore_words: set) -> list:
    seen = set()
    result = []
    for word in jieba.cut(text):
        word = word.strip()
        if not word or not is_chinese(word) or word in ignore_words or word in seen:
            continue
        seen.add(word)
        result.append(word)
    return result


def get_pinyin(word: str) -> str:
    return ' '.join(''.join(syllable) for syllable in pinyin(word, style=Style.TONE))


def translate_words(words: list, batch_size: int = 50) -> list:
    translator = GoogleTranslator(source='zh-CN', target='en')
    results = []
    total = len(words)

    for batch_start in range(0, total, batch_size):
        batch = words[batch_start:batch_start + batch_size]
        print(f"  Translating words {batch_start + 1}–{min(batch_start + batch_size, total)} of {total}...")

        # Send as newline-separated batch — much faster than one request per word
        try:
            combined = '\n'.join(batch)
            translated = translator.translate(combined)
            translations = translated.split('\n')

            # Pad if the response came back short
            while len(translations) < len(batch):
                translations.append('???')

            for word, eng in zip(batch, translations):
                results.append({
                    'chinese': word,
                    'pinyin': get_pinyin(word),
                    'english': eng.strip(),
                })
        except Exception as e:
            print(f"  Batch failed ({e}), falling back to word-by-word...")
            for word in batch:
                try:
                    eng = translator.translate(word)
                    time.sleep(0.2)
                except Exception:
                    eng = '???'
                results.append({
                    'chinese': word,
                    'pinyin': get_pinyin(word),
                    'english': eng,
                })

        # Small pause between batches to avoid rate limiting
        if batch_start + batch_size < total:
            time.sleep(0.5)

    return results


def write_csv(flashcards: list, output_path: str):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['chinese', 'pinyin', 'english'])
        writer.writeheader()
        writer.writerows(flashcards)


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else input("YouTube URL: ").strip()
    ignore_path = 'ignore_words.csv'

    print("\n[1/5] Extracting video ID...")
    video_id = extract_video_id(url)
    print(f"  Video ID: {video_id}")

    print("\n[2/5] Fetching Chinese transcript...")
    text = fetch_chinese_transcript(video_id)
    print(f"  Transcript: {len(text)} characters")

    print("\n[3/5] Loading ignore words...")
    ignore_words = load_ignore_words(ignore_path)
    print(f"  Ignoring {len(ignore_words)} words")

    print("\n[4/5] Segmenting and filtering...")
    words = segment_and_filter(text, ignore_words)
    print(f"  {len(words)} unique words to translate")

    print("\n[5/5] Translating...")
    flashcards = translate_words(words)

    output_path = f"flashcards_{video_id}.csv"
    write_csv(flashcards, output_path)
    print(f"\nDone. Saved {len(flashcards)} flashcards to '{output_path}'")


if __name__ == '__main__':
    main()
