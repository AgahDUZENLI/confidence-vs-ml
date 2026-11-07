"""Download the Eedi NeurIPS 2020 Education Challenge data into data/.

Keeps only the Task 3 and 4 files this project uses (about 105 MB).
Data license: CC BY-NC-ND 4.0. Do not commit or share the data.
Source: https://www.eedischool.com/projects/neurips-education-challenge

Run from the repo folder:  python src/download_data.py
"""
import urllib.request
import zipfile
from pathlib import Path

URL = "https://dqanonymousdata.blob.core.windows.net/neurips-public/data.zip"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ZIP_PATH = ROOT / "data.zip"

FILES = [
    "train_data/train_task_3_4.csv",
    "metadata/answer_metadata_task_3_4.csv",
    "metadata/question_metadata_task_3_4.csv",
    "metadata/student_metadata_task_3_4.csv",
    "metadata/subject_metadata.csv",
]


def main():
    if all((DATA_DIR / f).exists() for f in FILES):
        print(f"Data already in {DATA_DIR}")
        return

    if not ZIP_PATH.exists():
        print("Downloading Eedi data ...")
        urllib.request.urlretrieve(URL, ZIP_PATH)

    print("Unzipping the files we need...")
    with zipfile.ZipFile(ZIP_PATH) as z:
        for f in FILES:
            target = DATA_DIR / f
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(f"data/{f}"))
            print("  ", f)

    ZIP_PATH.unlink()
    print(f"Done. Files are in {DATA_DIR}")


if __name__ == "__main__":
    main()
