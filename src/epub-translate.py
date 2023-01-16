#!/usr/bin/env python3
import sys
import argparse
import re
import ebooklib
from ebooklib import epub
from lxml import etree

from translator import Translator

from tqdm import tqdm

METADATA = {   
    "DC": [
        "identifier",
        "title",
        "language",
        "creator",
        "contributor",
        "publisher",
        "rights",
        "coverage",
        "date",
        "description",
    ]
}


def parse_html(html, translator):
    if html.tag == 'head':
        return
    if html.text:
        html.text = translator.translate(html.text)
    for x in html.getchildren():
        tail = parse_html(x, translator)
        if tail:
            x.tail = translator.translate(tail)
    return html.tail

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", "-l", dest="lang", action="store", nargs=1,
                        default="it", type=str, help="Language to translate to")
    parser.add_argument("--output", "-o", dest="output", action="store", nargs=1,
                        type=str, help="Translated ebook filename")
    parser.add_argument("ebook", action="store", nargs=1, help="Ebook to translate")

    args = parser.parse_args(argv)

    ebook0 = epub.read_epub(args.ebook[0], {"ignore_ncx": True})
    ebook = epub.EpubBook()

    dest_languange = args.lang
    source_language = "auto"

    for ns, meta in METADATA.items():
        for name in meta:
            for data in ebook0.get_metadata(ns, name):
                if data == 'language':
                    source_language = data[0]
                    ebook.add_metadata(ns, name, dest_languange, data[1])
                else:
                    ebook.add_metadata(ns, name, data[0], data[1])

    translator = Translator(from_=source_language, to_=dest_languange)
    
    if args.output:
        ebook_filename = args.output
    else:
        match = re.match(r'(.*)(\.[a-zA-Z]+)$', args.ebook[0])
        ebook_filename = match.group(1) + '_' + args.lang + match.group(2)

    spine = ['nav']
    for item in tqdm(ebook0.items, desc="Items", leave=True):
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            html = etree.HTML(item.get_content())
            parse_html(html, translator)
            page = epub.EpubHtml(title=translator.translate(item.title), file_name=item.file_name)
            page.content = etree.tostring(html, method='html')
            ebook.add_item(page)
            spine.append(page)
        else:
            ebook.add_item(item)
        
    #    text = translator.translate(x.content, from_language=source_language, to_language=dest_languange)
    #    print(text)

    ebook.toc = [epub.Link(x.href, translator.translate(x.title), uid=x.uid) for x in ebook0.toc]
    ebook.add_item(epub.EpubNav())
    ebook.spine = spine
    epub.write_epub(ebook_filename, ebook)

if __name__ == "__main__":
    main(sys.argv[1:])
