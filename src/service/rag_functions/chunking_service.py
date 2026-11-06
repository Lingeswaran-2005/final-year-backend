import re


def split_sentences(text: str) -> list[str]:
    """
    Split text into approximate sentences while preserving
    sentence-ending punctuation.
    """
    sentences = re.split(
        r"(?<=[.!?])\s+|\n{2,}",
        text.strip(),
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def create_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[str]:

    if not text or not text.strip():
        return []

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size."
        )

    sentences = split_sentences(text)

    chunks: list[str] = []
    current_sentences: list[str] = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        # Handle a single sentence larger than chunk_size.
        if sentence_length > chunk_size:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_length = 0

            chunks.append(sentence)
            continue

        additional_length = (
            sentence_length
            if not current_sentences
            else sentence_length + 1
        )

        if (
            current_sentences
            and current_length + additional_length > chunk_size
        ):
            chunks.append(" ".join(current_sentences))

            # Keep complete sentences for overlap.
            overlap_sentences: list[str] = []
            overlap_length = 0

            for previous_sentence in reversed(current_sentences):
                extra_length = (
                    len(previous_sentence)
                    if not overlap_sentences
                    else len(previous_sentence) + 1
                )

                if overlap_length + extra_length > overlap:
                    break

                overlap_sentences.insert(0, previous_sentence)
                overlap_length += extra_length

            current_sentences = overlap_sentences
            current_length = overlap_length

        current_sentences.append(sentence)
        current_length += (
            sentence_length
            if len(current_sentences) == 1
            else sentence_length + 1
        )

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks