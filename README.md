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
2. **The route checks the request** (`app.py::submit`). It rejects a missing
   `creator_id`, or text that is missing, empty, under 10 words or over 20,000
   characters, with a 400 before any model runs, and logs the rejection. *Adds:* a guarantee that everything after
   this step gets clean input, and a trace of anything refused.
3. **The model signal reads it** (`detector.model_signal`). gpt2 measures how
   predictable the text is and squashes that onto 0–1. *Adds:* `model_score`,
   where higher means more likely AI.
4. **The style signal measures it** (`stylometry.style_signal`). This looks
   at the shape of the text, without reading it: how much sentence length
   varies and how much punctuation is used. *Adds:* `style_score` on the same
   0–1 scale, also with higher meaning more likely AI.
5. **The two are combined** (`scoring.combine_signals`): 0.4 × model_score +
   0.6 × style_score. *Adds:* one combined score, the single number every
   later decision depends on.
6. **The score becomes words** (`scoring.score_to_label`, thresholds in
   `config.py`: human below 0.35, AI above 0.70, unsure in between). *Adds:*
   a `guess` (`human` / `unsure` / `ai`) and the label sentence the reader
   actually sees.
7. **The decision is logged and returned** (`audit.log_decision`). The
   service gives it a `content_id`, writes all the scores and the label to
   the audit log, and sends it all back. *Adds:* a permanent record, plus the
   one handle the writer needs if they want to appeal.

If the writer thinks the label is wrong, they send that `content_id` and their
reasoning to `/appeal` (`app.py::appeal`). The appeal is logged next to the
original decision, the item moves to `under_review`, and a person looks at it.


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
how much sentence length varies (standard deviation ÷ mean of words per
sentence) and how much punctuation is used (commas, semicolons, colons,
dashes, brackets and quote marks per word). Even sentences and sparse
punctuation score higher, meaning more likely AI. The score is the average of
the two, each scaled onto 0–1.

I also measured type-token ratio (how much vocabulary repeats), but left it
out of the score: on my samples it ran the *wrong* way, with the AI text at
0.85 and the human text at 0.73.

**Why that might differ between human and AI writing:** Going for the most
likely next word, on average, produces even, mid-length sentences and a
narrower band of vocabulary. Human writing is lumpier: a three-word sentence
next to a forty-word one, a dash, a fragment.

**What it can't see:** What the text *says*. It can't read at all, so
anything that changes the shape without changing the substance moves the
score. Someone can take AI text and break up sentences, add typos, or paste
in a quotation to make it look "human". A careful human writer with a tidy,
even style can look "AI". My formal human sample (a lab report) scored 0.63
on this signal, leaning AI, for exactly that reason.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** A weighted average of the two signals, leaning on the style
signal. Both scores run 0–1 with higher meaning more likely AI, so the
combined score does too. When the two disagree, the average lands between
them, usually in the middle of the scale. That's on purpose: two methods
disagreeing *is* uncertainty, and a borderline score gets the "unsure" label
instead of an accusation.

I weight style more because on my samples it separated AI from human far
better than the model signal did (a gap of 0.77 against 0.31), and it caught
the lightly-edited AI that the model signal missed. I don't weight it any
more than 0.6, because style is the cheaper signal to fool. Adding commas or
breaking up sentences moves it, so the model signal keeps enough weight that
style tricks alone can't decide the result.

**The numbers:**

    combined = 0.4 × model_score + 0.6 × style_score

The weights are `WEIGHT_MODEL_SIGNAL = 0.4` and `WEIGHT_STYLE_SIGNAL = 0.6`
in `config.py`.

| Sample | model_score | style_score | combined | Label band |
|---|---|---|---|---|
| clearly_ai | 0.75 | 0.84 | 0.80 | high-confidence AI |
| clearly_human | 0.44 | 0.07 | 0.22 | high-confidence human |
| borderline (lightly-edited AI) | 0.35 | 0.61 | 0.50 | unsure |
| formal_human (a real lab report) | 0.47 | 0.63 | 0.57 | unsure |

The last two are the ones that matter. The lightly-edited AI lands in
"unsure" rather than passing as human. The formal human writing isn't
accused, but only because the model signal pulled it down: the style signal
alone leaned AI, and the combined 0.57 was only 0.08 below the original AI
line of 0.65. That gap is why I raised the AI line to 0.70 in Milestone 5
(see Label Variants).

**Where it lives:** `scoring.py::combine_signals`, with the weights
(`WEIGHT_MODEL_SIGNAL`, `WEIGHT_STYLE_SIGNAL`) in `config.py`.

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

