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

from bs4 import BeautifulSoup
from pywikiapi import wikipedia


class Corpus:
    def __init__(self, lang, max_size=-1, random_choise=False):
        self.size = 0
        self.lang = lang
        self.generator = iter([])
        self.max_size = max_size
        self.random_choise = random_choise
        self.site = wikipedia(self.lang)

    def __len__(self):
        return self.size

    def __iterate_wikipages_by_id__(self, pageids):
        paragaraphs = []
        for pageid in pageids:
            gen = self.site.query(
                pageids=pageid, prop=["extracts"], exlimit=1
            )  # could use explaintext instead bs4 html parser
            try:
                info = next(gen)
                page = info["pages"][0]
                html_text = page["extract"].replace("\xa0", " ").replace("\n", "")
                soup = BeautifulSoup(html_text, "html.parser")
                for data in soup.find_all("p"):
                    paragaraphs.append(data.get_text())

            except:
                continue
        if self.random_choise:
            paragaraphs = np.random.permutation(paragaraphs)

        return paragaraphs

    def collect_data(self, n_proc=os.cpu_count() - 1):
        corpus_gens = []
        pages_gen = self.site.query(list="allpages", apprefix="")
        pool = mp.Pool(n_proc)
        while True:
            batch = []
            while len(batch) < 2 * n_proc:
                try:
                    pages = next(pages_gen)
                    pageids = [page.pageid for page in pages.allpages]
                    batch.append(pageids)
                except StopIteration:
                    break

            res = pool.starmap(
                Corpus.__iterate_wikipages_by_id__, zip(itertools.repeat(self), batch)
            )
            for paragaraph in res:
                self.size += len(paragaraph)
                corpus_gens.append(iter(paragaraph))

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

    def save_tsv(self, file_path=None, encoding="utf-8", write_len=True):
        if file_path is None:
            timestamp_name = f"{int(time.time())}.tsv"
            file_path = os.path.join(os.curdir, timestamp_name)
        with open(file_path, "w", encoding=encoding) as target:
            for paragaraph in self.generator:
                res_string = ""
                if write_len:
                    res_string += f"{len(paragaraph)}\t"
                res_string += paragaraph
                res_string += "\n"
                target.write(res_string)
