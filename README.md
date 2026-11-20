# Readwise Learn Words

This project helps with learning words from the books you read by providing definitions and examples.
The translation is done using LLMs. I found LLMs to be useful here because they can provide examples, pronunciation, and describing the word.

The final result looks like [this](https://github.com/Glyphack/readwise-learn-words/issues/1).


## How it Works

When I encounter a new word, I highlight it with tag "w".
This program finds all such highlights and the uses an LLM for creating a description for the word and saves it in `synced_words.json`.
Then I run the program with a flag to export the words as flashcards in Anki.

This is highly personal software. The prompt I'm using is translates to Persian. So change the code for your use.

## How to setup

You need [Readwise API key](https://readwise.io/api_deets) and OpenAI or Claude key.
Set the `READWISE_API_KEY` environment variable before running the update mode.

You have to tag the highlights that contain a word you want to learn with "w" tag.

The script runs in two modes.

Update words reads the highlights tagged with "w" from Readwise, translates them, saves them to `synced_words.json`, and writes the meaning back into each highlight note:

```
uv run src/main.py --update-words
```

Export anki reads the saved words from `synced_words.json` and adds them as flashcards to a local Anki deck through AnkiConnect:

```
uv run src/main.py --export-anki
```
