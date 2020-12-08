import argparse
import numpy as np
import random
import re
import requests

from pywikiapi import wikipedia


def build_ngrams(words, min_n=2, max_n=4):
    if min_n > max_n:
        raise ValueError("min_m must be less then max_n")

    res_ngrams = {}
    for n in range(min_n, max_n + 1):
        res_ngrams[n] = [" ".join(words[i : i + n]) for i in range(len(words) - n + 1)]

    return res_ngrams


def parse_articles(site, pageids, lang):
    seqs = []
    for page in site.query_pages(pageids=pageids, prop="cirrusdoc"):
        raw = page["cirrusdoc"][0]["source"]["text"]

        # deleting headers
        text = re.sub(r"\\n\\n[\=]+ [\w\s!:;,.~@#$%^&*()\_\-]+ [\=]+\\n", "", raw)

        # deleting punctuation
        text = re.sub(r"[\.,()!?\[\]:;\"\-«»\=]", "", text)

        # lowercase
        text = text.lower()

        # TODO: add additional text clearing:
        #       * remove links
        #       *(?) remove special symbols like << and >>
        #       * remove chars from not current language

        words_seq = text.split()
        seqs.append(words_seq)

    return seqs


def get_corpus(
    lang,
    min_n,
    max_n,
    max_size=-1,
    file_path=None,
    encoding="utf-8",
    random_choise=False,
):
    site = wikipedia(lang)

    corpus = []
    for r in site.query(list="allpages", apprefix=""):
        pageids = (page["pageid"] for page in r.allpages)
        seqs = parse_articles(site, pageids, lang)
        for seq in seqs:
            ngrams = build_ngrams(seq, min_n, max_n)
            for _, ngrams_list in ngrams.items():
                corpus += ngrams_list
                if max_size > 0 and len(corpus) >= max_size:
                    break

            else:
                continue
            break

        else:
            continue
        break

    if max_size > 0:
        if random_choise:
            corpus = np.random.choice(corpus, size=max_size, replace=False)
        else:
            corpus = corpus[:max_size]

    if file_path is not None:
        with open(file_path, "w", encoding=encoding) as target:
            for ngram in corpus:
                target.write(f"{len(ngram)}\t{ngram}\n")

    return corpus


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
        "-file",
        "--file_path",
        help="path to file which will contain desired corpus",
        type=str,
        default=None,
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
    get_corpus(
        args.lang,
        args.min_n,
        args.max_n,
        args.max_size,
        args.file_path,
        args.encoding,
        args.random_choise,
    )
