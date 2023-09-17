import requests
from bs4 import BeautifulSoup


def get_response(word):
    url = f"https://www.merriam-webster.com/dictionary/{word}"
    response = requests.get(url)
    content = response.content
    response.close()

    return content

def get_definition(content):
    soup = BeautifulSoup(content, "html.parser")
    div_entries = soup.find_all("div", class_="vg-sseq-entry-item")

    defs = []

    for entry in div_entries:
        # Find the span elements with class "dtText"
        dt_text = entry.find("span", class_="dtText")
        if dt_text:
            # Extract the text within the span
            usage_text = dt_text.get_text(strip=True)
            defs.append(usage_text)

    return defs

def get_examples(content):
    soup = BeautifulSoup(content, "html.parser")
    examples_div = soup.find_all("div", class_="in-sentences")

    if examples_div:
        examples = []
        for example in examples_div:
            examples.append(example.get_text(strip=True))


        return examples


def get_definition_and_examples(word):
    content = get_response(word)
    definition = get_definition(content)
    examples = get_examples(content)

    return definition, examples
