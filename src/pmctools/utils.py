from typing import Iterator


def chunk_list(input_list: list = None, nb_chunks: int = None) -> Iterator[list]:
    """
    Chunk a list in n parts of equivalent sizes (+- 1).

    :param input_list: list to chunk
    :type input_list: list

    :param nb_chunks: number of chunks
    :type nb_chunks: int

    :return: Iterator of list objects
    :rtype: Iterator[list]
    """

    main_chunk_size = len(input_list) // nb_chunks
    rest = len(input_list) % nb_chunks

    start = 0
    for i in range(nb_chunks):
        end = start + main_chunk_size

        if rest > 0:
            end += 1
            rest -= 1

        yield input_list[start:end]

        start += end - start
