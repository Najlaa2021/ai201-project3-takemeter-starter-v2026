# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the
> notebook, the baseline, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv     # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` **in this folder** — in VS Code, or with
> `jupyter notebook` if you prefer. Pick the kernel: the `.venv` inside this
> project. Run section 1, which reports the hardware you'll be training on.
> Everything else waits until you have data.
>
> Nothing to upload, nothing to connect, no accounts and no keys. The notebook
> runs on your machine and writes next to your code.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     Unit 5 asks for the first five sections. Unit 6 adds the five below them.

     Everything is pasted as TEXT. No screenshots, no images.

     ⚠️ The confusion matrix especially. The notebook prints one as a markdown
     table, ready to copy. A screenshot of a matrix earns nothing. Paste the
     table.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Your community, and what your classifier sorts posts into. Three or four
     sentences. -->

TakeMeter sorts comments from **Hacker News** (news.ycombinator.com), a
public tech and startup forum, into three labels by *what a comment offers to
back up what it says*:

- **`evidence`:** something you could check yourself.
- **`experience`:** the commenter's own first-hand account.
- **`take`:** nothing at all; opinions, jokes, jabs and quick reactions.

It doesn't judge whether a comment is right or well written, only what kind
of support it rests on.

### Notes from reading (Milestone 1)

These came from reading the first 70 comments in `data/hn_pool.csv`
(`reading_sample.md` has the first 40), plus the 270 after them while
labelling:

1. **Some comments link to, quote or name something outside themselves.**
   For example a doc page, a CVE-style incident, a named standard ("CAA
   records"), or a number with a source. Most don't.
2. **Some comments are first-person accounts.** "My $dayJob was poking at
   the unifi controller", "I have 5 blue jays in my yard". These feel
   substantial even with no link, because the commenter was there.
3. **Many comments are aimed at another commenter, not the topic.** "Surely
   you can concede…", "Respectfully: you are out of your depth." They carry
   heat but no support.
4. **A large share are one-line quips or reactions.** "They're selling
   delegated responsibility as a service. Seriously?" These make a point,
   but don't argue it.

Distinctions 3 and 4 turned out to be the same label, because what they have
in common is that nothing backs them up. Splitting them would have made a
fourth label that was hard to tell apart from the third.

---

## Label Taxonomy

### `evidence`

**Definition:** The comment backs its point with something a reader could
check without taking the commenter's word: a link offered as support, a
published number, a quote, or a named document, standard or public event.

**Example 1:**
> > Why isn't there a mechanism where a domain owner can specify which CA it allows?
>
> CAA records do this, but only for issuance, not for use, so it only protects against eg. unexpected domain validation, because the CA has to respect the CAA record.  Extending that to use seems like a logical step to me.

**Example 2:**
> Yes, we're discussing though in safe (non-unsafe/normal) Rust here. There is no safe C++, everything in C++ is unsafe by default. Even more unsafe than Rust unsafe, because Rust unsafe still does a lot of the safety measures of normal Rust, but allows only a handful extra things and doesn't disable the borrow checker:
>
> https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html
>
> But getting back to the point, the C++ compiler doesn't have a borrow checker, so it can't have a bug in it. So it's on you, as the developer, to take care of all unsoundness. […]

### `experience`

**Definition:** The comment's support is the commenter's own first-hand
account (something they did, built, used, measured or saw), with nothing a
reader could check independently.

**Example 1:**
> > unifi seems to have some bug
>
> Maybe things have changed in the past few years but prior to covid a decent chunk of my $dayJob was poking about the internals of the unifi controller to support an API.
>
> They used MongoDB for stats. If they still do, that might explain the bug :)

**Example 2:**
> I have 5 blue jays in my yard and they don't care about the sparrows, finches, etc at all. They only feud with the crows.

### `take`

**Definition:** An opinion, prediction, joke, jab or quick reaction with no
support offered, neither something checkable nor a first-hand account.

**Example 1:**
> They're selling delegated responsibility as a service. Seriously?

**Example 2:**
> If the main effort is trawling through forums or poorly written documentation the main thing you've learned is how to trawl through these things. I'm of the opinion these should've never been useful skills to begin with.

### The hardest boundary

**Which two labels:** `evidence` and `experience`. Lots of HN comments are
personal stories that also contain numbers or links, like the M1 MacBook
comment in hard case 1 below.