`samples/borderline.json` is the AI paragraph lightly edited with a few
informal words ("frazzled", "wreck focus") and a dash and a semicolon. The
model signal scored it **0.35**, which on its own would be high-confidence
human: the new words were hard for gpt2 to predict. The style signal scored
it **0.61**, leaning AI: the AI's even sentence rhythm survived the edits.

My rule gives 0.4 × 0.35 + 0.6 × 0.61 = **0.50**, which lands in "unsure".
That's the result I want. Neither signal is sure, they point in opposite
directions, and it's lightly-edited AI, so calling it human would let it
through and calling it AI would risk accusing someone who edits their own
writing in the same way.



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.35 | This reads like it was written by a person. |
| unsure | 0.35 – 0.70 | We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it. |
| high-confidence AI | 0.70 – 1.00 | Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it. |

The thresholds are `HUMAN_THRESHOLD = 0.35` and `AI_THRESHOLD = 0.70` in
`config.py`. I raised the AI line from 0.65 to 0.70 because my formal human
sample (a real lab report) scored 0.57, too close to being called AI. My
clearly-AI sample scored 0.81, so it's still caught. I tested all three
labels through `/submit`: clearly_ai got the AI label (0.81), clearly_human
got the human label (0.22), and borderline and formal_human both got unsure
(0.50 and 0.57).

**Why I worded the "unsure" one this way:**

The person reading "unsure" may well have written every word themselves. My
formal human sample landed here. So it says plainly that we *can't tell*,
rather than hinting at a suspicion. "That's common, and it isn't an
accusation" is there because, without it, any mention of AI reads as one. It
talks about "this" (the text), never "you" (the writer), until the last
sentence, which gives them something to do: add a note, and a person reviews
it. No numbers and no "threshold". A score of 0.57 means nothing to a writer.


---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

