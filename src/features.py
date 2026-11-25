import pandas as pd


def add_history(df, group_cols, suffix=""):
    """For each answer, count the student's answers from EARLIER minutes.

    group_cols=["UserId"]               -> history over all questions
    group_cols=["UserId", "skill_L2"]   -> history on this question's skill only
    """
    # Step A: one row per student-minute
    per_minute = (
        df.groupby(group_cols + ["DateAnswered"])["IsCorrect"]
          .agg(n="count", correct="sum")
          .reset_index()
    )

    # Step B: running totals, minus this minute = totals from BEFORE this minute
    g = per_minute.groupby(group_cols)
    per_minute["n_prev" + suffix] = g["n"].cumsum() - per_minute["n"]
    per_minute["correct_prev" + suffix] = g["correct"].cumsum() - per_minute["correct"]
    per_minute = per_minute.drop(columns=["n", "correct"])

    # Step C: put the numbers back on every answer
    df = df.merge(per_minute, on=group_cols + ["DateAnswered"], how="left", validate="many_to_one")

    # Step D: smoothed accuracy (0.5 when there's no history yet)
    df["acc_prev" + suffix] = (df["correct_prev" + suffix] + 1) / (df["n_prev" + suffix] + 2)
    return df

def add_question_rate(df):
    """Share of TRAINING answers that got this question right.

    Training rows leave out their own answer (leave-one-out), so a row's
    feature never contains its own label. Val/test rows use the plain
    training rate, because their answers were never part of it.
    """
    # Count answers and correct answers per question, training students only
    train = df[df["split"] == "train"]
    stats = (
        train.groupby("QuestionId")["IsCorrect"]
             .agg(q_n="count", q_correct="sum")
             .reset_index()
    )
    df = df.merge(stats, on="QuestionId", how="left", validate="many_to_one")

    # Leave-one-out: training rows remove their own answer
    is_train = df["split"] == "train"
    n = df["q_n"] - is_train.astype(int)
    correct = df["q_correct"] - df["IsCorrect"].where(is_train, 0)

    # Smoothed, like acc_prev
    df["q_correct_rate"] = (correct + 1) / (n + 2)
    return df.drop(columns=["q_n", "q_correct"])


def build_features(df):
    """All features in one call. df must already have the 'split' column."""
    df = add_history(df, ["UserId"])
    df = add_history(df, ["UserId", "skill_L0"], "_L0")
    df = add_history(df, ["UserId", "skill_L1"], "_L1")
    df = add_history(df, ["UserId", "skill_L2"], "_L2")
    df = add_history(df, ["UserId", "skill_L3"], "_L3")
    df = add_question_rate(df)
    return df