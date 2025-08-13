from app.pdf_utils import split_text_to_chunks
def test_split_chunks():
    text = " ".join(str(i) for i in range(1000))
    chunks = split_text_to_chunks(text, chunk_words=100, overlap_words=20)
    assert len(chunks) > 1