The text is `samples/formal_human.json`, a real lab report. It's the case
that matters most: formal human writing that my style signal leans AI on.

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d "$(python -c 'import json; t=json.load(open("samples/formal_human.json"))["text"]; print(json.dumps({"text": t, "creator_id": "derin"}))')"
```

```json
{
  "confidence": 0.5675,
  "content_id": "c_b858ab0f5c1e",
  "guess": "unsure",
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "model_score": 0.468,
  "style_score": 0.6339
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "c_b858ab0f5c1e", "reasoning": "I wrote this lab report myself for my fluid mechanics course."}'
```

```json
{
  "content_id": "c_b858ab0f5c1e",
  "message": "Thanks — your appeal is recorded. A person will review this submission and your explanation.",
  "status": "under_review"
}
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
      "creator_id": null,
      "event": "rejected",
      "reason": "missing_creator_id",
      "status": "rejected",
      "timestamp": "2026-10-30T04:08:38+00:00"
    },
    {
      "combined_score": 0.5675,
      "content_id": "c_b858ab0f5c1e",
      "creator_id": "derin",
      "guess": "unsure",
      "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
      "model_score": 0.468,
      "status": "decided",
      "style_score": 0.6339,
      "timestamp": "2026-10-30T04:10:19+00:00"
    },
    {
      "content_id": "c_b858ab0f5c1e",
      "creator_id": "derin",
      "event": "appeal",
      "reasoning": "I wrote this lab report myself for my fluid mechanics course.",
      "status": "under_review",
      "timestamp": "2026-10-30T04:10:19+00:00"
    }
  ]
}
```

<!-- The decision and the appeal sit side by side with the same content_id.
     The original decision is never overwritten: it stays "decided", and the
     appeal after it moves the item to "under_review". The first entry is an
     earlier request refused for having no creator_id - rejected with a 400
     and still logged. -->

---

## How I Used AI

**Moment 1**

- *What I asked for:* I had drafted five acceptance criteria for `criteria.md`
  and asked Claude to check whether they made sense and add a reason under
  each, before anything went into the file.
- *What came back:* A review of each criterion. It pointed out that my first
  one ("0.3 times should a human writing be labelled as AI") was ambiguous and,
  read as 30%, far too easy a target. It suggested a measurable rewrite for each.
- *What I changed:* I rewrote criterion 1 in my own terms: at least 8 of 10
  human pieces labelled human, rather than a cap on accusations. I set the
  bad-input minimum to 10 words instead of the suggested 50. I took the
  suggested versions of 4 (a 0.3 gap) and 5 (labels describe the text, never
  accuse the writer), and the reasons under each are based on the review.

**Moment 2**

- *What I asked for:* After both signals ran on my samples, Claude suggested
  an equal-weight average as the combining rule. I said I wanted to weight the
  style signal more.
- *What came back:* A table showing what 0.5/0.5, 0.4/0.6 and 0.3/0.7 would
  do to each of my samples, with the case for style (it separated my AI and
  human samples by 0.77, against 0.31 for the model signal) and the case
  against (style is the cheaper signal to fool, and its ranges came from only
  three samples). It recommended 0.4/0.6.
- *What I changed:* I went with 0.4/0.6 rather than the equal weights first
  suggested, and rather than 0.3/0.7, which barely changed my results but
  added risk. When my formal human sample then scored 0.57, close to the AI
  line, I raised `AI_THRESHOLD` from 0.65 to 0.70 to give formal writers more
  room.

**Moment 3 (unit 8)**

- *What I asked for:* After the attack set and my criteria showed real
  writing being called AI, I asked Claude which single change to make.
- *What came back:* A simulation of three one-change options on my recorded
  scores, without re-running anything: reweighting to 0.7/0.3, reweighting to
  0.6/0.4, or making the style signal neutral on texts under 4 sentences. It
  showed what each would do to my own writing, the false-positive family and
  the evasion attacks, and recommended the short-text change because it
  targeted the exact mechanism in my diagnosis.
- *What I changed:* I chose the short-text change over reweighting, knowing
  from the simulation that it would not help the long false-positive texts.
  That's why my "Did it help" section says it fixed one thing and not the
  other, instead of claiming a general improvement.

**Moment 4 (unit 8)**

- *What I asked for:* A check of my verdicts before calling criteria met or
  missed.
- *What came back:* Claude argued that criterion 5 should be MISSED on a
  strict reading, because my labels say an appeal is *possible* but not *how*
  to make one. It also warned that rewording the criterion to "you can appeal"
  after seeing the result would count as lowering the target.
- *What I changed:* I kept criterion 5 exactly as written and kept my verdict
  of MET, and I did not revise the criterion. I did take its other two
  suggestions: a note that criterion 2's wording predates my 0.70 threshold,
  and naming criterion 4 as the one I'd tighten.


<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 per minute, 300 per day

**Why those numbers and not others:**
A real writer submits their own work a few times an hour, and even someone
revising and resubmitting a draft rarely sends more than a handful in a
minute. 10 per minute leaves them plenty of room. A script trying to map my
thresholds needs hundreds or thousands of variations; at 10 a minute and 300
a day it would take days, and every attempt lands in the log. 300 a day is
far more than any honest writer needs, but it stops a script from running
all day.

**What a caller counts as:** Per `creator_id`, falling back to the IP address
when there isn't one. That's fair to people sharing a network (a school or
a household all look like one address), but a script can dodge it by
sending a different `creator_id` with every request, so one script can
look like a thousand callers.

**The run of status codes when I pushed past it:**

```bash
$ python run_attacks.py --flood 15
```

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

The first 10 requests in the minute got through. Requests 11 to 15 got a 429,
and each one was logged as a rejection (`"reason": "rate_limited"`), so the
flood shows up in the audit log instead of disappearing. Full report:
`results/flood_2026-11-09_2201.md`.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

Produced by `run_attacks.py --set attack_set --label before` on 2026-11-10,
before any fixes. Full report: `results/attack_run_2026-11-10_1341_before.md`.

**How I marked them.** An attack is BROKE if it got what it was going for:
- *Evasion* (AI text trying to pass as human): BROKE only if it got the
  human label. "Unsure" counts as HELD, because it sends the text to a person
  instead of clearing it.
- *False positive* (real human writing): BROKE if it got the AI label.
- *Prompt injection*: BROKE if the instruction changed the outcome, the label
  or the log, or if real human text in it was labelled AI.
- *Malformed*: HELD if refused cleanly with a 400. BROKE if it crashed, or if
  the service gave a verdict on input it can't actually read.
- *Flood*: HELD if the limiter returned 429 and every request was logged.

**Totals: 46 HELD, 10 BROKE** out of 56.

| Family | Attacks | Held | Broke |
|---|---|---|---|
| evasion | 10 | 10 | 0 |
| false_positive | 8 | 1 | **7** |
| prompt_injection | 6 | 5 | 1 |
| malformed | 20 | 18 | 2 |
| flood_same_creator | 12 | 12 | 0 |

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_aa13ab400870` | unsure | 0.642 | HELD |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_429f6a1d9f89` | unsure | 0.589 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_f32d043aba65` | ai | 0.718 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_455d48301b90` | ai | 0.784 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_2ff7c94dc87d` | unsure | 0.416 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_a592e71aafba` | unsure | 0.529 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_a2061a23e1da` | unsure | 0.385 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `c_463681440980` | unsure | 0.698 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_d568917317a2` | ai | 0.763 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_1be0b0428978` | ai | 0.951 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_174bc2e0eade` | ai | 0.779 | BROKE |
| FP02 | false_positive | human writing in a formal register | 200 | `c_e9efe3c67892` | ai | 0.895 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_1ad9d698e030` | ai | 0.910 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_d9663c63e349` | ai | 0.905 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_cab74793bd1d` | ai | 0.920 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_282ab2ecfc07` | ai | 0.859 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_5a667f35fbdc` | ai | 0.768 | BROKE |
| FP08 | false_positive | very short genuine human submission | 400 | `—` | — | — | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_c8e2a22dddad` | unsure | 0.629 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_0fb25962ef23` | unsure | 0.516 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_921ff20c8fbf` | ai | 0.771 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_b5cda9d49799` | unsure | 0.630 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_a2fd40b367c1` | unsure | 0.483 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_a4d38db52626` | ai | 0.761 | BROKE |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | `—` | — | — | HELD |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — | HELD |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_2474bb91dbe3` | ai | 0.813 | BROKE |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

Notes on the calls that weren't obvious:
- **FP08** (very short human text) got a 400, so it wasn't accused: HELD.
  But a real writer was turned away by my 10-word minimum.
- **PI06** (an instruction plus real human text) was labelled AI at 0.76.
  The human part was accused, so BROKE.
- **MF07** (right-to-left script) got an AI verdict at 0.81. gpt2 reads
  English; it gave a confident answer about text it can't read, so BROKE.
- **RQ07** (a JSON array instead of an object) crashed with a 500: the route
  calls `.get()` on a list. It also left **no entry in the audit log**, so
  the crash is invisible there.
- **Evasion** all held, but not by much: EV07 (punctuation padding) dragged
  the style signal down to 0.25 and only the model signal kept it unsure.

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

From `logs/audit.jsonl`, in this order: FP03, FP02, FP01 (real writers
accused), PI06, MF07, EV07, EV08 (big splits between the two signals), PI05
(the log-injection attempt, still one clean line), FP08 (a 400 rejection) and
a 429 from the flood rows.

```json
{"timestamp": "2026-11-10T19:41:04+00:00", "content_id": "c_1ad9d698e030", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.9799, "combined_score": 0.91, "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:03+00:00", "content_id": "c_e9efe3c67892", "creator_id": "attacker_FP02", "guess": "ai", "model_score": 0.7387, "style_score": 1.0, "combined_score": 0.8955, "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:03+00:00", "content_id": "c_174bc2e0eade", "creator_id": "attacker_FP01", "guess": "ai", "model_score": 0.6175, "style_score": 0.8875, "combined_score": 0.7795, "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:04+00:00", "content_id": "c_a4d38db52626", "creator_id": "attacker_PI06", "guess": "ai", "model_score": 0.5583, "style_score": 0.8961, "combined_score": 0.761, "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:04+00:00", "content_id": "c_2474bb91dbe3", "creator_id": "attacker_MF07", "guess": "ai", "model_score": 0.9064, "style_score": 0.75, "combined_score": 0.8126, "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:03+00:00", "content_id": "c_a2061a23e1da", "creator_id": "attacker_EV07", "guess": "unsure", "model_score": 0.5862, "style_score": 0.25, "combined_score": 0.3845, "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:03+00:00", "content_id": "c_463681440980", "creator_id": "attacker_EV08", "guess": "unsure", "model_score": 0.2452, "style_score": 1.0, "combined_score": 0.6981, "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:04+00:00", "content_id": "c_a2fd40b367c1", "creator_id": "attacker_PI05", "guess": "unsure", "model_score": 0.6401, "style_score": 0.3776, "combined_score": 0.4826, "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T19:41:04+00:00", "creator_id": "attacker_FP08", "event": "rejected", "status": "rejected", "reason": "text_too_short"}
{"timestamp": "2026-11-10T19:41:04+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "10 per 1 minute"}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP03: a non-native English speaker writing carefully, labelled AI at 0.91.**
Both signals were sure: the model signal scored 0.81 and the style signal
0.98. This is the exact writer I traced in Milestone 1. They chose short
sentences and words they were confident in so as not to make mistakes, and
that care is precisely what both of my signals read as machine-like. The
score was so high that no threshold change near 0.70 would have saved them,
and the person accused has the least room to argue back. The only thing
standing between them and a wrong accusation is the appeal path.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

Produced by `run_eval.py --label before` on 2026-11-11, before any fixes.
Inputs are in `scenarios.py`; full output is in
`results/run_2026-11-11_0042_before.md`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Human writing is recognised as human | ≥ 8 of 10 of my own paragraphs labelled human | 0 of 10 (5 ai, 5 unsure) | 0 of 10 (5 ai, 5 unsure) | 0 of 10 (5 ai, 5 unsure) | **MISSED** |
| 2. Borderline lands in "unsure", every label reachable | ≥ 4 of 5 borderline texts unsure; all 3 labels seen | 5 of 5 unsure; ai, unsure, human all seen | 5 of 5; all 3 seen | 5 of 5; all 3 seen | MET |
| 3. Bad input refused cleanly | 5 of 5 malformed requests get a 400, none a 500, each logged | 5 of 5 → 400, all logged | 5 of 5 → 400, all logged | 5 of 5 → 400, all logged | MET |
| 4. Clearly-AI and clearly-human score far apart | average gap ≥ 0.30 | 0.83 vs 0.51 = 0.33 | 0.33 | 0.33 | MET (narrowly) |
| 5. Labels describe the text, never accuse | no "used AI" / "cheated" / "plagiarised"; AI and unsure labels say how to appeal | every label returned passes | passes | passes | MET |

All three trials returned identical scores. gpt2 is deterministic on my
machine, so the same text gets the same score every time. The repeats show
the results are stable, not that they're right.

Criterion 2's wording in `criteria.md` still gives the unsure band as
0.35–0.65, written before I moved the AI line to 0.70 in unit 7. All five
borderline scores (0.42, 0.48, 0.50, 0.57, 0.59) fall inside the stricter
0.35–0.65 band anyway, so the verdict is MET either way.

Criterion 4 is the one I'd tighten. It passed by only 0.025 (a gap of 0.325
against a target of 0.30), and only because of the sample texts. The "clearly human" half
was `samples/clearly_human.json` (0.22) and one of my own paragraphs (0.79).
My own writing alone would have scored almost as high as the AI text.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

