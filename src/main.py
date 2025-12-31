import secrets
import string

import requests
import argparse
from typing import Optional
from models import Highlight, SyncedData, HighlightWithMeaning

url = "https://readwise.io/api/v2/export/"
headers = {"Authorization": f"Token {secrets.READWISE_API_KEY}"}
synced_path = "synced_words.json"

# Command-line arguments
parser = argparse.ArgumentParser(description="Sync words from Readwise to Anki")
parser.add_argument(
    "--no-anki",
    "--disable-anki",
    action="store_true",
    dest="no_anki",
    help="Disable syncing to Anki",
    default=True,
)
parser.add_argument(
    "--delete-synced-words",
    action="store_true",
    dest="delete_synced_words",
    help="Delete synced words from Readwise after saving to JSON",
    default=False,
)
args = parser.parse_args()


def get_word_highlights(updated_after=None):
    params = {}
    words: list[Highlight] = []
    total_highlights = 0
    next_page_cursor = None
    while True:
        params = {}
        if next_page_cursor:
            params["pageCursor"] = next_page_cursor
        if updated_after:
            params["updatedAfter"] = updated_after
        print("Making export api request with params " + str(params) + "...")
        response = requests.get(
            url="https://readwise.io/api/v2/export/",
            params=params,
            headers=headers,
        )

        for book in response.json()["results"]:
            for highlight in book["highlights"]:
                total_highlights += 1
                if any(tag["name"] == "w" for tag in highlight["tags"]):
                    words.append(Highlight.from_dict(highlight))
        next_page_cursor = response.json().get("nextPageCursor")
        if not next_page_cursor:
            break

    print(f"Total highlights processed: {total_highlights}")
    print(f"Total words found: {len(words)}")
    return words


def update_highlight(highlight: Highlight, data):
    url = f"https://readwise.io/api/v2/highlights/{highlight.id}/"
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Successfully updated highlight", data)
    else:
        print(
            "Error: Unable to update highlight."
            f"Status code: {response.status_code}"
            f"Response: {response.content}"
        )


def delete_highlight(highlight: Highlight):
    url = f"https://readwise.io/api/v2/highlights/{highlight.id}/"
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Successfully deleted highlight: {highlight.text}")
        return True
    else:
        print(
            "Error: Unable to delete highlight."
            f"Status code: {response.status_code}"
            f"Response: {response.content}"
        )
        return False


def get_definition(word):
    prompt_word_only = """I am a native Persian speaker trying to learn English. 

Please translate the English word or phrase "{phrase}" to Persian.
If there are multiple meanings provide all of them and the context each one is used.

The output should be:
The pronunciation of the english word or phrase in english. For example for library write: lahy-brer-ee.
the meaning in persian.
The meaning in english. Explain it for uncommon or old words and phrases.

For example when the word is "Bellicose":

bel-i-kohs
ستیزه‌جو
"Bellicose" is an adjective used to describe someone who is eager to fight or prone to aggression and hostility.
"""
    import llm

    model = llm.get_model("gpt-4o-mini")
    model.key = secrets.OPENAI_API_KEY
    response = model.prompt(prompt_word_only.format(phrase=word))
    return response.text()


def remove_edge_symbols(text):
    symbols = string.punctuation
    cleaned_text = text.strip(symbols)
    return cleaned_text


def is_placeholder_note(note: Optional[str]) -> bool:
    """
    A note is considered a placeholder when it is missing or only contains the
    Readwise tag marker ``.w``.
    """
    return note is None or note.strip() == ".w" or note.strip() == "..w"


def create_flashcards(highlights: list[Highlight]):
    flashcards = []
    for highlight in highlights:
        question = highlight.text
        answer = highlight.note
        flashcards.append({"question": question, "answer": answer})
    return flashcards


