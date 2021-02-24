import argparse
import os

from corpus import Corpus


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corpus collecting tool")
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
    parser.add_argument(
        "-n_proc",
        "--num_of_processes",
        help="number of processing will be using for multiprocessing",
        type=int,
        default=os.cpu_count() - 1,
    )

    args = parser.parse_args()
    corpus = Corpus(
        args.lang, args.min_n, args.min_n, args.max_size, args.random_choise
    )
    corpus.collect_data(args.num_of_processes)
    if args.save:
        corpus.save_tsv(
            args.file_path, args.encoding, args.write_n, args.ngram_as_string
        )
