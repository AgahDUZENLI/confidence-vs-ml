# Findings Log

What we learned about the data.
Numbers come from `src/data.py`.

---

## 1. The files (Step 1)

| File | Rows | What one row is |
|---|---|---|
| answers | 1,382,727 | one answer by one student |
| answer metadata | 1,508,917 | date and confidence for one answer |
| students | 6,148 | one student |
| questions | 948 | one question and its topics |
| subjects | 388 | one topic |

- **Answer metadata has 126,190 extra rows.** These answers are not in the answers file, so we don't know if they were right or wrong. They are probably the competition's hidden test set. We can't use them, and the merge drops them.
- **Only 4,918 of the 6,148 students have answers.** The other 1,230 students are never used.
- **How the files connect:**
  - answers ↔ answer metadata: `AnswerId`
  - answers ↔ students: `UserId`
  - answers ↔ questions: `QuestionId`
- **Columns stored in the wrong type:**
  - `DateAnswered` is text. Convert it to a date before sorting.
  - `SubjectId` in questions is text that looks like a list, `"[3, 71, 98, 209]"`. Convert it to a real list.

## 2. Merging (Step 2)

- We merged everything onto the answers table with `how="left"`.
- Result: **1,382,727 rows × 15 columns**. Same number of rows as answers, so nothing was lost or duplicated.

## 3. Data quality (Step 3)

- **No duplicate answers.** Every `AnswerId` appears once.
- **No student answered the same question twice.** So "past answers on this exact question" can't be a feature.
- **`IsCorrect` is always right.** It always matches `CorrectAnswer == AnswerValue`. The target can be trusted.

## 4. Target: IsCorrect

- **53.7% of all answers are correct.**
- So "always guess correct" already gets **53.7% accuracy**. This is the majority-class baseline our models must beat.
- The classes are almost balanced (54 / 46), so **accuracy is a fair metric** and we don't need class weights.

## 5. Confidence

| Rating | Answers |
|---|---|
| 100 | 159,469 |
| 75 | 87,778 |
| 50 | 53,043 |
| 25 | 17,405 |
| 0 | 28,733 |
| no rating | 1,036,299 |

- **Only 5 possible values: 0, 25, 50, 75, 100.** It's not a full 0–100 scale.
- **346,428 answers have a rating (about 25%).** We compare models and confidence on these only.
- **100 is the most common rating.** Students lean toward saying they are sure.
- The reliability diagram for confidence will have exactly 5 points.

**How often each rating is actually correct:**

| Rating | Actually correct | Gap |
|---|---|---|
| 0 | 33.5% | +33.5 (underconfident) |
| 25 | 38.8% | +13.8 (underconfident) |
| 50 | 48.3% | −1.7 (about right) |
| 75 | 64.5% | −10.5 (overconfident) |
| 100 | 73.3% | −26.7 (overconfident) |

- Answers rated 100 are correct only 73.3% of the time.** About 1 in 4 "sure" answers is wrong.
- **Students are overconfident at the top and underconfident at the bottom.** Students who say "0, I'm guessing" still get a third right.
- **But the order is right.** Higher ratings always mean more correct answers. So confidence does carry real information. It's just badly calibrated.
- This means confidence could have a decent AUC (good ranking) but a bad ECE (wrong probabilities). Our models need to beat it on both.

## 6. Gender

| Value | Meaning | Answers | % |
|---|---|---|---|
| 1 | female | 472,040 | 34.1% |
| 2 | male | 467,265 | 33.8% |
| 0 | unspecified | 442,838 | 32.0% |
| 3 | other | 584 | 0.04% |

- **0 means "unspecified".** It's missing data hidden as a number, so `isna()` doesn't see it.
- **Female and male are almost equal.** That comparison is fair.
- **"Other" has only 584 answers.** Too few for a reliable result. Say so in the report instead of reporting a noisy number.

## 7. Free school meals (PremiumPupil)

`1` = eligible for free school meals (lower-income family), `0` = not eligible, empty = unknown.

| Value | Answers | % of all |
|---|---|---|
| 1 | 197,380 | 14.3% |
| 0 | 510,480 | 36.9% |
| unknown | 674,867 | 48.8% |

- **About half of the answers have no group.** The group comparison only uses the other half.
- **Among known students, about 28% of answers come from free-school-meal students.**
- **Students with a known status answer more questions.** 58.7% of all students in the student file are unknown, but only 48.8% of answers are. So the unknown students are less active.

**Percent correct by group:**

| Group | Correct |
|---|---|
| Not eligible | 54.6% |
| Free school meals | 44.4% |

- **Free-school-meal students get about 10 points fewer answers right.**
- Because the groups have different base rates, accuracy and calibration can differ between groups even if the model is equally good. AUC doesn't depend on the base rate, so use AUC as the main fairness check.
## 8. Topics / skills

Each question has a list of topics from broad to specific, e.g. `[3, 71, 98, 209]` = Maths → Geometry and Measure → Units of Measurement → Time. The `subjects` file gives each topic's `Level` (0 = Maths, 3 = most specific).

| Level | Topics used by our questions | Questions per topic |
|---|---|---|
| 0 | 1 (Maths) | 948 |
| 1 | 3 (Number, Algebra, Geometry and Measure) | 144–509 |
| 2 | 25 | 2–141 |
| 3 | 57 | 1–59 |

- **Our 948 questions use 86 of the 388 topics.** The rest are never used.
- **Level 1 is too broad.** "Number" covers more than half of all questions.
- **Level 3 has some tiny topics.** 2 topics have only 1 question, and about a dozen have 5 or fewer. Since no student answers the same question twice, a 1-question topic can never have any past history.
- **Level 2 topics are bigger,** so students build up more history per topic.
- **A few questions have two topics at one level:** 2 questions at level 2, 14 at level 3 (1.5%). **We keep the first topic in the list.**
- We made two columns, `skill_L2` and `skill_L3`, one skill per question at each level. Every question has both.
- **Plan:** build features from both levels and pick the better one (or both) using AUC on the validation set.

## 9. Time order and ties

- `DateAnswered` only goes to the **minute**, not seconds.
- **940,464 answers (68.0%) share the same minute with another answer by the same student.** Ties are the normal case, not a rare one.
- **Why:** tied answers come from the same quiz (same `QuizId`). Students often answer about 2 questions per minute.
- **We can't know the true order inside a minute.** We sort by `UserId`, `DateAnswered`, then `QuestionId`. This makes the order fixed and repeatable (a student never answers the same question twice, so it never ties), but not necessarily true.
- **Leakage risk:** if two answers share a minute, the sorted "first" one may really have come second. A "so far" feature would then use a future answer. With 68% of answers in ties, this matters.
- **Decision for features:** only count answers from an **earlier minute** as "the past". Answers in the same minute don't count as each other's history.
