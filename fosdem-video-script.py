#!/bin/python3

import argparse
import json
from lxml import html
import os
import requests

extensions_list = ["avi", "ogg", "ogv", "mp4", "webm"]
verbose = False


class media():
    def __init__(self, name, url, year, format):
        self.name = name
        self.url = url
        self.year = year
        self.format = format

    def to_data(self):
        return (self.name, {"name": self.name, "url": self.url, "year":
                self.year, "format": self.format})


def objs_to_json(objs, path):
    with open(path, 'w', encoding="utf-8") as fd:
        objs_list = {}

        for obj in objs:
            name, data = obj.to_data()
            objs_list[name] = data

        json.dump(objs_list, fd, sort_keys=True, ensure_ascii=False, indent=4)

    if verbose:
        print("finished writing objects to file:", path)


def format_urls(base_url, raw_urls):
    objs = []
    # Remove "https://video.fosdem.org/"
    prefix = len(base_url)

    for url in raw_urls:
        # Splitting into ['2015', 'jansson', '<filename>.<filetype>']
        url_split = url[prefix:].split('/')
        split_len = len(url_split)

        # Splitting ['<filename>', 'filetype']
        format = url_split[-1].split('.')[-1]

        if split_len:
            objs.append(media(url_split[-1], url, url_split[0], format))
        else:
            print("Unexpected:", url)

    return objs


def walk_nodes(url, leafs):

    nodes = map_nodes(url)

    if nodes:
        for node in nodes:
            walk_nodes(url + node, leafs)
    else:
        dir_leafs = map_leafs(url)
        for leaf in dir_leafs:
            leafs.append(url + leaf)


def map_nodes(url):
    nodes = []

    if verbose:
        print("getting node:", url)
    page = requests.get(url)
    tree = html.fromstring(str(page.content, 'utf-8'))

    links = tree.cssselect('a')

    for link in links:
        if link.attrib['href'] == link.text and link.text[-1:] == '/' and \
                link.text != "Parent directory/":
            nodes.append(link.text)

    return nodes


def map_leafs(url):
    leafs = []

    if verbose:
        print("getting leafs:", url)
    page = requests.get(url)
    tree = html.fromstring(str(page.content, 'utf-8'))

    links = tree.cssselect('a')

    for link in links:
        if link.attrib['href'] == link.text and '.' in link.text and \
                any(ext in link.text for ext in extensions_list):
            leafs.append(link.text)

    return leafs


def scrape(url):
    res = []

    walk_nodes(url, res)

    return res


def handle_fetch(json_filename, base_url, years, quiet=False):
    raw_urls = []

    if years:
        for year in years:
            url = base_url + year + '/'
            if not quiet:
                print("scraping", url, "...")
            raw_urls += scrape(url)
    else:
        if not quiet:
            print("scraping", base_url, "...")
        raw_urls += scrape(base_url)

    if verbose:
        print("formatting results...")

    formated_urls = format_urls(base_url, raw_urls)

    if not quiet:
        print("writing data to", json_filename, "...")

    objs_to_json(formated_urls, json_filename)

    if not quiet:
        print("done")


def load_objects_from_data(json_filename):
    if not os.path.exists(json_filename):
        print("Missing json file, please run `fosdem-video-script.py fetch`")
        return None

    data = []
    objects = []

    with open(json_filename, 'r', encoding="utf-8") as fd:
        data = json.load(fd)

    for entry in data:
        entry_data = data[entry]
        obj = media(entry_data["name"], entry_data["url"], entry_data["year"],
                    entry_data["format"])
        objects.append(obj)

    return objects


def handle_search(json_filename, tokens):
    objects = load_objects_from_data(json_filename)

    if objects is None:
        return

    for obj in objects:
        if all(token in obj.url for token in tokens):
            print(obj.url)


def main():
    json_filename = "./fosdem-video-data.json"
    # _NOTE_ the URL have to end with '/'
    base_url = "https://video.fosdem.org/"

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--quiet", action="store_true")

    subparsers = parser.add_subparsers(help="")

    fetch_parser = subparsers.add_parser("fetch")
    fetch_parser.set_defaults(which="fetch")
    fetch_parser.add_argument("fetch", action="store_true", help="building a \
            JSON file from the collected video data")
    fetch_parser.add_argument("--years", nargs="*", help="specifying what \
            years that will be fetched")

    search_parser = subparsers.add_parser("search")
    search_parser.set_defaults(which="search")
    search_parser.add_argument("search", nargs="*", help="search the \
            collected video data")

    args = parser.parse_args()

    if args.verbose:
        global verbose
        verbose = True
        print(args)

    if args.which is "fetch":
        handle_fetch(json_filename, base_url, args.years, args.quiet)

    if args.which is "search":
        handle_search(json_filename, args.search)


if __name__ == "__main__":
    main()
