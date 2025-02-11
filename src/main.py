import secrets
import string

import requests

url = "https://readwise.io/api/v2/export/"
headers = {"Authorization": f"Token {secrets.READWISE_API_TOKEN}"}


def get_word_highlights(updated_after=None):
    params = {}
    words = []
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
                for tags in highlight["tags"]:
                    if tags["name"] in "w":
                        words.append(highlight)
        next_page_cursor = response.json().get("nextPageCursor")
        if not next_page_cursor:
            break

    print(f"Total highlights processed: {total_highlights}")
    print(f"Total words found: {len(words)}")
    return words


def update_highlight(highlight, data):
    url = f'https://readwise.io/api/v2/highlights/{highlight["id"]}/'
    response = requests.patch(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Successfully updated highlight", data)
    else:
        print(
            "Error: Unable to update highlight."
            f"Status code: {response.status_code}"
            f"Response: {response.content}"
        )


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

    model = llm.get_model("gpt-4o")
    model.key = secrets.OPENAI_API_KEY
    response = model.prompt(prompt_word_only.format(phrase=word))
    return response.text()


def remove_edge_symbols(text):
    symbols = string.punctuation
    cleaned_text = text.strip(symbols)
    return cleaned_text


def create_flashcards(highlights):
    flashcards = []
    for highlight in highlights:
        question = highlight["text"]
        answer = highlight["note"]
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


word_highlights = get_word_highlights()

if not word_highlights:
    print("No words found.")

updated_count = 0

for highlight in word_highlights:
    word = highlight["text"]
    print(f"Word: {word}")
    new_word = remove_edge_symbols(word)
    if new_word != word:
        update_highlight(highlight, {"text": new_word})
        word = new_word
        updated_count += 1
    if highlight["note"] is not None:
        continue
    note = get_definition(word)
    update_highlight(highlight, {"note": note})
    updated_count += 1
    print("updated highlight with new note")

flashcards = create_flashcards(word_highlights)
print(f"Total highlights updated: {updated_count}")
print("Adding flashcards to Anki...")
add_flashcards_to_anki(flashcards)
print("Flashcards added to Anki.")
