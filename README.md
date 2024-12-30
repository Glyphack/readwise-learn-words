# readwise-language-learn

This project helps with learning words from the books you read by providing definitions and examples.
The translation is done using OpenAI.

The final result looks like this:

![image](https://private-user-images.githubusercontent.com/20788334/399279509-72355b96-cac0-480f-bb33-d81604a7c656.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzU1NTc1NDgsIm5iZiI6MTczNTU1NzI0OCwicGF0aCI6Ii8yMDc4ODMzNC8zOTkyNzk1MDktNzIzNTViOTYtY2FjMC00ODBmLWJiMzMtZDgxNjA0YTdjNjU2LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDEyMzAlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMjMwVDExMTQwOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWVkZDU4ZmI1ZmExNDkzOGJiYzQ0YjdlYzIxYjlkYmJjNThkZGUyNDViYTNkMWJjNWU2NTViOTkwODkzOGNlYzImWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.IqBCJnrinuHlKXEoYy4EpOvwh0M2mjHrn75c0VoWFwg)

## How to setup

You need [Readwise API key](https://readwise.io/api_deets) and [OpenAI key](https://platform.openai.com/account/api-keys)
Follow the `secrets.py` to update the env var

You have to tag the highlights that contain a word you want to learn with "w" tag.

Run:

```
uv run src/main.py
```

Now all the highlights with tag "w" are updated with new notes.
