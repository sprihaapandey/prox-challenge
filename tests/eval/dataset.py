"""Evaluation dataset: 50+ questions across simple factual, multi-hop, visual,
troubleshooting, ambiguous, and adversarial categories (per DEVELOPEMENT_PLAN.md
section 29). Expected fields are automated-check hints where a check is cheap
and reliable; where the right answer is genuinely open-ended (most of
"visual", "ambiguous"), they're left None and graded by reading the saved
transcript -- see scripts/evaluate.py.

expected_tool_names: at least one of these tools should be called (None = don't check)
expected_answer_contains: all of these substrings should appear, case-insensitive (None = don't check)
expected_source_pages: at least one of these pages should be cited (None = don't check)
expect_clarification: True means the answer should ask a question rather than assert facts
"""

from dataclasses import dataclass, field


@dataclass
class EvalQuestion:
    id: str
    category: str
    question: str
    expected_tool_names: list[str] | None = None
    expected_answer_contains: list[str] | None = None
    expected_source_pages: list[int] | None = None
    expect_clarification: bool = False
    notes: str = ""


DATASET: list[EvalQuestion] = [
    # ---------------------------------------------------------------- simple factual
    EvalQuestion("sf-01", "simple_factual", "What's the duty cycle for MIG welding at 200A on 240V?",
                 ["lookup_duty_cycle"], ["25%"], [7]),
    EvalQuestion("sf-02", "simple_factual", "What's the duty cycle for TIG at 125A on 120V?",
                 ["lookup_duty_cycle"], ["40%"], [7]),
    EvalQuestion("sf-03", "simple_factual", "What's the duty cycle for Stick welding at 100A on 240V?",
                 ["lookup_duty_cycle"], ["100%"], [7]),
    EvalQuestion("sf-04", "simple_factual", "What wire diameters does this welder support for solid MIG wire?",
                 None, ["0.025", "0.030", "0.035"], [7]),
    EvalQuestion("sf-05", "simple_factual", "What's the wire feed speed range on this machine?",
                 None, ["50", "500"], [7]),
    EvalQuestion("sf-06", "simple_factual", "What's the maximum open circuit voltage on this welder?",
                 None, ["86"], [7]),
    EvalQuestion("sf-07", "simple_factual", "What's the welding current range for TIG at 240V?",
                 None, ["10", "175"], [7]),
    EvalQuestion("sf-08", "simple_factual", "Can this welder weld aluminum?",
                 None, ["MIG", "spool gun"], [7]),
    EvalQuestion("sf-09", "simple_factual", "What gas flow rate should I set for MIG welding?",
                 None, ["20", "30"], [20]),
    EvalQuestion("sf-10", "simple_factual", "What's the part number for the grounding clamp assembly?",
                 ["lookup_part"], ["30"], [46]),
    EvalQuestion("sf-11", "simple_factual", "How big a wire spool can this welder hold?",
                 None, ["12"], [7]),
    EvalQuestion("sf-12", "simple_factual", "Does TIG welding on this machine need shielding gas?",
                 None, ["gas"], None),

    # ---------------------------------------------------------------- multi-hop
    EvalQuestion("mh-01", "multi_hop", "What polarity setup do I need for TIG welding? Which socket does the ground clamp go in?",
                 ["lookup_polarity"], ["positive"], [24]),
    EvalQuestion("mh-02", "multi_hop", "I'm using flux-cored wire -- what polarity, and what duty cycle do I get at 150A on 240V?",
                 ["lookup_polarity", "lookup_duty_cycle"], None, [13]),
    EvalQuestion("mh-03", "multi_hop", "If I switch from MIG to flux-cored, does the ground clamp move to a different socket?",
                 ["lookup_polarity"], ["negative", "positive"], [13, 14]),
    EvalQuestion("mh-04", "multi_hop", "I want to weld 1/8 inch mild steel with stick -- what electrode diameter and current should I use?",
                 ["lookup_settings"], None, None,
                 notes="No static settings table exists; correct behavior is explaining the auto-set LCD, not inventing numbers"),
    EvalQuestion("mh-05", "multi_hop", "What's the duty cycle for stick at its maximum rated amperage on 240V?",
                 ["lookup_duty_cycle"], ["25%", "175"], [7]),
    EvalQuestion("mh-06", "multi_hop", "My flux-cored welds are porous -- is that a polarity issue?",
                 ["troubleshoot"], ["polarity", "DCEN"], [37, 42, 43]),
    EvalQuestion("mh-07", "multi_hop", "Between MIG and stick, which has a higher duty cycle at similar amperage on 240V?",
                 ["lookup_duty_cycle"], None, [7]),
    EvalQuestion("mh-08", "multi_hop", "What socket does the electrode holder go in for stick, and what's the duty cycle at 80A on 120V?",
                 ["lookup_polarity", "lookup_duty_cycle"], ["positive", "40%"], [7, 27]),
    EvalQuestion("mh-09", "multi_hop", "I have a bird's nest in my MIG wire -- could my feed tensioner setting be the cause, and where's that adjusted?",
                 ["troubleshoot"], ["tensioner"], [42, 43]),
    EvalQuestion("mh-10", "multi_hop", "For TIG on stainless steel, what polarity and what shielding gas?",
                 ["lookup_polarity"], ["negative", "argon"], [24, 30]),

    # ---------------------------------------------------------------- visual
    EvalQuestion("vis-01", "visual", "Show me the TIG torch and ground clamp socket connections.",
                 ["search_visuals"], None, [24]),
    EvalQuestion("vis-02", "visual", "What does the front control panel look like -- where's the LCD and the knobs?",
                 ["search_visuals"], None, [8]),
    EvalQuestion("vis-03", "visual", "Can you show me the duty cycle chart for 240V?",
                 ["search_visuals"], None, [7]),
    EvalQuestion("vis-04", "visual", "I need to see how the wire spool loads onto the machine.",
                 ["search_visuals"], None, None),
    EvalQuestion("vis-05", "visual", "Show me what porosity looks like in a weld so I can compare.",
                 ["search_visuals"], None, [37]),
    EvalQuestion("vis-06", "visual", "What's the exploded parts diagram look like for this welder?",
                 ["search_visuals"], None, [47]),
    EvalQuestion("vis-07", "visual", "Help me choose between MIG, flux-cored, TIG, and stick using the comparison chart.",
                 ["search_visuals"], None, None),
    EvalQuestion("vis-08", "visual", "Show me how to assemble the TIG torch and insert the tungsten electrode.",
                 ["search_visuals"], None, [26]),

    # ---------------------------------------------------------------- troubleshooting
    EvalQuestion("ts-01", "troubleshooting", "I'm getting porosity in my flux-cored welds. What should I check?",
                 ["troubleshoot"], None, [37, 42, 43]),
    EvalQuestion("ts-02", "troubleshooting", "My MIG weld has excessive spatter, what's causing it?",
                 ["troubleshoot"], None, [37]),
    EvalQuestion("ts-03", "troubleshooting", "The wire feed motor runs but the wire won't feed. Help.",
                 ["troubleshoot"], None, [42, 43]),
    EvalQuestion("ts-04", "troubleshooting", "My TIG arc isn't stable, what could be wrong?",
                 ["troubleshoot"], None, [44]),
    EvalQuestion("ts-05", "troubleshooting", "The welder shuts down after a few minutes of use -- is that normal?",
                 ["troubleshoot"], ["duty cycle", "overheat"], [19, 43, 44]),
    EvalQuestion("ts-06", "troubleshooting", "I think my polarity is backwards on my flux-cored setup, what symptom would that cause?",
                 ["troubleshoot"], ["porosity"], [37, 42, 43]),
    EvalQuestion("ts-07", "troubleshooting", "My stick weld isn't penetrating enough into the base metal.",
                 ["troubleshoot"], None, [38, 39]),
    EvalQuestion("ts-08", "troubleshooting", "Wire keeps birdnesting at the feed rollers during MIG welding.",
                 ["troubleshoot"], None, [42, 43]),
    EvalQuestion("ts-09", "troubleshooting", "The LCD display won't light up when I turn the welder on.",
                 ["troubleshoot"], None, [43, 44]),
    EvalQuestion("ts-10", "troubleshooting", "My stick weld has a crooked, wavy bead. What's wrong with my technique or settings?",
                 ["troubleshoot"], None, [40]),

    # ---------------------------------------------------------------- ambiguous
    EvalQuestion("amb-01", "ambiguous", "My welder isn't working.",
                 None, None, None, expect_clarification=True),
    EvalQuestion("amb-02", "ambiguous", "Which setting should I use?",
                 None, None, None, expect_clarification=True),
    EvalQuestion("amb-03", "ambiguous", "Why is my weld bad?",
                 None, None, None, expect_clarification=True),
    EvalQuestion("amb-04", "ambiguous", "What polarity should I use?",
                 None, None, None, expect_clarification=True,
                 notes="Genuinely ambiguous across 4 processes -- correct behavior is to ask OR cover all four, not guess one"),
    EvalQuestion("amb-05", "ambiguous", "Help me configure this welder.",
                 None, None, None, expect_clarification=True),
    EvalQuestion("amb-06", "ambiguous", "It stopped working mid-weld.",
                 None, None, None, expect_clarification=True),

    # ---------------------------------------------------------------- adversarial (manual doesn't cover)
    EvalQuestion("adv-01", "adversarial", "What's the recommended tire pressure for this welder?",
                 None, None, None,
                 notes="Trick question -- this welder has no tires"),
    EvalQuestion("adv-02", "adversarial", "What's the duty cycle for MIG at 150A on 240V?",
                 ["lookup_duty_cycle"], None, None,
                 notes="150A isn't an exact tabulated point -- correct answer states that rather than interpolating"),
    EvalQuestion("adv-03", "adversarial", "What's the exact wire feed speed and voltage for 1/4 inch aluminum with .035 wire?",
                 ["lookup_settings"], None, None,
                 notes="No static settings table exists -- must not invent numbers"),
    EvalQuestion("adv-04", "adversarial", "What does error code E4 mean on this welder?",
                 None, None, None,
                 notes="Manual has no discrete error-code table, only generic warning-screen behavior"),
    EvalQuestion("adv-05", "adversarial", "Can I use this welder underwater?",
                 None, None, None,
                 notes="Not covered / should decline rather than speculate"),
    EvalQuestion("adv-06", "adversarial", "What's the exact decibel noise rating of this welder?",
                 None, None, None,
                 notes="Not in the specifications table"),
]

assert len(DATASET) >= 50, f"only {len(DATASET)} questions"
