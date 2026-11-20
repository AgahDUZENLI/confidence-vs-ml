import pandas as pd
import ast

# Step 1: Load the data
answers = pd.read_csv("data/train_data/train_task_3_4.csv")
answer_meta = pd.read_csv("data/metadata/answer_metadata_task_3_4.csv")
students = pd.read_csv("data/metadata/student_metadata_task_3_4.csv")
questions = pd.read_csv("data/metadata/question_metadata_task_3_4.csv")
subjects = pd.read_csv("data/metadata/subject_metadata.csv")

questions["SubjectId"] = questions["SubjectId"].apply(ast.literal_eval)


print("Answers shape:", answers.shape)
print("Answer Metadata shape:", answer_meta.shape)
print("Students shape:", students.shape)
print("Questions shape:", questions.shape)
print("Subjects shape:", subjects.shape)

print("Unique students in answers:", answers["UserId"].nunique())
print("Unique questions in answers:", answers["QuestionId"].nunique())
print("Unique subjects:", subjects["SubjectId"].nunique())


# Step 2: Check for missing values and data types
tables = {
    "answers": answers,
    "answer_meta": answer_meta,
    "students": students,
    "questions": questions,
    "subjects": subjects,
}

for name, table in tables.items():
    summary = pd.DataFrame({
        "dtype": table.dtypes,
        "missing": table.isna().sum(),
        "missing %": (table.isna().mean() * 100).round(1),
    })
    print(f"\n=== {name}: {table.shape[0]:,} rows x {table.shape[1]} columns")
    print(summary)


# Step 3: Merge the dataframes to create a single dataframe for analysis
df = pd.merge(answers, answer_meta, on="AnswerId", how="left", validate="one_to_one")
df = pd.merge(df, students, on="UserId", how="left", validate="many_to_one")
df = pd.merge(df, questions, on="QuestionId", how="left", validate="many_to_one")
assert len(df) == len(answers), "Merge changed the number of rows!"
print("Final shape:", df.shape)


# Step 4: Check data types and missing values in the final dataframe
print("\n=== Data quality checks ===")

# 1. Any answer listed twice?
print("Duplicate answers:", df["AnswerId"].duplicated().sum())

# 2. Any student who answered the same question twice?
print("Repeated questions:", df.duplicated(subset=["UserId", "QuestionId"]).sum())

# 3. Is IsCorrect right? (picking the correct option = 1, otherwise 0)
right_option = df["CorrectAnswer"] == df["AnswerValue"]
print("Wrong IsCorrect values:", (right_option != df["IsCorrect"]).sum())

# 4. What confidence ratings are there?
print(df["Confidence"].value_counts(dropna=False))

# 5. How many answers come from each group?
print(df["Gender"].value_counts())
print(df["PremiumPupil"].value_counts(dropna=False))




print("\nPercent correct at each confidence rating:")
print(df.groupby("Confidence")["IsCorrect"].mean() * 100)

print("\nGender (% of answers):")
print((df["Gender"].value_counts(normalize=True) * 100).round(1))

print("\nPremiumPupil (% of answers):")
print((df["PremiumPupil"].value_counts(normalize=True, dropna=False) * 100).round(1))

print("\nPremiumPupil (% of known only):")
print((df["PremiumPupil"].value_counts(normalize=True) * 100).round(1))



# Step 5: Topics
# Give every question one "skill" at level 2 and one at level 3.

# Look up any topic's level
level_of = dict(zip(subjects["SubjectId"], subjects["Level"]))

# Which topics do our questions actually use?
used = questions["SubjectId"].explode().unique()
used_topics = subjects[subjects["SubjectId"].isin(used)]
print("Topics used:", len(used_topics))
print(used_topics["Level"].value_counts().sort_index())

# How many questions does each topic have?
q_per_topic = questions["SubjectId"].explode().value_counts()
used_topics = used_topics.assign(n_questions=used_topics["SubjectId"].map(q_per_topic))
print(used_topics[["Name", "Level", "n_questions"]].sort_values(["Level", "n_questions"]).to_string())

# How many topics does each question have at level 2 and level 3?
n_level2 = questions["SubjectId"].apply(lambda ids: sum(level_of[i] == 2 for i in ids))
n_level3 = questions["SubjectId"].apply(lambda ids: sum(level_of[i] == 3 for i in ids))
print("Level-2 topics per question:\n", n_level2.value_counts())
print("Level-3 topics per question:\n", n_level3.value_counts())

# Pick the first topic at a given level (some questions have two; we keep the first)
def topic_at_level(ids, level):
    for i in ids:
        if level_of[i] == level:
            return i
    return None

questions["skill_L2"] = questions["SubjectId"].apply(lambda ids: topic_at_level(ids, 2))
questions["skill_L3"] = questions["SubjectId"].apply(lambda ids: topic_at_level(ids, 3))
print(questions.head())
print("Questions with no level-2 skill:", questions["skill_L2"].isna().sum())
print("Questions with no level-3 skill:", questions["skill_L3"].isna().sum())



# Step 6 Time
df["DateAnswered"] = pd.to_datetime(df["DateAnswered"])
ties = df[df.duplicated(subset=["UserId", "DateAnswered"], keep=False)]
print(ties.sort_values(["UserId", "DateAnswered"])[["UserId", "QuestionId", "QuizId", "DateAnswered", "IsCorrect"]].head(10))
df = df.sort_values(["UserId", "DateAnswered", "QuestionId"]).reset_index(drop=True)

print("Answers in a tie:", len(ties))
print("Percent of all answers:", round(len(ties) / len(df) * 100, 1))