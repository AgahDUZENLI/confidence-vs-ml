"""Load the Eedi Task 3/4 data into one clean table.
"""
import ast
from pathlib import Path

import pandas as pd
import numpy as np

# The data folder, found relative to this file so it works from anywhere
DATA = Path(__file__).resolve().parent.parent / "data"


def topic_at_level(ids, level, level_of):
    """Return the first topic in `ids` at the given level (some questions have two)."""
    for i in ids:
        if level_of[i] == level:
            return i
    return None


def load_data():
    """Return one row per answer, sorted by student and time."""
    # 1. Load the files
    answers = pd.read_csv(DATA / "train_data/train_task_3_4.csv")
    answer_meta = pd.read_csv(DATA / "metadata/answer_metadata_task_3_4.csv")
    students = pd.read_csv(DATA / "metadata/student_metadata_task_3_4.csv")
    questions = pd.read_csv(DATA / "metadata/question_metadata_task_3_4.csv")
    subjects = pd.read_csv(DATA / "metadata/subject_metadata.csv")

    # 2. SubjectId is text like "[3, 71, 98, 209]". Turn it into a real list.
    questions["SubjectId"] = questions["SubjectId"].apply(ast.literal_eval)

    # 3. Give every question one skill at level 2 and one at level 3
    level_of = dict(zip(subjects["SubjectId"], subjects["Level"]))
    questions["skill_L0"] = questions["SubjectId"].apply(lambda ids: topic_at_level(ids, 0, level_of))
    questions["skill_L1"] = questions["SubjectId"].apply(lambda ids: topic_at_level(ids, 1, level_of))
    questions["skill_L2"] = questions["SubjectId"].apply(lambda ids: topic_at_level(ids, 2, level_of))
    questions["skill_L3"] = questions["SubjectId"].apply(lambda ids: topic_at_level(ids, 3, level_of))

    # 4. Merge everything onto answers (one row per answer)
    df = pd.merge(answers, answer_meta, on="AnswerId", how="left", validate="one_to_one")
    df = pd.merge(df, students, on="UserId", how="left", validate="many_to_one")
    df = pd.merge(df, questions, on="QuestionId", how="left", validate="many_to_one")
    assert len(df) == len(answers), "Merge changed the number of rows!"

    # 5. Sort by student and time. Timestamps are per minute, so QuestionId breaks ties.
    df["DateAnswered"] = pd.to_datetime(df["DateAnswered"])
    df = df.sort_values(["UserId", "DateAnswered", "QuestionId"]).reset_index(drop=True)

    return df


def split_students(df, seed=42, train=0.70, val=0.15):
    """Add a "split" column: each student goes to train, val or test (70/15/15).

    All answers from one student stay in the same split, so the test set is
    made of new students. The fixed seed gives everyone the same split.
    """
    # 1. The list of studnets, in a fixed order
    users = np.sort(df["UserId"].unique())

    # 2. Shuffle them
    rng = np.random.default_rng(seed)
    users = rng.permutation(users)

    #  3. Cut into three pieces
    n = len(users)
    n_train = int(n * train)
    n_val = int(n * val)
    train_users = users[:n_train]
    val_users = users[n_train:n_train + n_val]
    test_users = users[n_train + n_val:]

    # 4. Label every answer by its student's group
    group_of = {}
    for u in train_users:
        group_of[u] = "train"
    for u in val_users:
        group_of[u] = "val"
    for u in test_users:
        group_of[u] = "test"

    df = df.copy()
    df["split"] = df["UserId"].map(group_of)
    return df


if __name__ == "__main__":
    df = load_data()
    print(df.shape)
    print(df.head())