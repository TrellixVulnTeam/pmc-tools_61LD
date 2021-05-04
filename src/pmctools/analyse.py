from spacy.language import Language


def analyse_text_chunks(text_chunks: list = None, nlp: Language = None):

    all_parts = list()
    skipped_chunks = list()

    for chunk in text_chunks:
        chunk_sentences = list()

        if len(chunk) >= 1_000_000:
            skipped_chunks.append(chunk)
            continue

        doc = nlp(chunk)

        for sent in doc.sents:
            chunk_sentences.append(str(sent))

        all_parts.append(chunk_sentences)

    return all_parts, skipped_chunks
