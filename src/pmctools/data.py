import logging
import os
import re

from joblib import Parallel, delayed

import spacy
from pmctools.analyse import analyse_text_chunks
from pmctools.parse import extract_content_from_file
from pmctools.utils import chunk_list


def process_corpus(
    input_dir: str = None,
    output_dir: str = None,
    spacy_model: str = None,
    n_jobs: int = None,
):

    logging.info("Gathering file list ...")
    to_be_processed = list()

    for root, dirs, files in os.walk(input_dir):
        for filename in files:

            if not re.match(r"^.*\.nxml$", filename):
                continue

            source_file = os.path.join(root, filename)

            relative_path = os.path.relpath(root, input_dir)
            basename, extension = os.path.splitext(filename)

            target_path = os.path.join(output_dir, relative_path)
            target_file = os.path.join(target_path, "{}.txt".format(basename))

            if not os.path.isdir(target_path):
                os.makedirs(target_path)

            to_be_processed.append((source_file, target_file))

    logging.info("Number of files: {}".format(len(to_be_processed)))

    skipped = Parallel(n_jobs=n_jobs)(
        delayed(process_file_batch)(file_batch=file_batch, spacy_model=spacy_model)
        for file_batch in chunk_list(input_list=to_be_processed, nb_chunks=n_jobs)
    )

    skipped_file = os.path.join(output_dir, "skipped.txt")
    with open(skipped_file, "w", encoding="UTF-8") as output_file:
        for group in skipped:
            for chunk in group:
                output_file.write("{}\n\n".format(chunk))


def process_file_batch(file_batch: list = None, spacy_model: str = None):

    nlp = spacy.load(spacy_model, exclude=["ner"])

    all_skipped_chunks = list()

    for source_file, target_file in file_batch:
        file_chunks = extract_content_from_file(filepath=source_file)
        file_chunks, skipped_chunks = analyse_text_chunks(
            text_chunks=file_chunks, nlp=nlp
        )

        if len(file_chunks) > 0:
            write_to_file(file_chunks=file_chunks, target_file=target_file)

        if len(skipped_chunks) > 0:
            all_skipped_chunks.extend(skipped_chunks)

    return all_skipped_chunks


def write_to_file(file_chunks: list = None, target_file: str = None):

    with open(target_file, "w", encoding="UTF-8") as output_file:
        for i, chunk in enumerate(file_chunks, start=1):
            for sentence in chunk:
                output_file.write("{}\n".format(sentence))

            if i < len(file_chunks):
                output_file.write("\n")
