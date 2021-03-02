# markdown-to-anki

I favor markdown for note taking. However, the spaced repetition is done with anki. markdown-to-anki aims to convert markdown note to plain text format to import into anki desktop version.

## Markdown to HTML

Anki cards support content as HTML, so we can simply render markdown as HTML and import into Anki.
The tools used are:

- `python-markdown` library
- `pymdown-extensions` library's `arithmatex` module. This allow us to use `$, $$` separator for mathjax formula. (it is translated to `\(\), \[\]`)
- `fenced_code` extension. This allow us to convert code block.
- `tables` extension. This allow us to convert table.

[other extensions](https://python-markdown.github.io/extensions/)

```python
md = markdown.Markdown(
    extensions=[
      'pymdownx.arithmatex',
      'fenced_code`,
      'tables'
    ],
    extension_configs={
        "pymdownx.arithmatex": {
        "generic": True
      }
    })
```

## Divide markdown content into cards

In order to parse markdown sections, there are two methods:

- parse markdown AST(abstrace syntax tree) directly
- parse markdown rendered HTML AST
- here we use the second method, as parsing HTML structure is a common task and easily done with `beautifulsoup` library.
