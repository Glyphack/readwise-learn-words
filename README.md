# readwise-language-learn

This project helps with learning words from the books you read by providing definitions and examples.
The translation is done using OpenAI.

The final result looks like [this](https://github.com/Glyphack/readwise-learn-words/issues/1).

## How to setup

You need [Readwise API key](https://readwise.io/api_deets) and [OpenAI key](https://platform.openai.com/account/api-keys)
Follow the `secrets.py` to update the env var

You have to tag the highlights that contain a word you want to learn with "w" tag.

Run:

```
uv run src/main.py
```

Now all the highlights with tag "w" are updated with new notes.
