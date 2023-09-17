import requests

from readwise_language_learn.secrets import READWISE_API_TOKEN
from readwise_language_learn.dictionary import get_definition_and_examples

def get_word_highlights():
    url = "https://readwise.io/api/v2/export/"
    headers = {
        "Authorization": f"Token {READWISE_API_TOKEN}"
    }
    params = {}

    words = []
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()

            for book in data["results"]:
                for highlight in book["highlights"]:
                    for tags in highlight["tags"]:
                        if tags["name"] == "word":
                            words.append(highlight)
        else:
            print(
                    "Error: Unable to fetch highlights." \
                    f"Status code: {response.status_code}"
                    )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return words

def add_definition_and_examples(highlight, definition, examples):
    url = f'https://readwise.io/api/v2/highlights/{highlight["id"]}/'
    headers = {
        "Authorization": f"Token {READWISE_API_TOKEN}"
    }
    text_definition = "No definition found."
    text_examples = "No examples found."
    if definition:
        text_definition = "\n".join([f"{i+1}. {d}" for i, d in enumerate(definition)])
    if examples:
        text_examples = "\n".join([f"{i+1}. {e}" for i, e in enumerate(examples)])
    data = {
        "note": highlight["note"] + "\nDefinition:\n" + text_definition + "\nExamples:\n" + text_examples,
    }
    response = requests.patch(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Successfully updated highlight.")
    else:
        print(
                "Error: Unable to update highlight." \
                f"Status code: {response.status_code}" \
                f"Response: {response.content}"
        )

def update_word_tags(highlight):
    highlight_url = f"https://readwise.io/api/v2/highlights/{highlight['id']}/"
    headers = {
        "Authorization": f"Token {READWISE_API_TOKEN}"
    }

    for tag in highlight["tags"]:
        if tag["name"] == "word":
            tag_id = tag["id"]
            delete_tag_url = highlight_url + f"tags/{tag_id}/"
            name = "words-defined"
            data = {
                "name": name
            }
            response = requests.patch(delete_tag_url, headers=headers, data=data)
            if response.status_code == 200:
                print("Successfully updated tag.")
            else:
                print(
                        "Error: Unable to delete tag." \
                        f"Status code: {response.status_code}" \
                        f"Response: {response.content}"
                
                )

word_highlights = get_word_highlights()

print(f"Found {len(word_highlights)} words.")

if not word_highlights:
    print("No words found.")

for word_highlight in word_highlights:
    word = word_highlight["text"]
    print(f"Word: {word}")
    definition, examples = get_definition_and_examples(word)
    print(f"Definition: {definition}")
    print(f"Examples: {examples}")
    if not definition:
        continue
    add_definition_and_examples(word_highlight, definition, examples)
    update_word_tags(word_highlight)
