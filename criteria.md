# Acceptance criteria — TakeMeter

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## 1. Overall accuracy of at least 0.65

The model is right on at least 65% of held-out posts, on every seed.

**Why this target:** A always-guess-`take` rule would already be right about
57% of the time (`take` is 168 of 295 rows). 0.65 is above that majority
baseline, so the model has to have learned something about `evidence` and
`experience`, not just the common label. It is still loose enough that a
15% test split (~44 posts) can miss it on an unlucky seed.

---

## 2. Every label has an F1 of at least 0.50

`evidence`, `experience`, and `take` each have F1 ≥ 0.50 on the held-out set,
on every seed.

**Why this target:** `evidence` (63) and `experience` (64) are my thinnest
labels. About 9–10 of each land in a 15% test split, so F1 on those labels
will jump. 0.50 is lower than I would set for `take`, and I am saying so on
purpose: a 0.60 floor on 9 examples is a coin-flip dressed as a target.

---

## 3. Beats the zero-shot baseline on accuracy

The fine-tuned model's overall accuracy is higher than the baseline's, on
every seed, when both are scored on that seed's held-out posts.

**Why this target:** Fine-tuning 200+ labelled HN comments should beat a
general model that has only my three definitions. If it does not, training
added nothing, and that is a finding I want a number I can check.

---

## 4. Precision on `evidence` of at least 0.60

Of the posts the model called `evidence`, at least 60% really were, on every
seed.

**Why this target:** My hardest boundary is `evidence` vs `experience`. A
false `evidence` label is the worse error for this taxonomy — it tells a
reader there is something checkable when there is not. 0.60 means I will
tolerate some leakage, but not a model that sprays `evidence` on personal
stories.

---

## 5. Recall on `take` of at least 0.70

Of the posts that really were `take`, the model catches at least 70%, on
every seed.

**Why this target:** `take` is 57% of the data and the easiest definition
("nothing backs it up"). Missing a third of them would mean the model is
over-calling support on jabs and one-liners, which is the opposite of what
the taxonomy is for.

---