**The decision rule I used every time:** If the comment gives the reader
*anything they could check without taking the commenter's word* (a link
offered as support, a published number, a quote, or a named document,
standard or public event), it's `evidence`, even if it's told as a
personal story. If its only support is the commenter's own account, it's
`experience`, however many numbers it contains; the commenter's own
electricity bill isn't checkable. A link to the commenter's own project, or
a link that is the subject of a joke or reaction, doesn't count as support.

A second, smaller rule for `take` versus `evidence`: a technical claim
stated with confidence ("On Windows it always goes in the order of what was
used last") is still `take` unless it names something checkable. Being
specific isn't the same as offering support.

---

## The Dataset

**Where the posts came from:** Public Hacker News comments, pulled from
the HN Algolia search API: 9 comments each from 40 popular stories (150+
points, 80+ comments) posted in the three weeks before October 20, 2026.
Comments under 60 or over 1,200 characters were skipped. All 360 are in
`data/hn_pool.csv`, with a link to each original. No login is needed to
read any of them.

**How I labelled them:**

- **Pre-labelling.** Claude read and pre-labelled comments 1–250 of the
  pool, then 251–340 keeping only the `evidence` and `experience` ones,
  because `evidence` was my thinnest label (41) after the first 250.
  Every pre-labelled row says `pre-labelled by Claude` in the `note` column.
  One comment (#31, in Romanian) was dropped.
- **The rule changed partway.** It began as "label by whichever support
  comes first", then became the presence test above. All earlier rows were
  re-checked against it, which moved 4 labels. An audit of every row
  containing a link then moved 4 more (see How I Used AI).
- **Cold labels.** Comments 341–360 were set aside unread for my 20 cold
  labels.

**Counts per label** (all 295 rows: 275 pre-labelled plus 20 cold):

| Label | Count | Share |
|---|---|---|
| `take` | 168 | 57% |
| `experience` | 64 | 22% |
| `evidence` | 63 | 21% |
| **Total** | 295 | 100% |

**Three hard cases**

**1.**
> *The post:* "Here's an anecdote. I have repurposed my 6 year old 32gb M1 MacBook Pro to run Qwen 3.6 35b a3b … My MBP consumes 0.1w idle and about 10w running inference. I pay $0.33/kwh. If it runs for 2 hours a day over 365 days - it will cost $2.41/year …"
>
> *Could have been:* `evidence` or `experience`.
>
> *I chose `experience`, because:* every number in it comes from the
> commenter's own machine and electricity bill. A reader can't check any of
> it without trusting them. This is the post that made me write the
> decision rule.

**2.**
> *The post:* "I did my thesis on this back in 2018, around 566k fingerprints, mostly phones. Can confirm they change a lot. Almost 10% of returning devices had a new one within a day. … Data is old now though: https://virpo.sk/browser-fingerprinting-hraska-diploma-thesis.pdf"
>
> *Could have been:* `experience` or `evidence`.
>
> *I chose `evidence`, because:* it reads like hard case 1, a personal
> story with numbers, but the last line links the published thesis, so a
> reader can check every figure. I first had it as `experience`, and
> relabelled it when I re-checked every row containing a link.

**3.**
> *The post:* "Honestly, it shouldn't even be possible to suspect and be unable to prove. They should be prohibited from using customers data as training data. That is copyright theft and corporate espionage. … https://youtu.be/GweKOBSJvEY…"
>
> *Could have been:* `take` or `evidence`.
>
> *I chose `evidence`, because:* the rule says a link offered as support
> counts, and the video is posted as backing for the argument. It doesn't
> feel like `evidence`, because the text is a rant and the link is
> unexplained. This is where the rule is weakest: it checks whether support
> is *offered*, not whether it's any good. I kept it anyway, because a rule
> that bent for posts I didn't like would stop being a rule.

---

## The Training Run

<!-- Your starting model, your settings, and anything you changed and why. -->

**Base model:** `distilbert-base-uncased`

**Settings:** 3 epochs, learning rate `2e-5`, batch size 16, seed 42 for the
unit 5 run. Unit 6 retrains on seeds 42, 7 and 2024.

**Anything I changed from the defaults, and why:** Only `LABELS`, to
`evidence` / `experience` / `take` so they match `labels.csv`. Training
settings stayed at the notebook defaults.

**Split sizes:** 70 / 15 / 15, stratified. With 295 rows that is about 206
train / 45 val / 44 test. `evidence` and `experience` each get about 9–10
test examples — under the "about 8" warning line, so their F1 will jump
between seeds.



---

## How I Used AI

**Moment 1: stress-testing the boundary**

- *What I asked for:* posts written to sit on the `evidence`/`experience`
  line, to see whether my first rule ("label by whichever support comes
  first") gave clean answers.
- *What came back:* posts like *"At my last job we used Kafka and it was a
  nightmare; LinkedIn's own postmortem (link) says the same."* Under the
  first-support rule that's `experience`, but reverse the two sentences
  and it becomes `evidence`. Same content, different label.
- *What I changed:* I replaced the ordering rule with a presence test
  (anything checkable makes it `evidence`), then re-checked every
  pre-labelled row against it. 4 labels moved.

**Moment 2: auditing links against my own rule**

- *What I asked for:* a list of every row that contains a link but isn't
  labelled `evidence`.
- *What came back:* 10 rows. Four of them (a published thesis, a benchmark
  write-up, a GitHub PR, a video posted as backing) were links offered as
  support that I had labelled `experience` or `take` from the overall feel
  of the post.
- *What I changed:* I relabelled those four as `evidence`, and kept the six
  where the link was a product recommendation, the commenter's own project
  or earlier comment, or the subject of a reaction. That's why hard
  cases 2 and 3 are `evidence`.

**Pre-labelling disclosure:** All 275 non-cold rows were pre-labelled by
Claude (Anthropic), and marked `pre-labelled by Claude` in the `note`
column. The 20 rows marked `cold` were labelled by me alone, with no tools,
before I looked at any pre-label. Claude also collected the posts through
the HN API and drafted this README.

**Moment 3: unit 6 runs and write-up (Cursor / Claude)**

- *What I asked for:* help running the baseline, the three-seed retrains,
  and filling the unit 6 README from the JSON the scripts wrote.
- *What came back:* a headless `run_unit6.py` that copies the notebook's
  train/eval functions so the three seeds could finish without a kernel
  restart; the Baseline vs. Trained table from `baseline.py`; and a draft
  of the verdicts that I checked against the three-seed JSON.
- *What I changed:* I kept the numbers the scripts produced. I wrote the
  diagnoses and the staff-set labels myself. I used the model to argue the
  opposite verdict on criterion 3 (beats baseline) before I locked MET.

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

Same 45 held-out posts (`test_split.csv`, seed 42). Baseline used
`label_definitions.txt`. Device: Apple Silicon GPU (MPS), torch 2.14.1.

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy | 0.222 | 0.578 | +0.356 |
| Macro F1 | 0.138 | 0.244 | +0.106 |
| F1 — `evidence` | 0.340 | 0.000 | -0.340 |
| F1 — `experience` | 0.000 | 0.000 | +0.000 |
| F1 — `take` | 0.074 | 0.732 | +0.658 |

**What I predicted before I looked:**
The trained model will beat the baseline most on `take`, because that
label is 57% of the data and often looks like a short jab. It will gain
less on `evidence` vs `experience`, because that is the boundary I already
had to write a decision rule for.

**What the gap actually means:**
Fine-tuning added something, but only for `take`. The trained model is a
majority classifier: it called every test post `take` (26/45, accuracy
0.578). The baseline was the opposite — it over-called `evidence` (recall
1.0, precision 0.20) and almost never said `take` (recall 0.038). So the
+0.356 accuracy is "learned the common label," not "learned the taxonomy."
The baseline actually beat the trained model on `evidence` F1 (0.340 vs
0.000). That matches the prediction in direction (`take` is where training
won) and is worse than I hoped on the hard boundary.



---

## Run Log — Before

Device: Apple Silicon GPU (MPS). Three epochs, lr 2e-5, batch 16.
Accuracy did **not** swing across seeds — it stuck at 0.578 all three times
because every seed collapsed to always-`take`.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 | 0.578 | 0.578 | 0.578 | MISSED |
| 2. Every label F1 | ≥ 0.50 | ev 0.00 / ex 0.00 / take 0.73 | ev 0.00 / ex 0.00 / take 0.73 | ev 0.00 / ex 0.00 / take 0.73 | MISSED |
| 3. Beats the baseline on accuracy | yes (baseline 0.222) | yes (0.578) | yes (0.578) | yes (0.578) | MET |
| 4. Precision on `evidence` | ≥ 0.60 | 0.00 | 0.00 | 0.00 | MISSED |
| 5. Recall on `take` | ≥ 0.70 | 1.00 | 1.00 | 1.00 | MET |

### Confusion matrix

Seed 42 (seeds 7 and 2024 produced the same matrix):

| true \ predicted | evidence | experience | take |
|---|---|---|---|
| **evidence** | 0 | 0 | 9 |
| **experience** | 0 | 0 | 10 |
| **take** | 0 | 0 | 26 |

**My biggest off-diagonal number, and what it means:**
19 real support posts (9 `evidence` + 10 `experience`) were called `take`,
and 0 went the other way. The model did not learn either support boundary.
It learned one direction: when unsure, say `take`. That is a collapse to
the majority class, not an `evidence`/`experience` mix-up.



---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Overall accuracy | ≥ 0.65 | MISSED | 0.578 on every seed. 0.65 has to hold on all three, and it held on none. |
| 2 | Every label F1 | ≥ 0.50 | MISSED | `evidence` and `experience` F1 are 0.00 on every seed. `take` is 0.73, which is not enough — the criterion says every label. |
| 3 | Beats the baseline on accuracy | yes | MET | Baseline accuracy on the seed-42 held-out set is 0.222. Every trained seed is 0.578. |
| 4 | Precision on `evidence` | ≥ 0.60 | MISSED | The model never predicted `evidence`, so precision is 0.00. |
| 5 | Recall on `take` | ≥ 0.70 | MET | Recall is 1.00 on every seed — it called every post `take`. |

**Diagnoses**

**1 and 2 and 4 — training never left the majority class.** Val macro-F1
stayed at 0.238 for all three epochs on seed 42, and the test matrix is
all-`take` on every seed. This is not "too few examples" in the sense of a
jumpy F1 on 9 rows — the model produced *zero* minority predictions. 63
`evidence` and 64 `experience` rows exist in the file. Three epochs at
2e-5 with a 57% majority was not enough training for DistilBERT to use
them. That is a training-setting cause, with the stuck val curve as
evidence.

**Not a labelling-boundary diagnosis, as far as I can tell from the
staff set I have.** I labelled the 30 staff posts under *their* taxonomy
(`analysis` / `hot_take` / `reaction`) and applied their four rules
without flipping back and forth on the obvious ones (1–10 analysis,
11–20 hot_take except the "3% shoes" example which is their own
hot_take, 21–30 reaction). I do not yet have `data/staff_labels.csv`
from the TF, so I cannot compute an agreement rate or point at a pair I
applied two ways. The trained matrix also does **not** show
`evidence`↔`experience` confusion — it shows no `evidence` or
`experience` predictions at all. If my own 295 labels were noisy on that
boundary, this run never got far enough to reveal it.

**The task is reachable from 200+ examples in principle** (the baseline
already got `evidence` F1 0.340 with no training). The miss is that
fine-tuning for 3 epochs on this imbalance erased that and replaced it
with always-`take`.



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** not computed yet — `my_staff_labels.csv` is filed (30
rows, staff taxonomy). `data/staff_labels.csv` has not arrived from the
TF, so `agreement.py` cannot run. I labelled first and stopped, as the
brief requires.

I applied the staff rules as:

- **sp_001–sp_010 → `analysis`.** Each one uses a load-bearing number,
  date, or comparison (rule 1). Even the first-person ones (sleep log,
  heat loop, carbon plates) argue *from* the measurement.
- **sp_011–sp_020 → `hot_take`.** Confident general claims, no
  load-bearing fact. sp_014 is their own worked example: "times are down
  3%" is decoration on a conclusion already reached.
- **sp_021–sp_030 → `reaction`.** About the writer, just now. sp_027's
  "20 degrees" and sp_028's "third DNF this year" are not load-bearing
  arguments (rule 2).

Once `staff_labels.csv` is in `data/`, the command is `python agreement.py`.
I will adjudicate every disagreement from those four rules, including
wins, and will not write "staff is right" as a default.

<!-- Nobody grades this number. A 60% who argues every disagreement from the
     stated rules beats a 95% who wrote "staff was right" nine times. Several
     of the 30 were chosen because they're genuinely ambiguous — you should be
     winning some of these. -->

**Disagreements**

<!-- Three lines each: the post, both labels, and who you think is right and
     why — grounded in the staff definitions you were both applying.

     Then sort each into one of three piles:
       (a) the rule covered it and I applied it loosely → a consistency problem
       (b) the rule genuinely doesn't say               → a gap in the definitions
       (c) the rule is ambiguous here and my reading is defensible → argue it.
           This is a legitimate win.

     Pile (a) is the one that matters most for your diagnosis: if you applied a
     written rule two different ways on 30 posts, that is direct evidence about
     what you did across your own 200. -->

**1.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**2.**
> *The post:*
>
> *Staff said / I said:*
>
> *My call, and why:*
>
> *Which pile:*

**What the pattern in my disagreements tells me:**
I cannot use agreement as evidence yet. The pattern I *can* use is the
confusion matrix: the model never reached the `evidence`/`experience`
boundary my unit 5 hard cases were about. Until it predicts those labels,
a labelling-inconsistency story is not supported by this run.



---

## The Improvement

**What I changed:**
One training setting: **3 epochs → 8 epochs**. Labels, taxonomy, criteria,
learning rate, batch size, and the three seeds stayed the same.

**Which diagnosis pointed at it:**
The before-run val macro-F1 sat at 0.238 for every epoch, and the test
matrix was always-`take`. That is the brief's "change one training
setting" case: the diagnosis named training, not a boundary I applied two
ways (I still do not have staff labels to prove a labelling inconsistency).

### Run Log — After

From `results_three_seeds_after.json`. Device: Apple Silicon GPU (MPS).
Eight epochs, lr 2e-5, batch 16. Same three seeds, same splits.

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1. Overall accuracy | ≥ 0.65 | 0.644 | 0.622 | 0.644 | MISSED (close) |
| 2. Every label F1 | ≥ 0.50 | ev 0.50 / ex 0.29 / take 0.77 | ev 0.38 / ex 0.38 / take 0.76 | ev 0.63 / ex 0.27 / take 0.75 | MISSED |
| 3. Beats the baseline on accuracy | yes (0.222) | yes (0.644) | yes (0.622) | yes (0.644) | MET |
| 4. Precision on `evidence` | ≥ 0.60 | 0.571 | 0.429 | 0.714 | MISSED |
| 5. Recall on `take` | ≥ 0.70 | 0.885 | 0.846 | 0.846 | MET |

**Confusion matrix — after, seed 42** (rows = true, columns = predicted)

| true \ predicted | `evidence` | `experience` | `take` |
|---|---|---|---|
| `evidence` | 4 | 1 | 4 |
| `experience` | 1 | 2 | 7 |
| `take` | 2 | 1 | 23 |

**Did it help, and how do I know:**
Yes, by the test I set beforehand: `evidence` and `experience` F1 left
0.00 and accuracy left 0.578 on all three seeds. Macro F1 went from 0.244
to 0.50–0.55 (0.518 / 0.503 / 0.546), and every seed now predicts all three labels. It did not
help enough to flip a criterion: accuracy sits just under 0.65 on every
seed, and `experience` F1 (0.27–0.38) is the weakest number in the table.
The matrix shows where it still fails. Most `experience` posts (7 of 10
on seed 42) go to `take`, not to `evidence`. So the boundary the model is
missing is `experience`/`take`, not the `evidence`/`experience` one I
wrote my unit 5 rule for.



---

## What's Still Broken

**1 / 2 / 4 (accuracy, every-label F1, evidence precision).** Next I would
either train longer still, or add ~30 more `evidence` and `experience`
rows and keep 8 epochs. I stopped at one change (epochs) because the
brief allows one. I ran out of the second change.

**Agreement.** `staff_labels.csv` is still with the TF. The 30 labels I
wrote are in `my_staff_labels.csv`. I will adjudicate as soon as the
answer key is in `data/`.

**The gap between what I meant my labels to capture and what the model
learned:**
I meant three kinds of *support*: checkable, first-hand, or none. The
confusion matrix shows the model learned one kind: `take`. It never
predicted `evidence` or `experience`, so the hard boundary I spent unit 5
on is not something this run can have learned.



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 5

       [ ] criteria.md has five numbered criteria, each naming a NUMBER
       [ ] Each has a reason underneath tied to your data or taxonomy
       [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split
       [ ] No label above 70%
       [ ] All five unit 5 sections have real content
       [ ] Label Taxonomy includes the decision rule for your hardest boundary
       [ ] The Dataset includes three hard cases
       [ ] results.json and test_split.csv committed (the notebook does this)
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 6

       [ ] Baseline vs. Trained table, with your prediction written beforehand
       [ ] Run Log — Before, five criteria across three seeds
       [ ] Confusion matrix TYPED AS A MARKDOWN TABLE
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, using the agreement report as evidence
       [ ] Agreement Report with every disagreement adjudicated
       [ ] One improvement, with Run Log — After
       [ ] What's Still Broken
       [ ] results_three_seeds_before.json, results_three_seeds_after.json,
           baseline_results.json and
           agreement_results.json committed
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
