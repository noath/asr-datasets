import argparse
import logging
import os

from corpus import Corpus


def run():
    parser = argparse.ArgumentParser(description="Corpus collecting tool")
    parser.add_argument(
        "lang", help="language for which wikipedia will be parsed", type=str
    )
    parser.add_argument(
        "-size",
        "--max_size",
        help="limit for corpus paragraphs count",
        type=int,
        default=-1,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="shows how often print progress message",
        type=int,
        default=10,
    )
    parser.add_argument(
        "-min_len",
        "--min_paragraph_len",
        help="lower bound for paragraphs length",
        type=int,
        default=None,
    )
    parser.add_argument(
        "-max_len",
        "--max_paragraph_len",
        help="upper bound for paragraphs length",
        type=int,
        default=None,
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
        "-wl",
        "--write_len",
        help="flag for write ID\tLEN\tPAR instead of ID\tPAR in .tsv file.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-rand",
        "--random_choise",
        help="flag for random choice of max_size paragraphs from collected corpus (ignored if max_sized doesn`t specified)",
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

    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        filename="collect_corpus.log",
        level=logging.INFO,
    )
    corpus = Corpus(
        args.lang,
        args.max_size,
        args.random_choise,
        args.min_paragraph_len,
        args.max_paragraph_len,
        args.verbose,
    )
    corpus.collect_data(args.num_of_processes)
    if args.save:
        corpus.save_tsv(args.file_path, args.encoding, args.write_len)


if __name__ == "__main__":
    run()
