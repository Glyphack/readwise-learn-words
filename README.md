# readwise-language-learn

This projects helps with adding english definition to the words you highlighted with readwise.

The definitions are coming from merriam-webster.

The final result looks like this:

![image](https://user-images.githubusercontent.com/20788334/268514491-d7263b31-cc0d-47e2-93ac-428097dcb574.png)

## How to setup

Get your readwise API key and follow the `secrets.py` to update the env var.

You have to tag the highlights that contain a word you want to learn with "word" tag.

Run the script, and the highlihgts will now have a note with definitions and examples of the word. The tag will also be updated to "words-defined".
If the program fails to find definitions for the word, it won't do anything.

