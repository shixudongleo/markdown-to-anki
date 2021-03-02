#!/usr/bin/env python3

import csv
import markdown
from bs4 import BeautifulSoup

md = markdown.Markdown(
    extensions=[
        'pymdownx.arithmatex',
        'fenced_code',
        'tables'
    ],
    extension_configs={
        "pymdownx.arithmatex": {
        "generic": True
      }
})

def markdown_to_html(md_text):
    """convert markdown to html

    Args:
        md_text (str): the text content of markdown file

    Returns:
        str: render markdown text as html
    """

    md.reset()
    html = md.convert(md_text)
    import ipdb; ipdb.set_trace()

    return html


def markdown_file_to_html(md_filename):
    """convert markdown file given by path to html

    Args:
        md_filename (str): the markdown filename
    Returns:
        str: render markdown text as html
    """

    with open(md_filename, 'r') as md_file:
        html = markdown_to_html(md_file.read())

    return html

def convert_h2_as_cards(html):
    """import cards, h2 header as Question, content between h2 header as Answer.

    Args:
        html (str): the markdown content as html

    Returns:
        list: list of question and answer pairs
    """
    soup = BeautifulSoup(html, 'html.parser')

    cards = []

    size_contents = len(soup.contents)
    idx = 0
    while idx < size_contents:
        tag = soup.contents[idx]

        if tag.name == 'h2':
            question = tag.text
            ans = []
            while True:
                if idx + 1 >= size_contents:
                    break

                if soup.contents[idx + 1].name == 'h2':
                    idx += 1
                    break

                idx += 1
                ans.append(str(soup.contents[idx]).strip())

            card = (question, ans)
            cards.append(card)
        else:
            idx += 1

    cards = [(e[0], ''.join(e[1])) for e in cards]
    # TODO: the format is not correct, especially the newline
    # import ipdb; ipdb.set_trace()
    return cards

def export_cards_as_csv(outfile, cards):
    with open(outfile, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for card in cards:
            csv_writer.writerow(card)


if __name__ == '__main__':

    html = markdown_file_to_html('chapter2-python-data-structure-performance.md')
    cards = convert_h2_as_cards(html)
    export_cards_as_csv('chapter2-python-ds.txt', cards)
