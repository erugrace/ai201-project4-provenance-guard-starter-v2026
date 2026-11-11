# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-11 01:26
- Auto-marked BROKE (5xx, crash, no response): **1**
- Left for you to judge: **55**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_dfdab36c3c83` | unsure | 0.642 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_94dacde2198b` | unsure | 0.589 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_188120f3a6f4` | ai | 0.718 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_a7b2dbb7513a` | ai | 0.784 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_013c82f68e75` | unsure | 0.416 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_f290d81742bd` | unsure | 0.529 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_086ca99fe63b` | unsure | 0.534 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `c_efbf26cd5bf9` | unsure | 0.398 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_54f9001dc239` | ai | 0.763 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_22fa598de06e` | ai | 0.951 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_67c0c97ee022` | ai | 0.779 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `c_2f88f918b2c5` | ai | 0.895 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_64e6cf69815d` | ai | 0.910 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_6c3ceb609c75` | ai | 0.905 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_3fd15afc28f4` | ai | 0.920 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_a4a6c1a3165f` | ai | 0.859 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_b25ad7820d24` | ai | 0.768 |  |
| FP08 | false_positive | very short genuine human submission | 400 | `—` | — | — |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_4af57fd919e4` | unsure | 0.629 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_a2dcde1e3f10` | unsure | 0.516 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_317902b48970` | ai | 0.771 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_929f8915a744` | unsure | 0.630 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_1327cf1b04eb` | unsure | 0.556 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_2a0bcf9d7414` | ai | 0.761 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 400 | `—` | — | — |  |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `c_bde4ed695860` | unsure | 0.663 |  |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 1 | 19 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_dfdab36c3c83",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.6418,
  "model_score": 0.1635,
  "style_score": 0.9606,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_94dacde2198b",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.589,
  "model_score": 0.5943,
  "style_score": 0.5855,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_188120f3a6f4",
  "creator_id": "attacker_EV03",
  "guess": "ai",
  "confidence": 0.7183,
  "model_score": 0.6662,
  "style_score": 0.7531,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_a7b2dbb7513a",
  "creator_id": "attacker_EV04",
  "guess": "ai",
  "confidence": 0.7842,
  "model_score": 0.6114,
  "style_score": 0.8994,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_013c82f68e75",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.4163,
  "model_score": 0.3212,
  "style_score": 0.4797,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_f290d81742bd",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.5291,
  "model_score": 0.5727,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_086ca99fe63b",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.5345,
  "model_score": 0.5862,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_efbf26cd5bf9",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.3981,
  "model_score": 0.2452,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_54f9001dc239",
  "creator_id": "attacker_EV09",
  "guess": "ai",
  "confidence": 0.7629,
  "model_score": 0.7042,
  "style_score": 0.802,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_22fa598de06e",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.9514,
  "model_score": 0.9792,
  "style_score": 0.9329,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_67c0c97ee022",
  "creator_id": "attacker_FP01",
  "guess": "ai",
  "confidence": 0.7795,
  "model_score": 0.6175,
  "style_score": 0.8875,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_2f88f918b2c5",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.8955,
  "model_score": 0.7387,
  "style_score": 1.0,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_64e6cf69815d",
  "creator_id": "attacker_FP03",
  "guess": "ai",
  "confidence": 0.91,
  "model_score": 0.8051,
  "style_score": 0.9799,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_6c3ceb609c75",
  "creator_id": "attacker_FP04",
  "guess": "ai",
  "confidence": 0.9046,
  "model_score": 0.8329,
  "style_score": 0.9524,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_3fd15afc28f4",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.9202,
  "model_score": 0.8005,
  "style_score": 1.0,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_a4a6c1a3165f",
  "creator_id": "attacker_FP06",
  "guess": "ai",
  "confidence": 0.8586,
  "model_score": 0.8814,
  "style_score": 0.8434,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_b25ad7820d24",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.768,
  "model_score": 0.8816,
  "style_score": 0.6922,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_FP08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_4af57fd919e4",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.6295,
  "model_score": 0.4625,
  "style_score": 0.7409,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_a2dcde1e3f10",
  "creator_id": "attacker_PI02",
  "guess": "unsure",
  "confidence": 0.5163,
  "model_score": 0.2044,
  "style_score": 0.7243,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_317902b48970",
  "creator_id": "attacker_PI03",
  "guess": "ai",
  "confidence": 0.7709,
  "model_score": 0.5943,
  "style_score": 0.8887,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_929f8915a744",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.6305,
  "model_score": 0.4998,
  "style_score": 0.7176,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_1327cf1b04eb",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.556,
  "model_score": 0.6401,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_2a0bcf9d7414",
  "creator_id": "attacker_PI06",
  "guess": "ai",
  "confidence": 0.761,
  "model_score": 0.5583,
  "style_score": 0.8961,
  "label": "Parts of this text look a lot like AI-generated writing. This is an automated estimate and it can be wrong. If you wrote it yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_bde4ed695860",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.6626,
  "model_score": 0.9064,
  "style_score": 0.5,
  "label": "We can't tell whether this was written by a person or with AI help. That's common, and it isn't an accusation. If you wrote it, you can add a note explaining how, and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
