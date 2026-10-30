# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **A writer sends the text.** A client POSTs JSON to `/submit` with `text`
   and `creator_id`. *Adds:* the raw material, plus who it belongs to.
2. **The route checks the request** (`app.py::submit`). It rejects missing,
   empty, non-string, too-short or too-long text with a 400 before any model
   runs, and logs the rejection. *Adds:* a guarantee that everything after
   this step gets clean input, and a trace of anything refused.
3. **The model signal reads it** (`detector.model_signal`). gpt2 measures how
   predictable the text is and squashes that onto 0–1. *Adds:* `model_score`,
   where higher means more likely AI.
4. **The style signal measures it** (`stylometry.style_signal`). This looks
   at the shape of the text: sentence-length spread, vocabulary repetition
   and punctuation. *Adds:* `style_score` on the same 0–1 scale, also with
   higher meaning more likely AI.
5. **The two are combined** (`scoring.combine_signals`). *Adds:* one combined
   score, the single number every later decision depends on.
6. **The score becomes words** (`scoring.score_to_label`, thresholds in
   `config.py`). *Adds:* a `guess` (`human` / `unsure` / `ai`) and the label
   sentence the reader actually sees.
7. **The decision is logged and returned** (`audit.log_decision`). The
   service gives it a `content_id`, writes all the scores and the label to
   the audit log, and sends it all back. *Adds:* a permanent record, plus the
   one handle the writer needs if they want to appeal.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How *predictable* the text is to a language model
(gpt2). This is perplexity: how surprised the model is by each next word. Low
perplexity gets a high score, meaning more likely AI.

**Why that might differ between human and AI writing:** A language model
writes by picking a likely next word again and again, so its output is text a
model finds easy to predict. Human writing wanders more. People make odd word
choices, change direction suddenly, and reach for specific details over
typical ones.

**What it can't see:** *Who* wrote the text. Predictability is not
authorship. What this signal really rewards is common words in short, ordinary
sentences, and many real people write that way: second-language writers
sticking to words they're sure of, younger writers, anyone writing plainly on
purpose. Their honest work can score as machine-like. It also fails the other
way. AI text pushed toward rare words or ornate phrasing ("write it more
unusually") surprises the model and can pass as human. It only reads the
first ~400 tokens, so anything after that is invisible to it.

### Signal two — the style signal

**What it measures:** The *shape* of the text, without reading its meaning:
how much sentence length varies, how much vocabulary repeats (type-token
ratio), and how much varied punctuation is used. Even sentences, a narrow
vocabulary and sparse punctuation score higher, meaning more likely AI.

**Why that might differ between human and AI writing:** Going for the most
likely next word, on average, produces even, mid-length sentences and a
narrower band of vocabulary. Human writing is lumpier: a three-word sentence
next to a forty-word one, a dash, a fragment.

**What it can't see:** What the text *says*. It can't read at all, so
anything that changes the shape without changing the substance moves the
score. Someone can take AI text and break up sentences, add typos, or paste
in a quotation to make it look "human". A careful human writer with a tidy,
even style can look "AI". Type-token ratio also falls as text gets longer, so
length alone can move the score.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:**

**The numbers:**

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

The text is `samples/clearly_ai.json`, read out of the file so the full
paragraph doesn't need pasting into the command.

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d "$(python -c 'import json; t=json.load(open("samples/clearly_ai.json"))["text"]; print(json.dumps({"text": t, "creator_id": "derin"}))')"
```

```json
{
  "confidence": 0.5,
  "content_id": "c_a3d699f87c4a",
  "guess": "unsure",
  "label": "not built yet",
  "model_score": 0.7544,
  "style_score": null
}
```

<!-- Unit 7, Milestone 3: model_score is real. confidence, guess and label are
     placeholders, and style_score is null until Milestone 4. -->


**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "creator_id": "u1",
      "event": "rejected",
      "reason": "text_too_long",
      "status": "rejected",
      "timestamp": "2026-10-30T03:13:05+00:00"
    },
    {
      "creator_id": null,
      "event": "rejected",
      "reason": "missing_creator_id",
      "status": "rejected",
      "timestamp": "2026-10-30T03:13:05+00:00"
    },
    {
      "combined_score": null,
      "content_id": "c_a3d699f87c4a",
      "creator_id": "derin",
      "guess": "unsure",
      "label": null,
      "model_score": 0.7544,
      "status": "decided",
      "style_score": null,
      "timestamp": "2026-10-30T03:18:18+00:00"
    }
  ]
}
```

<!-- The last entry is the submission above: same content_id, same
     model_score. The two before it are bad-input tests (text over 20,000
     characters, missing creator_id), rejected with a 400 and still logged. -->


---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
