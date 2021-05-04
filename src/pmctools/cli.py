import logging
import os
import re
import shutil
import sys
import tarfile

import click

from pmctools.data import process_corpus


@click.group()
@click.option("--debug", is_flag=True)
def cli(debug):
    log = logging.getLogger("")
    log.handlers = []
    log_format = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)

    # Adding a stdout handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(log_format)
    log.addHandler(ch)


@cli.command("UNCOMPRESS")
@click.option(
    "--input-dir", help="PMC corpus directory (.tar.gz format)", required=True, type=str
)
@click.option(
    "--output-dir",
    help="Directory where files will be uncompressed",
    required=True,
    type=str,
)
def uncompress_cli(input_dir: str, output_dir: str):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    if not os.path.isdir(input_dir):
        raise NotADirectoryError("The input directory does not exist")

    if os.path.isdir(output_dir):
        click.confirm(
            "The output directory already exists. Do you want to overwrite?",
            abort=True,
        )
        click.echo("Overwriting output directory: {}".format(output_dir))
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if not re.match(r"^.*\.xml.tar.gz$", filename):
            continue

        logging.info("Uncompressing {}".format(filename))

        tar_filepath = os.path.join(input_dir, filename)

        with tarfile.open(tar_filepath) as input_file:
            input_file.extractall(path=output_dir)


@cli.command("LM")
@click.option("--input-dir", help="PMC corpus directory", required=True, type=str)
@click.option(
    "--output-dir",
    help="Directory where TXT files will be created",
    required=True,
    type=str,
)
@click.option(
    "--spacy-model",
    help="spaCy model that will be used for conversion",
    required=False,
    type=str,
    default="en_core_sci_lg",
    show_default=True,
)
@click.option(
    "--n-jobs",
    help="Number of parallel processes that must be used",
    required=False,
    type=int,
    default=1,
    show_default=True,
)
def lm_cli(input_dir: str, output_dir: str, spacy_model: str, n_jobs: int):
    """Prepare the PMC dataset for language modelling"""

    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    if not os.path.isdir(input_dir):
        raise NotADirectoryError("The input directory does not exist")

    if os.path.isdir(output_dir):
        click.confirm(
            "The output directory already exists. Do you want to overwrite?",
            abort=True,
        )
        click.echo("Overwriting output directory: {}".format(output_dir))
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    process_corpus(
        input_dir=input_dir,
        output_dir=output_dir,
        spacy_model=spacy_model,
        n_jobs=n_jobs,
    )
