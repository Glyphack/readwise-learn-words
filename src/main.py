import os
import string

import argparse
from typing import Optional
from models import Highlight, SyncedData, HighlightWithMeaning
from translator import ClaudeCliTranslator, OpenAITranslator
from httpclient import http_request

synced_path = "synced_words.json"

translators = {"openai": OpenAITranslator, "claude": ClaudeCliTranslator}


class ReadwiseClient:
    export_url = "https://readwise.io/api/v2/export/"

    def __init__(self):
        self.headers = {"Authorization": f"Token {os.environ['READWISE_API_KEY']}"}

    def export_highlights(self, updated_after=None):
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
            response = http_request(
                "GET",
                self.export_url,
                headers=self.headers,
                params=params,
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

    def update_highlight(self, highlight: Highlight, data):
        url = f"https://readwise.io/api/v2/highlights/{highlight.id}/"
        response = http_request("PATCH", url, headers=self.headers, json_body=data)
        if response.status_code == 200:
            print("Successfully updated highlight", data)
            return
        print(
            "Error: Unable to update highlight."
            f"Status code: {response.status_code}"
            f"Response: {response.content}"
        )

    def delete_highlight(self, highlight: Highlight):
        url = f"https://readwise.io/api/v2/highlights/{highlight.id}/"
        response = http_request("DELETE", url, headers=self.headers)
        if response.status_code == 204:
            print(f"Successfully deleted highlight: {highlight.text}")
            return True
        print(
            "Error: Unable to delete highlight."
            f"Status code: {response.status_code}"
            f"Response: {response.content}"
        )
        return False

# Command-line arguments
parser = argparse.ArgumentParser(
    description="Sync words from Readwise and export flashcards"
)
parser.add_argument(
    "--update-words",
    action="store_true",
    dest="update_words",
    help="Read tagged highlights from Readwise, translate them, and save to JSON",
    default=False,
)
parser.add_argument(
    "--export-anki",
    action="store_true",
    dest="export_anki",
    help="Read saved words from JSON and export them to Anki",
    default=False,
)
parser.add_argument(
    "--delete-synced-words",
    action="store_true",
    dest="delete_synced_words",
    help="Delete synced words from Readwise after saving to JSON",
    default=False,
)
parser.add_argument(
    "--llm",
    choices=["openai", "claude"],
    dest="llm",
    help="LLM backend used to translate words",
    default="claude",
)
args = parser.parse_args()


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


def add_flashcards_to_anki(flashcards):
    anki_connect_url = "http://localhost:8765"
    deck_name = "Learn Words"
    model_name = "Basic"

    create_deck_payload = {
        "action": "createDeck",
        "version": 6,
        "params": {"deck": deck_name},
    }
    http_request("POST", anki_connect_url, json_body=create_deck_payload)

    find_notes_payload = {
        "action": "findNotes",
        "version": 6,
        "params": {"query": f'deck:"{deck_name}"'},
    }
    find_notes_response = http_request(
        "POST", anki_connect_url, json_body=find_notes_payload
    )
    note_ids = find_notes_response.json().get("result", [])

    notes_info_payload = {
        "action": "notesInfo",
        "version": 6,
        "params": {"notes": note_ids},
    }
    notes_info_response = http_request(
        "POST", anki_connect_url, json_body=notes_info_payload
    )
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
            response = http_request(
                "POST", anki_connect_url, json_body=add_note_payload
            )
            if response.json().get("error"):
                print(f"Error adding flashcard: {response.json()['error']}")
            else:
                added_count += 1

    print(f"Total flashcards added: {added_count}")


def update_words(client, translator):
    synced_data = SyncedData.load(synced_path)
    updated_after = synced_data.last_synced_at
    if updated_after:
        print(f"Fetching highlights updated after {updated_after}")
    all_word_highlights = client.export_highlights(updated_after)

    if not all_word_highlights:
        print("No new highlights found")
        return

    existing_words = {
        word
        for word, meaning in synced_data.words.items()
        if not is_placeholder_note(meaning)
    }

    new_word_highlights = [
        h for h in all_word_highlights if h.text not in existing_words
    ]

    skipped = len(all_word_highlights) - len(new_word_highlights)
    if skipped > 0:
        print(f"Skipping {skipped} already synced words.")
    if not new_word_highlights:
        print("No words found.")

    highlights_with_meanings = []
    for highlight in new_word_highlights:
        word = highlight.text
        print(f"Processing word: {word}")
        definition = translator.translate(word)
        highlights_with_meanings.append(
            HighlightWithMeaning(highlight=highlight, meaning=definition)
        )

    print(f"Total highlights translated: {len(highlights_with_meanings)}")

    new_words = {
        remove_edge_symbols(hwm.highlight.text): hwm.meaning
        for hwm in highlights_with_meanings
    }
    synced_data.words.update(new_words)

    last_synced_at = max(all_word_highlights, key=lambda h: h.updated_at).updated_at
    synced_data.last_synced_at = last_synced_at

    print(synced_data.last_synced_at)
    synced_data.save(synced_path)
    print("Wrote synced words and latest highlight to synced_words.json")

    if args.delete_synced_words:
        print("Deleting synced words from Readwise...")
        deleted_count = 0
        for hwm in highlights_with_meanings:
            if client.delete_highlight(hwm.highlight):
                deleted_count += 1
        print(f"Total highlights deleted: {deleted_count}")
    else:
        print("Updating highlights in Readwise with meanings...")
        updated_count = 0
        for hwm in highlights_with_meanings:
            hwm.highlight.text = remove_edge_symbols(hwm.highlight.text)
            hwm.highlight.note = hwm.meaning
            client.update_highlight(
                hwm.highlight, {"text": hwm.highlight.text, "note": hwm.highlight.note}
            )
            updated_count += 1
        print(f"Total highlights updated: {updated_count}")


def export_anki():
    synced_data = SyncedData.load(synced_path)
    flashcards = [
        {"question": remove_edge_symbols(word), "answer": meaning}
        for word, meaning in synced_data.words.items()
        if not is_placeholder_note(meaning)
    ]
    if not flashcards:
        print("No words to export.")
        return
    print("Adding flashcards to Anki...")
    add_flashcards_to_anki(flashcards)
    print("Flashcards added to Anki.")


if not args.update_words and not args.export_anki:
    parser.error("choose at least one mode: --update-words or --export-anki")

if args.update_words:
    update_words(ReadwiseClient(), translators[args.llm]())

if args.export_anki:
    export_anki()
