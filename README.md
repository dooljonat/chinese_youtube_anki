# YouTube Chinese Flashcard Generator

Downloads the Chinese transcript from a YouTube video, extracts vocabulary, and exports a CSV of flashcards with pinyin and English translations.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

### `youtube_flashcards.py` — Generate flashcards from a video

```bash
python3 youtube_flashcards.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

Or run without arguments to be prompted for the URL:

```bash
python3 youtube_flashcards.py
```

Output is saved as `flashcards_VIDEO_ID.csv` in the current directory with two columns:

| chinese | pinyin & english |
|---------|-----------------|
| 学习 | xué xí / to study |

The script skips any words listed in `ignore_words.csv`.

---

### `clean_ignore_words.py` — Strip extra columns from `ignore_words.csv`

If your `ignore_words.csv` has extra columns (e.g. pinyin, english), run this to keep only the first column:

```bash
python3 clean_ignore_words.py
```

The file is updated in place.

---

## Customising the ignore list

Add words to `ignore_words.csv` (one word per row) to prevent them from appearing in your flashcards. The file already includes common particles, pronouns, numbers, and function words.
