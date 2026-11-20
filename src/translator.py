import os
import subprocess
from abc import ABC, abstractmethod
import llm

PROMPT_TEMPLATE = """I am a native Persian speaker trying to learn English.

Your task is to only help with translation and definition lookup of the asked words. Nothing else.

Translate the English word or phrase "{phrase}" to Persian.
If there are multiple meanings provide all of them and the context each one is used.

The output must only be:
The pronunciation of the english word or phrase in english. For example for library write: lahy-brer-ee.
The phonetic. For example for library write: /ˈlaɪ.brər.i/
the meaning in persian.
The meaning in english. Explain it for uncommon or old words and phrases.
Example sentence showing how the word is used.

For example when the word is "Bellicose":

bel-i-kohs
/ˈbɛl.ɪ.koʊs/
ستیزه‌جو
"Bellicose" is an adjective used to describe someone who is eager to fight or prone to aggression and hostility.
Bellicose hockey players who seem to spend more time fighting than playing
"""


class MeaningLookup(ABC):
    def _build_prompt(self, word):
        return PROMPT_TEMPLATE.format(phrase=word)

    @abstractmethod
    def translate(self, word): ...


class OpenAITranslator(MeaningLookup):
    model = "gpt-4o-mini"

    def __init__(self):
        self.OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

    def translate(self, word):

        model = llm.get_model(self.model)
        model.key = self.OPENAI_API_KEY
        response = model.prompt(self._build_prompt(word))
        return response.text()


class ClaudeCliTranslator(MeaningLookup):
    model = "sonnet"

    def translate(self, word):
        result = subprocess.run(
            ["claude", "-p", "--model", self.model],
            input=self._build_prompt(word),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"claude command failed: {result.stderr.strip()}")
        return result.stdout.strip()