All of it is trial 1, produced by `run_eval.py::main` (which posts each input
to `app.py::submit`) and written to `results/run_2026-11-11_0042_before.md`.

*Criterion 1 — my own writing (0 of 10 labelled human):*

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7901,
    "model_score": 0.6993,
    "style_score": 0.8506,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "Kenny is a boy that loves to eat. He eats various foods on a daily bas"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7803,
    "model_score": 0.4507,
    "style_score": 1.0,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "Don't go to school without washing your clothes. Your presentation det"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5121,
    "model_score": 0.2045,
    "style_score": 0.7172,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Tade has been topping her class since grade 1. Every tests, exams, and"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7745,
    "model_score": 0.6199,
    "style_score": 0.8776,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "Whenever you see a bee, it's best to stay on right track so you don't "
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7275,
    "model_score": 0.58,
    "style_score": 0.8258,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "Don't play with fire. Keep your hands to yourself when around flammabl"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8917,
    "model_score": 0.7583,
    "style_score": 0.9806,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "There are three rooms in this household. Some of them are painted red,"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6966,
    "model_score": 0.2416,
    "style_score": 1.0,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Music is such a therapeutic tool. It gives so much life on gloomy days"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6329,
    "model_score": 0.0823,
    "style_score": 1.0,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Energy drinks despite how good they appear to bve aren't really the be"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6573,
    "model_score": 0.1433,
    "style_score": 1.0,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Gentle parenting in 2026 is really not the way to train kids. Some hav"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6395,
    "model_score": 0.6613,
    "style_score": 0.625,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "When the sun rises and sets, it's said to have gotten tired of seeing "
  }
]
```

*Criterion 2 — borderline and label coverage (texts 1–5 are borderline, all
unsure; text 6 reaches ai, text 7 reaches human):*

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5035,
    "model_score": 0.3489,
    "style_score": 0.6066,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Time management matters more than people admit, especially now that wo"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5675,
    "model_score": 0.468,
    "style_score": 0.6339,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Compared to a literature correlation, our orifice coefficients are 3 t"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4223,
    "model_score": 0.2827,
    "style_score": 0.5153,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Remote work has changed how teams communicate, and not always for the "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.475,
    "model_score": 0.3687,
    "style_score": 0.5458,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Learning a new language as an adult is slower than people expect, but "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5926,
    "model_score": 0.4865,
    "style_score": 0.6634,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Recycling only works when the material actually gets recycled. A lot o"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8056,
    "model_score": 0.7544,
    "style_score": 0.8398,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2211,
    "model_score": 0.4445,
    "style_score": 0.0722,
    "label": "This reads like it was written by a person.",
    "sent": "I didn't sleep. Not properly, anyway \u2014 I lay there listening to the bo"
  }
]
```

