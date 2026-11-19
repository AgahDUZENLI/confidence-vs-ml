# Student Confidence vs. ML Models

COSC 3337 Data Science I term project.

Can machine learning models predict whether a student's next math answer is correct better than the student's own confidence rating? We compare logistic regression and a small neural network against student confidence on the Eedi NeurIPS 2020 Education Challenge data (Tasks 3 and 4).

## Setup

You need Python 3.12 and git.

**1. Clone the repo**

```bash
git clone <repo-url>
cd confidence-vs-ml
```

**2. Make a virtual environment and install the packages**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` instead.

**3. Download the data**

```bash
python src/download_data.py
```

This downloads the official Eedi zip (about 660 MB), keeps only the 5 files we use, and deletes the zip. You end up with about 100 MB in `data/`:

```
data/
  train_data/train_task_3_4.csv
  metadata/answer_metadata_task_3_4.csv
  metadata/question_metadata_task_3_4.csv
  metadata/student_metadata_task_3_4.csv
  metadata/subject_metadata.csv
```

If the files are already there, the script does nothing.

*
## Data license

The Eedi data is licensed CC BY-NC-ND 4.0. **Do not commit or share the data files.** `data/` is in `.gitignore`, so everyone downloads their own copy with the script above.

Source: https://www.eedischool.com/projects/neurips-education-challenge

## Repo layout

```
src/        shared Python code (data download, loading)
notebooks/  Jupyter notebooks with results
results/    saved figures and tables
data/       Eedi data (not in git)
```
