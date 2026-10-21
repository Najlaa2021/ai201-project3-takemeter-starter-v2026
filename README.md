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
| `take` | 167 | 57% |
| `experience` | 65 | 22% |
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

**Base model:**

**Settings:** <!-- epochs, learning rate, batch size, seed -->

**Anything I changed from the defaults, and why:**

**Split sizes:** <!-- train / val / test, and per-label counts in the test
split. If a label had fewer than about 8 in test, say so — it explains a lot
of next unit's variance. -->



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

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

     Don't fill these in during unit 5.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Baseline vs. Trained

<!-- Both models on the same posts. `python baseline.py --trained results.json`
     prints this table for you. -->

| Measure | Baseline | Trained | Difference |
|---|---|---|---|
| Overall accuracy |  |  |  |
| Macro F1 |  |  |  |
| F1 — `label_one` |  |  |  |
| F1 — `label_two` |  |  |  |

**What I predicted before I looked:**
<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A
     prediction made afterwards isn't one. -->

**What the gap actually means:**
<!-- If the baseline matched your trained model, your fine-tuning added
     nothing — and that is a real finding, not a failure. Say it plainly. -->



---

## Run Log — Before

<!-- Five criteria across three seeds. The notebook's section 6 prints the
     spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

### Confusion matrix

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.
     An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |
|---|---|---|---|
| **** |  |  |  |
| **** |  |  |  |
| **** |  |  |  |

**My biggest off-diagonal number, and what it means:**
<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which
     direction. "7 real analysis posts were called hot_take and only 3 went the
     other way" is a direction, not just an error rate. -->



---

## Verdicts and Diagnoses

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across
     all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**

<!-- For each miss: the cause, and how you know. The four common causes are:
     too few examples for a label, a boundary you applied inconsistently, a
     genuinely hard label pair, and a task the model can't reach from this
     much data.

     ⚠️ Use your agreement report as evidence. It is the only instrument you
     have that can tell a LABELLING problem from a MODEL problem, and this
     section is graded on whether you used it that way. -->



---

## Agreement Report

<!-- Your rate against the staff set, and every disagreement adjudicated.

     Remember you labelled these 30 under the STAFF taxonomy in
     data/staff_taxonomy.md, not your own — so every argument below is made
     from those definitions and those decision rules. -->

**Agreement rate:** ___ / 30 = ___%

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



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Run Log — After

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely
     interesting result and earns full credit. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped. -->



**The gap between what I meant my labels to capture and what the model
learned:**
<!-- Two sentences. Your confusion matrix is the evidence. -->



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