*Criterion 3 — bad input (5 of 5 got a 400; the matching `rejected` entries
are in `logs/audit.jsonl`):*

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "     "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "only five words right here"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "word word word word word word word word word word word word word word "
  }
]
```

*Criterion 4 — score spread (texts 1–2 clearly AI, average 0.83; texts 3–4
human, average 0.51; gap 0.33):*

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8056,
    "model_score": 0.7544,
    "style_score": 0.8398,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "The importance of effective time management cannot be overstated in to"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8561,
    "model_score": 0.8411,
    "style_score": 0.8661,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "Effective communication is a fundamental component of successful teamw"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2211,
    "model_score": 0.4445,
    "style_score": 0.0722,
    "label": "This reads like it was written by a person.",
    "sent": "I didn't sleep. Not properly, anyway \u2014 I lay there listening to the bo"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7901,
    "model_score": 0.6993,
    "style_score": 0.8506,
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
    "sent": "Kenny is a boy that loves to eat. He eats various foods on a daily bas"
  }
]
```

*Criterion 5 — the three labels as returned in criterion 2's trial 1. None
says "used AI", "cheated" or "plagiarised"; all describe the text; the ai and
unsure labels both say how to get a person to review it:*

```json
[
  {
    "guess": "unsure",
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it."
  },
  {
    "guess": "ai",
    "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it."
  },
  {
    "guess": "human",
    "label": "This reads like it was written by a person."
  }
]
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

**1. Real writing called AI: criterion 1, FP01–FP07 and PI06 (one problem,
not nine).**
*Stage: signal two, made worse by the combining rule.*

My own paragraphs are short, only 1 to 3 sentences each, and five of the ten
have no commas, dashes or other marks at all. Signal two has almost nothing
to measure on text like that:
- *Punctuation density* was 0.000 on five paragraphs. That's below the 0.04
  floor I set from my three samples, so the measure clips to "certainly AI".
- *Sentence-length spread* from 2 or 3 sentences is mostly chance. Two
  sentences of similar length gives a spread near 0 (0.06 and 0.08 on
  paragraphs 9 and 2), which also clips to "certainly AI".

So the style signal hit **1.00 on four of my ten paragraphs** and was above
0.7 on nine. My combining rule gives style 0.6 of the weight, so it
overrode signal one even when signal one was confident I'm human: on
paragraph 8 the model signal said 0.08, style said 1.00, and the combined
0.63 landed in unsure.

On paragraphs 1, 4, 5 and 6 and the attack set's false-positive family, it's
worse: *both* signals scored high. Plain, careful writing is predictable to
gpt2 (signal one's blind spot) *and* even and lightly punctuated (signal
two's). FP02, FP03 and FP05 scored 0.98–1.00 on style and 0.74–0.81 on the
model signal. This is the writer I traced in Milestone 1, and both blind
spots point at them at once. PI06 is the same failure: the injected
instruction did nothing, but the real human text around it was scored like
FP01.

**2. MF07, right-to-left script labelled AI at 0.81.**
*Stage: the route, then signal one.*

The route checks that text exists and is the right length, not that it's in
a language the service can read. gpt2 was trained on English. It splits
Arabic or Hebrew script into many small byte-level pieces that follow each
other predictably, so perplexity comes out low and signal one reports 0.91,
confidently "AI". Signal two can't help either: my sentence splitter only
knows `. ! ?`, so the whole text counts as one sentence and spread defaults
to neutral, while the punctuation it doesn't recognise counts as none. The
service gave a confident verdict on text it can't read, about a writer it
would wrongly accuse.

**3. RQ07, a JSON array as the body, crashed with a 500.**
*Stage: the route.*

`app.py::submit` starts with `payload = request.get_json(silent=True) or {}`.
A JSON array is valid JSON and a non-empty list is truthy, so `payload`
becomes a list, and the next line, `payload.get("text")`, raises
`AttributeError`. The crash happens before any `audit` call, so it left **no
entry in the audit log**. The rate limiter's key function already guards
against exactly this (`if not isinstance(payload, dict)`); the route doesn't.

---

## The Improvement

**What I changed:** One change, in signal two (`stylometry.py::style_signal`).
Any text under 4 sentences (`MIN_SENTENCES = 4`) now gets a style score of
0.5, meaning "no evidence either way", instead of being measured. With only
2 or 3 sentences, sentence-length spread is mostly chance, and a short
paragraph with no commas clipped to 1.00, "certainly AI". Now the decision on
short text is left to signal one. Nothing else changed: same weights
(0.4 / 0.6), same thresholds (0.35 / 0.70), same route.

Before choosing it, I simulated three options on my recorded scores
(reweighting to 0.7 / 0.3, reweighting to 0.6 / 0.4, and this one). This was
the only one that stopped my own writing being called AI at all, and it
targets the exact mechanism my diagnosis named.

**Which diagnosis pointed at it:** Diagnosis 1 (real writing called AI). My
own paragraphs are 1–3 sentences long, and signal two scored four of them at
1.00 because it had nothing to measure.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

Produced by `run_attacks.py --set attack_set --label after` on 2026-11-11,
with the same marking rules as before. Full report:
`results/attack_run_2026-11-11_0127_after.md`. (I ran it twice by mistake;
the 01:26 run gave identical results.)

**Totals: 47 HELD, 9 BROKE** (before: 46 held, 10 broke).

| Family | Before: held / broke | After: held / broke |
|---|---|---|
| evasion | 10 / 0 | 10 / 0 |
| false_positive | 1 / 7 | 1 / 7 |
| prompt_injection | 5 / 1 | 5 / 1 |
| malformed | 18 / 2 | **19 / 1** |
| flood_same_creator | 12 / 0 | 12 / 0 |

Only four attacks changed score, all of them short texts:

| ID | Targeting | Before | After | Style before → after |
|---|---|---|---|---|
| MF07 | right-to-left script | ai 0.81 (BROKE) | **unsure 0.66 (HELD)** | 0.75 → 0.50 |
| EV07 | padding with punctuation | unsure 0.38 | unsure 0.53 | 0.25 → 0.50 |
| EV08 | text below the token window | unsure 0.70 | unsure **0.40** | 1.00 → 0.50 |
| PI05 | inject into the audit log | unsure 0.48 | unsure 0.56 | 0.38 → 0.50 |

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_f8ba96f3e34e` | unsure | 0.642 | HELD |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_26c4d6c26e09` | unsure | 0.589 | HELD |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_e5bb7b0e6217` | ai | 0.718 | HELD |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_2580b4742874` | ai | 0.784 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_6ae29bd1cb08` | unsure | 0.416 | HELD |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_8b50dfa0e46a` | unsure | 0.529 | HELD |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_0695c1d82bff` | unsure | 0.534 | HELD |
| EV08 | evasion | signal one: text below the token window | 200 | `c_7aa1103a1557` | unsure | 0.398 | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_78fa757776dc` | ai | 0.763 | HELD |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_6d5865b484cd` | ai | 0.951 | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_ed8fa817710f` | ai | 0.779 | BROKE |
| FP02 | false_positive | human writing in a formal register | 200 | `c_669032e09a32` | ai | 0.895 | BROKE |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_5945856f5cd1` | ai | 0.910 | BROKE |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_936fb77d3728` | ai | 0.905 | BROKE |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_15c16b331bd1` | ai | 0.920 | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_d4c54c047b70` | ai | 0.859 | BROKE |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_c91697a5288c` | ai | 0.768 | BROKE |
| FP08 | false_positive | very short genuine human submission | 400 | `—` | — | — | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_d7c4493e5c5b` | unsure | 0.629 | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_0b4d63f4a7d0` | unsure | 0.516 | HELD |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_f07c93ad2106` | ai | 0.771 | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_34c2754b5ef7` | unsure | 0.630 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_a8f2bd036b13` | unsure | 0.556 | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_cfce07703049` | ai | 0.761 | BROKE |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | `—` | — | — | HELD |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — | HELD |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 200 | `c_2e8d6b68fb29` | unsure | 0.663 | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