def add_flashcards_to_anki(flashcards):
    anki_connect_url = "http://localhost:8765"
    deck_name = "Learn Words"
    model_name = "Basic"

    create_deck_payload = {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": deck_name},
    }
    requests.post(anki_connect_url, json=create_deck_payload)

    find_notes_payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f'deck:"{deck_name}"'},
    }
    find_notes_response = requests.post(anki_connect_url, json=find_notes_payload)
    note_ids = find_notes_response.json().get("result", [])

    notes_info_payload = {
        "action": "notesInfo",
        "version": 6,
        "params": {"notes": note_ids},
    }
    notes_info_response = requests.post(anki_connect_url, json=notes_info_payload)
    notes_info = notes_info_response.json().get("result", [])

    existing_questions = {note["fields"]["Front"]["value"] for note in notes_info}

    added_count = 0
    for flashcard in flashcards:
        if flashcard["question"] not in existing_questions:
            add_note_payload = {
                "action": "addNote",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": deck_name,
                        "modelName": model_name,
                        "fields": {
                            "Front": flashcard["question"],
                            "Back": flashcard["answer"],
                        },
                        "tags": [],
                    }
                },
            }
            response = requests.post(anki_connect_url, json=add_note_payload)
            if response.json().get("error"):
                print(f"Error adding flashcard: {response.json()['error']}")
            else:
                added_count += 1

    print(f"Total flashcards added: {added_count}")


synced_data = SyncedData.load(synced_path)
updated_after = synced_data.last_synced_at
if updated_after:
    print(f"Fetching highlights updated after {updated_after}")
all_word_highlights = get_word_highlights(updated_after)

if not all_word_highlights:
    print("No new highlights found")
    exit()

existing_words = {
    word
    for word, meaning in synced_data.words.items()
    if not is_placeholder_note(meaning)
}

new_word_highlights = [h for h in all_word_highlights if h.text not in existing_words]

skipped = len(all_word_highlights) - len(new_word_highlights)
if skipped > 0:
    print(f"Skipping {skipped} already synced words.")
if not new_word_highlights:
    print("No words found.")

highlights_with_meanings = []
for highlight in new_word_highlights:
    word = highlight.text
    print(f"Processing word: {word}")
    text = remove_edge_symbols(word)
    definition = get_definition(word)
    meaning = f"{definition}"
    highlights_with_meanings.append(
        HighlightWithMeaning(highlight=highlight, meaning=meaning)
    )

print(f"Total highlights translated: {len(highlights_with_meanings)}")


if args.no_anki:
    print("Skipping Anki sync as requested.")
else:
    flashcards = [
        {"question": remove_edge_symbols(hwm.highlight.text), "answer": hwm.meaning}
        for hwm in highlights_with_meanings
    ]
    print("Adding flashcards to Anki...")
    add_flashcards_to_anki(flashcards)
    print("Flashcards added to Anki.")

new_words = {
    remove_edge_symbols(hwm.highlight.text): hwm.meaning
    for hwm in highlights_with_meanings
}
synced_data.words.update(new_words)

if all_word_highlights:
    last_synced_at = max(all_word_highlights, key=lambda h: h.updated_at).updated_at
    synced_data.last_synced_at = last_synced_at

print(synced_data.last_synced_at)
synced_data.save(synced_path)
print("Wrote synced words and latest highlight to synced_words.json")

# Either delete or update highlights in Readwise
if args.delete_synced_words:
    print("Deleting synced words from Readwise...")
    deleted_count = 0
    for hwm in highlights_with_meanings:
        if delete_highlight(hwm.highlight):
            deleted_count += 1
    print(f"Total highlights deleted: {deleted_count}")
else:
    print("Updating highlights in Readwise with meanings...")
    updated_count = 0
    for hwm in highlights_with_meanings:
        hwm.highlight.text = remove_edge_symbols(hwm.highlight.text)
        hwm.highlight.note = hwm.meaning
        update_highlight(
            hwm.highlight, {"text": hwm.highlight.text, "note": hwm.highlight.note}
        )
        updated_count += 1
    print(f"Total highlights updated: {updated_count}")
