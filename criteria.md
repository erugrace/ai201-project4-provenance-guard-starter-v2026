# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. Human writing is recognised as human

<!-- Your criterion. It must name a number. -->

Of 10 pieces of writing by real people, at least 8 are labelled
high-confidence human, in each of the 3 trials.

**Why this target:** On a writing site, the people using the service are
mostly real writers, and they need to be recognised as writers. Calling a
real person's work AI costs them far more than a missed AI text costs the
site. 8 of 10 is demanding but possible. It has to hold in every trial
because the model can score the same text differently each run.

---

## 2. Borderline text lands in "unsure", and every label is reachable

<!-- Your criterion. -->

Of 5 texts I judge borderline (e.g. lightly edited AI, plain human writing),
at least 4 get a combined score between 0.35 and 0.65 and the "unsure"
label. Across all my test texts, each of the three labels appears at least
once.

**Why this target:** "Unsure" is the safety net for the writers my signals
misread, so it has to catch the hard cases instead of pushing them to one
side. A label that no text can reach means part of the system doesn't work.

---

## 3. Bad input is refused cleanly, never crashes

<!-- Your criterion. -->

Of 5 malformed requests (missing `text`, empty `text`, `text` that is only
spaces, `text` under 10 words, `text` over 20,000 characters), all 5 return
a 400 with a JSON error message, none return a 500, and each is logged as
rejected.

**Why this target:** A crash on bad input is one of the most common real
failures, and unit 8's attacks will send exactly these. Under 10 words gives
the signals too little to measure, so a score would be a guess dressed up as
a decision. It's 5 of 5 because a single 500 is a crash, not a near miss.

---

## 4. Clearly-AI and clearly-human text score far apart

<!-- Your criterion. -->

The average combined score of my clearly-AI texts is at least 0.3 higher
than the average combined score of my clearly-human texts, in each of the 3
trials.

**Why this target:** If the two kinds of text score close together, no
threshold can separate them, and every label is close to a guess. A gap of
0.3 is as wide as the whole 0.35–0.65 "unsure" band. Anything smaller and
clearly-AI and clearly-human text could both sit inside it.

---

## 5. Labels describe the text, never accuse the person

<!-- Your criterion. -->

None of the three labels says the writer "used AI", "cheated" or
"plagiarised". All three describe the text, not the person. The
high-confidence AI and unsure labels both tell the reader how to appeal.

**Why this target:** The person reading the AI label may well have written
every word themselves, as in the false-positive trace from Milestone 1. A
label shouldn't accuse them, and it should give them a way out. This is all
or nothing because there are only three labels and every reader sees one of
them.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
