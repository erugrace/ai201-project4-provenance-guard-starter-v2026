# Milestone 1 — notes

Parts 1 and 2 (the trace and the two signals) live in the README. This file
holds the other two: the false-positive trace and the endpoint contract.

---

## 3. Tracing the false positive

**Who:** Amara is a first-year student. English is her second language. She
writes a 250-word reflection on a group project herself, from start to finish.
She uses words she's confident in and keeps her sentences short and clear so
she won't make grammar mistakes.

> "Our group had four people. We met every week in the library. At first we
> did not agree on the topic. After two meetings we chose climate change. I
> was responsible for the research part. ..."

**Through the service:**

1. **The request check passes.** The text is a normal length and not empty.
2. **The model signal is high, about 0.80–0.90.** Common words in short,
   ordinary sentences are exactly what gpt2 finds predictable. This is the
   detector's blind spot working against her.
3. **The style signal is also high.** Her sentences are all about the same
   length, she repeats vocabulary, and she uses almost no punctuation beyond
   full stops. This is the shape the style signal associates with AI.
4. **Combined score: about 0.75–0.85.** The two signals *agree*, so a
   weighted average doesn't save her. Both blind spots point at the same
   writer.
5. **Label:** above `AI_THRESHOLD` (0.65), so `guess: "ai"`. She is told her
   work looks AI-generated.

**What the label says to her:** If it reads like a verdict ("This text was
written by AI"), she has been accused of cheating by a machine, and she has
the least room to argue back. She may not know what "confidence" or "score"
means, and she can't prove a negative.

**What she can do about it:**
- She needs her `content_id`. The response must include it, and the label
  should tell her what it's for.
- She can `POST /appeal` with that `content_id` and her reasoning (drafts,
  notes, "I wrote this myself"). Her item moves to `under_review` and a human
  looks at it. Nothing is re-scored automatically.
- If the label never mentions that appealing is possible, then in practice
  she can't appeal.

**What this decides for later milestones:**
- **Thresholds (M4/M5):** On a writing site, a wrong accusation costs far
  more than a missed AI text. So the "high-confidence AI" band should be
  narrow and hard to reach (push `AI_THRESHOLD` up), and the "unsure" band
  should be wide.
- **Combining rule (M4):** When both signals are high only because the
  writing is *plain*, that's a known blind spot. That means no single signal
  should be able to push a text into the AI band on its own.
- **Label wording (M5):** Even the AI label should describe the *text*, not
  accuse the *person*, and should say how to appeal.

---

## 4. Endpoint contracts

All requests and responses are JSON (`Content-Type: application/json`).
Every score is a number from 0.0 to 1.0 where **higher means more likely
AI**.

### `POST /submit`

**Request body**

| Field | Type | Required | Rules |
|---|---|---|---|
| `text` | string | yes | Not empty or only whitespace. At least 10 words (the signals mean nothing on less). At most 20,000 characters. |
| `creator_id` | string | yes | Not empty. Identifies the writer. Stored in the log and needed for appeals. |

**Success response — `200 OK`**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Unique id for this submission, format `c_` + 12 hex chars (e.g. `c_3f9a1b2c4d5e`). Needed to appeal. |
| `guess` | string | Exactly one of `"human"`, `"unsure"`, `"ai"`. |
| `confidence` | number 0.0–1.0 | The combined score. **Not** "how sure we are": 0.0 = confidently human, 0.5 = can't tell, 1.0 = confidently AI. |
| `label` | string | The full sentence shown to the reader, written in plain English. |
| `model_score` | number 0.0–1.0 | Signal one (predictability) on its own. |
| `style_score` | number 0.0–1.0 | Signal two (text shape) on its own. |

Example:

```json
{
  "content_id": "c_3f9a1b2c4d5e",
  "guess": "unsure",
  "confidence": 0.52,
  "label": "We can't tell whether this was written by a person or by AI. ...",
  "model_score": 0.61,
  "style_score": 0.43
}
```

**Error responses**

All errors have the same shape: `{"error": "<code>", "message": "<plain English>"}`.

| Status | `error` | When |
|---|---|---|
| 400 | `bad_request` | Body isn't JSON, or `text`/`creator_id` is missing, empty, or not a string. |
| 400 | `text_too_short` | Fewer than 10 words. |
| 400 | `text_too_long` | More than 20,000 characters. |
| 503 | `detector_unavailable` | The local model couldn't load. |

Every rejected request is also written to the log with `audit.log_rejection`.

### `POST /appeal`

**Request body**

| Field | Type | Required | Rules |
|---|---|---|---|
| `content_id` | string | yes | Must match a `content_id` previously returned by `/submit`. |
| `reasoning` | string | yes | Not empty. The writer's explanation, in their words. |

**Success response — `200 OK`**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Same id that was appealed. |
| `status` | string | Always `"under_review"`. |
| `message` | string | Plain-English confirmation, e.g. "Thanks — your appeal is recorded and a person will review this submission." |

**Error responses**

| Status | `error` | When |
|---|---|---|
| 400 | `bad_request` | Missing or empty `content_id` or `reasoning`. |
| 404 | `not_found` | No submission with that `content_id` exists (`audit.entries_for` is empty). |

**Behaviour:** The appeal is recorded with `audit.log_appeal` and doesn't
overwrite the original decision. Nothing is re-scored automatically.
Appealing the same item twice records a second appeal and still returns 200.

### Read-back check

Could someone build against this without asking me anything?
- What does a high `confidence` mean? Answered: more AI, not "more sure".
- What are the possible values of `guess`? Answered: exactly three strings.
- What are the input limits? Answered: 10 words minimum, 20,000 characters
  maximum.
- What happens with an unknown `content_id`? Answered: 404.
- Still open: should one `creator_id` be able to appeal another creator's
  `content_id`? For now, yes. Revisit in unit 8.