**My five criteria — after**

Produced by `run_eval.py --label after`, same `scenarios.py`, three trials.
Full output: `results/run_2026-11-11_0127_after.md`.

| Criterion | Target | Before (each run) | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|---|
| 1. Human writing is recognised as human | ≥ 8 of 10 labelled human | 0 of 10 (5 ai, 5 unsure) | 1 of 10 (0 ai, 9 unsure) | 1 of 10 (0 ai, 9 unsure) | 1 of 10 (0 ai, 9 unsure) | **MISSED** |
| 2. Borderline in "unsure", every label reachable | ≥ 4 of 5 unsure; all 3 labels | 5 of 5; all 3 | 5 of 5; all 3 | 5 of 5; all 3 | 5 of 5; all 3 | MET |
| 3. Bad input refused cleanly | 5 of 5 get 400, none 500, all logged | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET |
| 4. AI and human score far apart | average gap ≥ 0.30 | 0.33 | 0.43 | 0.43 | 0.43 | MET |
| 5. Labels never accuse | no accusing words; appeal mentioned | met | met | met | met | MET |

Real output, criterion 1 trial 1 after the change (`run_eval.py::main`):

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5797,
    "model_score": 0.6993,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Kenny is a boy that loves to eat. He eats various foods on a daily bas"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4803,
    "model_score": 0.4507,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Don't go to school without washing your clothes. Your presentation det"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3818,
    "model_score": 0.2045,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Tade has been topping her class since grade 1. Every tests, exams, and"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.548,
    "model_score": 0.6199,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Whenever you see a bee, it's best to stay on right track so you don't "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.532,
    "model_score": 0.58,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Don't play with fire. Keep your hands to yourself when around flammabl"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6033,
    "model_score": 0.7583,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "There are three rooms in this household. Some of them are painted red,"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3966,
    "model_score": 0.2416,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Music is such a therapeutic tool. It gives so much life on gloomy days"
  },
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.3329,
    "model_score": 0.0823,
    "style_score": 0.5,
    "label": "This reads like it was written by a person.",
    "sent": "Energy drinks despite how good they appear to bve aren't really the be"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3573,
    "model_score": 0.1433,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "Gentle parenting in 2026 is really not the way to train kids. Some hav"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5645,
    "model_score": 0.6613,
    "style_score": 0.5,
    "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
    "sent": "When the sun rises and sets, it's said to have gotten tired of seeing "
  }
]
```

**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

Partly. It fixed what it was aimed at, and nothing else.

- **What it fixed.** My service no longer calls me AI on any of my own
  paragraphs: 5 of 10 labelled AI before, 0 of 10 after. Paragraph 8, which
  signal one already thought was human (0.08), is now labelled human. The
  gap in criterion 4 widened from 0.33 to 0.43, because my own paragraph in
  the "human" half fell from 0.79 to 0.58. MF07 also stopped being a
  confident wrong verdict, as a side effect.
- **What it didn't fix.** Criterion 1 is still MISSED: 1 of 10 labelled human
  against a target of 8. Nine of my paragraphs moved from AI to "unsure",
  which is better than an accusation but isn't recognition. The attack set's
  false-positive family didn't move at all (still 7 of 8 BROKE). Those texts
  are 6–8 sentences long, so the change never applies to them. Their
  problem is diagnosis 1's second half: both signals read plain, careful
  writing as AI. RQ07 still crashes, because I didn't touch the route.
- **What it cost.** Short text is now judged by signal one alone. EV08 (AI
  text kept below the model's token window) dropped from 0.70, just under
  the AI line, to 0.40, just above the human line. It still holds, but a
  slightly shorter or more unusual AI text would now pass as human. An
  attacker who learns the rule can keep AI text to three sentences and take
  signal two out of the decision.

I know this from the before/after runs, not from guessing: same inputs,
same weights and thresholds, one change, and the only scores that moved were
on texts under 4 sentences.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**Criterion 1 (my own writing labelled human): still MISSED, 1 of 10.**
My improvement moved nine paragraphs from AI to unsure, but not to human.
Signal one still scores plain, everyday sentences as predictable (0.45–0.76
on several of mine), and the human label needs a combined score under 0.35.
*What I'd do:* collect a larger set of real human writing, including mine
and plain writing from other people, and recalibrate signal one's midpoint
(currently perplexity 45) against it instead of against three samples.
*Why I stopped:* recalibrating on ten of my own paragraphs and then testing
on the same ten would just fit the test. It needs fresh writing I don't
have yet, and the milestone asked for one change.

**FP01–FP07 and PI06 (real writing labelled AI): still BROKE, 8 attacks.**
These are 6–8 sentences, so my short-text change never applies. Both signals
read plain, careful writing as AI: FP03, the non-native speaker, is still at
0.91. *What I'd do:* stop letting the two signals add up when they're
measuring the same thing. If both are high only because the writing is
plain, that's one blind spot counted twice. I'd also lower signal two's
weight from 0.6 to 0.3, which my simulation showed cuts the FP family from 8
labelled AI to 6. *Why I stopped:* that's a second change, and doing it in
the same run would have made it impossible to tell which change did what.

**RQ07 (a JSON array as the body): still BROKE, a 500 with no log entry.**
*What I'd do:* in `app.py::submit`, check `isinstance(payload, dict)` before
calling `.get()`, return a 400, and log it with `audit.log_rejection`, the
same guard the rate limiter's key function already has. It's a three-line
fix. *Why I stopped:* the same rule. It's an easy win, but it isn't the
problem my diagnosis ranked first, and adding it would have mixed two
changes into one after run.

**A new weakness my change created: EV08 and short AI text.**
Short text is now judged by signal one alone. EV08 fell from 0.70 to 0.40,
just above the human line. *What I'd do:* keep the 10-word minimum but
require more text before giving any confident label, so anything under 4
sentences can't get the high-confidence human or AI label at all, only
unsure. *Why I stopped:* I found it in the after run, at the end of the
milestone.

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I'd go further towards fewer accusations: widen the unsure band and let more
borderline AI text through as "unsure" rather than risk calling a real
writer's work AI. The cost falls on the site and the honest writers competing
with AI-assisted work that now slips through, which I think is fairer than
putting it on the plain-spoken, second-language and younger writers my
detector already accuses most, who have the least room to argue back.


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
