import requests
from bs4 import BeautifulSoup

def get_meaning(word):
    """Scrapes the meaning of a word from the Wikipedia page for the word.

    Args:
    word: The word to scrape the meaning for.

    Returns:
    A string containing the meaning of the word, or None if the meaning could
    not be found.
    """

    url = f"https://en.wiktionary.org/wiki/{word}"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    h2_with_span_id_english = soup.find("h2", has_child="span", id_="English")

    print(h2_with_span_id_english)

    h3_tags = h2_with_span_id_english.find_next_siblings("h3")

    meanings = []
    for h3_tag in h3_tags:
        meaning = h3_tag.get_text().strip()
        meanings.append(meaning)
# Example usage:
word = "bikeshed"
meaning = get_meaning(word)

print(meaning)


get_meaning("bikeshed")
