import os, re
from mutagen.easyid3 import EasyID3

SOURCE_DIR = os.getenv("MUSIC_SOURCE_DIR", "/music")
SUPPORTED_EXTENSIONS = ('.mp3', '.wav', '.flac')


def scan_folder(path=None):
    if path is None:
        path = SOURCE_DIR

    files = []
    seen = set()

    for root, dirs, filenames in os.walk(path):
        for name in filenames:

            # ✅ filter first
            if not name.lower().endswith(SUPPORTED_EXTENSIONS):
                continue

            full_path = os.path.join(root, name)

            # ✅ avoid duplicates
            if full_path in seen:
                continue

            seen.add(full_path)

            # ✅ metadata extraction
            metadata = get_metadata(full_path)

            # ✅ fallback if needed
            if metadata["artist"] == "Unknown" and metadata["title"] == "Unknown":
                metadata = parse_filename(full_path)

            # ✅ cleaning
            metadata["artist"] = clean_text(metadata["artist"])
            metadata["title"] = clean_text(metadata["title"])
            metadata["artist"] = normalize_artist(metadata["artist"])

            # ✅ build track
            track = {
                "path": full_path,
                "artist": metadata["artist"],
                "title": metadata["title"],
            }

            # ✅ genre classification
            track["genre"] = classify_genre(track)

            files.append(track)

    return files

def get_metadata(file_path):
    try:
        audio = EasyID3(file_path)

        artist = audio.get("artist", ["Unknown"])[0]
        title = audio.get("title", ["Unknown"])[0]

        return {
            "artist": artist.strip(),
            "title": title.strip(),
        }
    except Exception:
        return {
            "artist": "Unknown",
            "title": "Unknown",
        }

def parse_filename(file_path):
    name = os.path.basename(file_path)

    # remove extension
    name = os.path.splitext(name)[0]

    # remove leading track numbers (e.g. "01-", "02 ")
    name = name.lstrip("0123456789.-_ ")

    # normalize underscores
    name = name.replace("_", " ")

    # try split with " - "
    if " - " in name:
        parts = name.split(" - ", 1)
    elif "-" in name:
        parts = name.split("-", 1)
    else:
        return {"artist": "Unknown", "title": name.strip()}

    artist = parts[0].strip()
    title = parts[1].strip()

    return {
        "artist": artist,
        "title": title
    }

def clean_text(text):
    if not text:
        return "Unknown"

    # normalize spaces
    text = text.strip()
    text = " ".join(text.split())

    # lowercase first
    text = text.lower()

    # fix apostrophes
    text = re.sub(r"(\w)'(\w)", lambda m: m.group(1) + "'" + m.group(2), text)

    # capitalize each word
    words = text.split(" ")
    words = [w.capitalize() for w in words]
    text = " ".join(words)

    # fix common music terms (important order)
    text = re.sub(r"\bfeat\.?\b", "feat.", text, flags=re.IGNORECASE)
    text = re.sub(r"\bremix\b", "Remix", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmix\b", "Mix", text, flags=re.IGNORECASE)

    # fix double dots (important)
    text = re.sub(r"\.\.", ".", text)

    return text

def normalize_artist(text):
    text = text.replace("_", " ")
    text = text.replace(" Ft ", " feat. ")
    text = text.replace(" ft ", " feat. ")
    text = text.replace(" Feat ", " feat. ")
    text = text.replace(" feat ", " feat. ")

    return text

def group_by_artist(tracks):
    grouped = {}

    for track in tracks:
        artist = track["artist"]

        if artist not in grouped:
            grouped[artist] = []

        grouped[artist].append(track)

    return grouped

def classify_genre(track):
    title = track["title"].lower()

    if "remix" in title:
        return "House"
    if "tech" in title:
        return "Tech House"
    if "deep" in title:
        return "Deep House"

    return "Other"


def group_by_genre(tracks):
    grouped = {}

    for track in tracks:
        genre = track["genre"]

        if genre not in grouped:
            grouped[genre] = []

        grouped[genre].append(track)

    return grouped

def preview_by_genre(tracks):
    preview = []

    base_dir = os.getenv("MUSIC_OUTPUT_BASE_DIR")
    if not base_dir:
        base_dir = "C:\\All Music" if os.name == "nt" else "/music-output"

    for track in tracks:
        source = track["path"]
        genre = track["genre"]
        artist = track["artist"]
        title = track["title"]

        # ✅ get original extension (.mp3, .flac, etc.)
        _, ext = os.path.splitext(source)

        filename = f"{title}{ext}"

        destination = os.path.join(base_dir, genre, artist, filename)

        preview.append({
            "from": source,
            "to": destination,
        })

    return preview
