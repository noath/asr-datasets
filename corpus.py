import itertools
import multiprocessing as mp
import nltk
import logging
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
        text = re.sub(r"[.,\(\)!?\[\]:;\"—\-«»\=\\\+]", "", text)

        # deleting numbers
        text = re.sub(r"[0-9]", "", text)

        # lowercase
        text = text.lower()

        # TODO: add additional text clearing:
        #       * remove links
        #       * remove chars from not current language
        #       ** not remove words with majority letters from current language

        words_seq = text.split()
        seqs.append(words_seq)

    return seqs


class Corpus:
    def __init__(self, lang, min_n, max_n, max_size=-1, random_choise=False):
        self.size = 0
        self.lang = lang
        self.generator = iter([])
        self.min_n = min_n
        self.max_n = max_n
        self.max_size = max_size
        self.random_choise = random_choise
        self.site = wikipedia(self.lang)

    def __len__(self):
        return self.size

    def __iterate_wikipages__(self, resp):
        pageids = (page["pageid"] for page in resp.allpages)
        seqs = parse_articles(self.site, pageids, self.lang)
        if self.random_choise:
            seqs = np.random.permutation(seqs)

        ngram_gens = []
        size = 0
        for seq in seqs:
            ngram_gens += list(nltk.everygrams(seq, self.min_n, self.max_n))

        return ngram_gens

    def collect_data(self, n_proc=os.cpu_count()):
        corpus_gens = []
        pages_gen = self.site.query(list="allpages", apprefix="")
        pool = mp.Pool(n_proc)
        while True:
            batch = []
            while len(batch) < 2 * n_proc:
                try:
                    page = next(pages_gen)
                    batch.append(page)
                except StopIteration:
                    break

            res = pool.starmap(
                Corpus.__iterate_wikipages__, zip(itertools.repeat(self), batch)
            )
            for ngrams in res:
                self.size += len(ngrams)
                corpus_gens.append(iter(ngrams))

            if self.size >= self.max_size:
                break

        self.generator = itertools.chain(*corpus_gens)

        if self.max_size > 0:
            self.generator = itertools.islice(self.generator, self.max_size)
            self.size = self.max_size

    def reset_data(self):
        self.generator = iter([])
        self.size = 0

    def get_data(self):
        return self.generator

    def save_tsv(
        self, file_path=None, encoding="utf-8", write_n=True, ngram_as_string=False
    ):
        if file_path is None:
            timestamp_name = f"{int(time.time())}.tsv"
            file_path = os.path.join(os.curdir, timestamp_name)
        with open(file_path, "w", encoding=encoding) as target:
            for ngram in self.generator:
                res_string = ""
                if write_n:
                    res_string += f"{len(ngram)}\t"
                ngram_string = (
                    f"{ngram}\n" if not ngram_as_string else f"{' '.join(ngram)}\n"
                )
                res_string += ngram_string
                target.write(res_string)
