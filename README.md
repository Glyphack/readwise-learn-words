# readwise-language-learn

This project helps with learning words from the books you read by providing definitions and examples.
The translation is done using OpenAI.

The final result looks like this:

![image](https://private-user-images.githubusercontent.com/20788334/399083184-179e9b53-d359-4424-b7e5-65b74f994a17.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MzUzOTI4ODgsIm5iZiI6MTczNTM5MjU4OCwicGF0aCI6Ii8yMDc4ODMzNC8zOTkwODMxODQtMTc5ZTliNTMtZDM1OS00NDI0LWI3ZTUtNjViNzRmOTk0YTE3LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDEyMjglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQxMjI4VDEzMjk0OFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTkxZDlmZDMyM2Q4Mzk0NGUzNzgyMjUwNjNiM2MxYzc4MjIwZjRlMDFlZWYwZDkyM2M4ZTFjNWM3NjJlMTk4MDMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.pkaoMg5zAkJTRaF4vI5j1M7MJmNGwo76UThMbccWAto)

## How to setup

You need [Readwise API key](https://readwise.io/api_deets) and [OpenAI key](https://platform.openai.com/account/api-keys)
Follow the `secrets.py` to update the env var

You have to tag the highlights that contain a word you want to learn with "w" tag.

Run:

```
uv run src/main.py
```

Now all the highlights with tag "w" are updated with new notes.
