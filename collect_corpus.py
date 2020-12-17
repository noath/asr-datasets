import argparse
import itertools
import nltk
import numpy as np
import os
import random
import re
import requests
import time

from pywikiapi import wikipedia


def parse_articles(site, pageids, lang):
    seqs = []
    for page in site.query_pages(pageids=pageids, prop="cirrusdoc"):
        raw = page["cirrusdoc"][0]["source"]["text"]

        # deleting headers
        text = re.sub(r"\\n\\n[\=]+ [\w\s!:;,.~@#$%^&*()\_\-]+ [\=]+\\n", "", raw)

        # deleting punctuation
        text = re.sub(r"[\.,()!?\[\]:;\"\–\-«»\=]", "", text)

        # lowercase
        text = text.lower()

        # TODO: add additional text clearing:
        #       * remove links
        #       *(?) remove special symbols like << and >>
        #       * remove chars from not current language

        words_seq = text.split()
        seqs.append(words_seq)

    return seqs


class Corpus:
    def __init__(self, lang):
        self.size = 0
        self.lang = lang
        self.generator = iter([])

    def __len__(self):
        return self.size

    def collect_data(self, min_n, max_n, max_size=-1, random_choise=False):
        site = wikipedia(self.lang)
        corpus_gens = []
        for r in site.query(list="allpages", apprefix=""):
            if max_size > 0 and self.size >= max_size:
                break

            pageids = (page["pageid"] for page in r.allpages)
            seqs = parse_articles(site, pageids, self.lang)
            if random_choise:
                seqs = np.random.permutation(seqs)

            ngram_gens = []
            for seq in seqs:
                if max_size > 0 and self.size >= max_size:
                    break

                self.size += len(tuple(nltk.everygrams(seq, min_n, max_n))) # not huge tuple here, so no problems with allocations
                ngram_gens.append(nltk.everygrams(seq, min_n, max_n))

            corpus_gens.append(itertools.chain(*ngram_gens))
        self.generator = itertools.chain(*corpus_gens)

        if max_size > 0:
            self.generator = itertools.islice(self.generator, max_size)
            self.size = max_size

    def reset_data(self):
        self.generator = iter([])
        self.size = 0

    def get_data(self):
        return self.generator

    def save_tsv(self, file_path=None, encoding="utf-8", write_n=True, ngram_as_string=False):
        if file_path is None:
            timestamp_name = f"{int(time.time())}.tsv"
            file_path = os.path.join(os.curdir, timestamp_name)
        with open(file_path, "w", encoding=encoding) as target:
            for ngram in self.generator:
                res_string = ""
                if write_n:
                    res_string += f"{len(ngram)}\t"
                ngram_string = f"{ngram}\n" if not ngram_as_string else f"{' '.join(ngram)}\n"
                res_string += ngram_string
                target.write(res_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Corpus collecting tool')
    parser.add_argument(
        "lang", help="language for which wikipedia will be parsed", type=str
    )
    parser.add_argument(
        "min_n", help="min n (including) for collecting n-grams", type=int
    )
    parser.add_argument(
        "max_n", help="max n (including) for collecting n-grams", type=int
    )
    parser.add_argument(
        "-size",
        "--max_size",
        help="limit for corpus n-grams count",
        type=int,
        default=-1,
    )
    parser.add_argument(
        "-fp",
        "--file_path",
        help="path to file which will contain desired corpus",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-s",
        "--save",
        help="flag for saving .tsv file (you can specify file using --file_path, encoding by --encoding, and whether write n with --write_n)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-wn",
        "--write_n",
        help="flag for write N\tNGRAM instead of NGRAM in .tsv file.",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "-str",
        "--ngram_as_string",
        help="flag for write ngram as string instead of tuple of strings in .tsv file.",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "-rand",
        "--random_choise",
        help="flag for random choice of max_size n-grams from collected corpus (ignored if max_sized doesn`t specified",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-enc",
        "--encoding",
        help="encoding (open-like str for python3) for output file (ignored if file_path doesn`t specified)",
        type=str,
        default="utf-8",
    )

    args = parser.parse_args()
    corpus = Corpus(args.lang)
    corpus.collect_data(args.min_n, args.max_n, args.max_size, args.random_choise)
    if args.save:
        corpus.save_tsv(args.file_path, args.encoding, args.write_n, args.ngram_as_string)
