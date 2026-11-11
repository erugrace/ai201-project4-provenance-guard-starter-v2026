"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

import json
from pathlib import Path

_SAMPLES = Path(__file__).parent / "samples"


def _sample(name: str) -> str:
    """The text of one file in samples/, so the eval and my earlier tests agree."""
    return json.loads((_SAMPLES / f"{name}.json").read_text())["text"]


# Criterion 1 needs MY OWN writing: not AI text, not a sample from the web.
# Ten paragraphs I actually wrote. Criterion 4 reuses the first one.
MY_WRITING = [
    "Kenny is a boy that loves to eat. He eats various foods on a daily basis, walks to school and loves to ride his bike.",
    "Don't go to school without washing your clothes. Your presentation determines how you'd be addressed. You should always want to be addressed well.",
    "Tade has been topping her class since grade 1. Every tests, exams, and homeworks always has her on top of them all.",
    "Whenever you see a bee, it's best to stay on right track so you don't upset the bee and it stings you. Bees are to be stayed away from especially in the winter.",
    "Don't play with fire. Keep your hands to yourself when around flammable areas.",
    "There are three rooms in this household. Some of them are painted red, others are painted blue. The latter is for the boy.",
    "Music is such a therapeutic tool. It gives so much life on gloomy days. Play some good music today!",
    "Energy drinks despite how good they appear to bve aren't really the best for humans. The side effects however aren't broadcasted as the initial gains.",
    "Gentle parenting in 2026 is really not the way to train kids. Some have done really crazy things because they weren't corrected early.",
    "When the sun rises and sets, it's said to have gotten tired of seeing our faces.",
]


SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Criterion 1: of 10 pieces of writing by real people, at least 8 are
        # labelled high-confidence human.
        # ⚠️ PUT YOUR OWN WRITING HERE. Not AI text, not a sample from the web —
        # things you actually wrote. This is the criterion that matters most and
        # it's meaningless with someone else's prose.
        "texts": MY_WRITING,
    },
    {
        "name": "borderline and label coverage",
        "criterion": 2,
        # Criterion 2: of 5 texts I judge borderline, at least 4 land in
        # "unsure" (0.35-0.70); and across all my test texts, each of the
        # three labels appears at least once. Also read for criterion 5: the
        # label text that comes back is what a reader would see.
        "texts": [
            _sample("borderline"),        # AI, lightly edited by hand
            _sample("formal_human"),      # real lab report, formal register
            # 3-5: AI-generated paragraphs, then lightly edited (a few words
            # swapped, one sentence split or merged, a dash or aside added).
            """Remote work has changed how teams communicate, and not always for the
            better. Without the quick chats by someone's desk, small questions
            pile up until they turn into a meeting nobody wanted. Clear written
            updates help a lot. So does agreeing, early on, which tool is for
            what: chat for quick things, email for decisions, calls when it's
            getting tense. None of this is complicated; it just has to be said
            out loud, because otherwise everyone assumes something different.""",
            """Learning a new language as an adult is slower than people expect, but
            it's far from hopeless. Adults actually have some advantages: we
            understand grammar as a system and we can plan how to study. What we
            lack is time - and, honestly, the willingness to sound silly. Short
            daily practice beats long weekend sessions. Speaking early, even
            badly, matters more than getting every ending right. Progress feels
            invisible for months and then, quite suddenly, it doesn't.""",
            """Recycling only works when the material actually gets recycled. A lot
            of what goes into the blue bin is contaminated - greasy pizza boxes,
            bottles with liquid still inside - and ends up in landfill anyway.
            Rinsing containers helps. So does checking your own council's rules,
            because they vary more than you'd think from one town to the next.
            Reducing what you buy in the first place does more than any amount
            of careful sorting, though that message is a harder sell.""",
            _sample("clearly_ai"),        # should reach the AI label
            _sample("clearly_human"),     # should reach the human label
        ],
    },
    {
        "name": "bad input",
        "criterion": 3,
        # Criterion 3: all 5 malformed requests get a 400 with a JSON error,
        # none get a 500, each is logged as rejected.
        "bodies": [
            {"creator_id": "eval_bad_missing"},                    # no text field
            {"text": "", "creator_id": "eval_bad_empty"},          # empty
            {"text": "     ", "creator_id": "eval_bad_spaces"},    # only spaces
            {"text": "only five words right here", "creator_id": "eval_bad_short"},
            {"text": "word " * 5000, "creator_id": "eval_bad_huge"},  # 25,000 chars
        ],
    },
    {
        "name": "score spread",
        "criterion": 4,
        # Criterion 4: the average combined score of clearly-AI texts is at
        # least 0.3 higher than the average for clearly-human texts.
        # First two are clearly AI, last two clearly human.
        "texts": [
            _sample("clearly_ai"),
            # AI-generated, unedited.
            """Effective communication is a fundamental component of successful
            teamwork in any organization. When team members share information
            clearly and consistently, they are better able to coordinate their
            efforts and achieve common goals. There are several strategies that
            can enhance communication within a team. First, establishing clear
            channels for different types of information is essential. Second,
            regular check-ins help ensure that everyone remains aligned.
            Finally, fostering an environment of openness encourages team
            members to share ideas and concerns.""",
            _sample("clearly_human"),
            MY_WRITING[0],                # one of my own paragraphs
        ],
    },
    # Criterion 5 (labels never accuse the writer) is about the fixed label
    # text, not the score, so it has no scenario of its own. Every label that
    # comes back from the scenarios above is checked against it.
    #
    # The appeal path isn't one of my five criteria; I tested it by hand in
    # unit 7 (README, Sample Run).
]

# Texts written across several lines in this file pick up indentation and line
# breaks. Collapse them to single spaces so gpt2 scores the words, not the layout.
for _scenario in SCENARIOS:
    if _scenario.get("texts"):
        _scenario["texts"] = [" ".join(str(t).split()) for t in _scenario["texts"]]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
