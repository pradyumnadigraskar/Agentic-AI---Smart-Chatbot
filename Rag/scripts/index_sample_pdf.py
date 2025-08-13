import os
from app.processor import index_pdf
from app.config import PDFS_DIR

if __name__ == "__main__":
    os.makedirs(PDFS_DIR, exist_ok=True)
    sample = os.path.join(PDFS_DIR, "sample.pdf")
    if not os.path.exists(sample):
        print("Place sample.pdf into the pdfs/ directory")
    else:
        n = index_pdf(sample)
        print(f"Indexed {n} chunks.")
