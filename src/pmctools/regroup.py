import gzip
import logging
import os
import random
from typing import List, Tuple

from joblib import Parallel, delayed


def get_names_and_sizes(corpus_dir: str = None, n_jobs=1) -> List[Tuple[str, int]]:
    """
    Retrieve file list and their sizes from the corpus directory

    :param corpus_dir: directory where files are stored
    :type corpus_dir: str

    :param n_jobs: number of parallel processes to use for the operation
    :type n_jobs: int

    :return: list of filenames and their sizes
    :rtype: List[Tuple[str, int]]
    """

    all_files = list()

    for root, dirs, files in os.walk(corpus_dir):
        for filename in files:
            all_files.append(os.path.join(root, filename))

    filenames_and_sizes = Parallel(n_jobs=n_jobs)(
        delayed(extract_size)(filename=filename) for filename in all_files
    )

    return filenames_and_sizes


def extract_size(filename: str = None) -> Tuple[str, int]:
    """
    Extract size of a text document in bytes

    :param filename: filepath
    :type filename: str

    :return: filename and size
    :rtype: Tuple[str, int]
    """

    with open(filename, "r", encoding="UTF-8") as input_file:
        size = len(input_file.read().encode("UTF-8"))

    return filename, size


def chunk_filenames_and_sizes(
    filenames_and_sizes: list = None, chunk_size: int = 524_288_000
) -> List:
    """
    Chunk the list of filenames

    :param filenames_and_sizes: list of filenames and sizes to chunk
    :type filenames_and_sizes: list

    :param chunk_size: chunk size in byte (default: 524_288_000)
    :type chunk_size: int

    :return: Iterator that yield chunks
    :rtype: list
    """
    current_chunk = list()
    current_size = 0

    for filename, size in filenames_and_sizes:
        current_chunk.append(filename)
        current_size += size

        if size >= chunk_size:
            yield current_chunk
            current_chunk = list()
            current_size = 0

    if len(current_chunk) > 0:
        yield current_chunk


def write_chunk_to_disk(filename_list: list = None, target_file: str = None):
    """
    Write a chunk to disk.

    :param filename_list: list of files included in the chunk
    :type filename_list: str

    :param target_file: destination file
    :type target_file: str

    :return: None
    """

    with gzip.open(target_file, "wt") as output_file:
        for filename in filename_list:
            with open(filename, "r", encoding="UTF-8") as input_file:
                output_file.write(input_file.read())


def split_corpus_in_chunk(
    corpus_dir: str = None,
    target_dir: str = None,
    chunk_size: int = 524_288_000,
    n_jobs: int = 1,
):
    """
    Regroup corpus in n chunks of predefined size (in bytes)

    :param corpus_dir: directory where corpus is stored
    :type corpus_dir: str

    :param target_dir: directory where chunks will be written
    :type target_dir: str

    :param chunk_size: chunk size in bytes (default: 524_288_000)
    :type chunk_size: int

    :param n_jobs: number of parallel processed to use for the opeation
    :type n_jobs: int

    :return: None
    """

    logging.info(
        "Gathering and shuffling file list using {} processes ...".format(n_jobs)
    )
    filenames_and_sizes = get_names_and_sizes(corpus_dir=corpus_dir, n_jobs=n_jobs)
    random.shuffle(filenames_and_sizes)

    logging.info("Number of files: {}".format(len(filenames_and_sizes)))

    logging.info(
        "Chunking and writing files to disk using {} processes ...".format(n_jobs)
    )
    Parallel(n_jobs=n_jobs)(
        delayed(write_chunk_to_disk)(
            filename_list=filename_list,
            target_file=os.path.join(target_dir, "{:03d}.json.gz".format(i)),
        )
        for i, filename_list in enumerate(
            chunk_filenames_and_sizes(
                filenames_and_sizes=filenames_and_sizes, chunk_size=chunk_size
            ),
            start=1,
        )
    )
