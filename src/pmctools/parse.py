from typing import List

import pubmed_parser as pp


def extract_content_from_file(filepath: str = None) -> List[str]:
    """
    Return the textual content of a PMC OpenAccess Article

    :param filepath: nxml filepath
    :type filepath: str

    :return: list of text chunks
    :rtype: List[str]
    """

    all_parts = list()

    try:
        metadata = pp.parse_pubmed_xml(filepath)

        if metadata.get("full_title") is not None:
            all_parts.append(metadata.get("full_title").strip("\n "))

        if metadata.get("abstract") is not None:
            all_parts.append(metadata.get("abstract").strip("\n "))
    except TypeError:
        pass

    try:
        paragraphs = pp.parse_pubmed_paragraph(filepath)

        for par in paragraphs:
            if par.get("text") is not None:
                all_parts.append(par.get("text").strip("\n "))
    except TypeError:
        pass

    return all_parts
