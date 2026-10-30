"""Question sets. All rubric wording is pasted verbatim from the College Board
scoring guidelines for that exact year+set+question (rubric.cell)."""
from rubric import cell

def _rc(rec, row):
    return cell(str(rec["year"]), int(rec["set"]), int(rec["question"]), row)

# ---------- shared rows (identical in both variants) ----------
def row_a_q(rec):
    c = _rc(rec, "A")
    return {"a_thesis": {"type": "noul",
        "instructions": ("You are applying the College Board AP English Language Row A (Thesis) scoring "
          "criterion to the section titled STUDENT RESPONSE (complete). The criterion for the 1 point, "
          "verbatim: \"%s\"\nDecision rules, verbatim. Responses that do NOT earn this point: %s\n"
          "Responses that DO earn this point: %s\n%s\nAnswer true only if STUDENT RESPONSE (complete) "
          "earns the 1 point." % (c["criteria"][1], c["notes"][0], c["notes"][1], c["additional"])),
        "criteria": {"true": "STUDENT RESPONSE (complete) earns the Row A thesis point: it responds to the "
                             "prompt with a thesis that presents a defensible position.",
                     "false": "STUDENT RESPONSE (complete) earns 0 points for Row A."}}}

def row_c_q(rec):
    c = _rc(rec, "C")
    return {"c_soph": {"type": "noul",
        "instructions": ("You are applying the College Board AP English Language Row C (Sophistication) "
          "scoring criterion to the section titled STUDENT RESPONSE (complete). The criterion for the 1 "
          "point, verbatim: \"%s\"\nDecision rules, verbatim. Responses that do NOT earn this point: %s\n"
          "Responses that earn this point: %s\n%s" % (c["criteria"][1], c["notes"][0], c["notes"][1], c["additional"])),
        "criteria": {"true": "STUDENT RESPONSE (complete) earns the Row C sophistication point.",
                     "false": "STUDENT RESPONSE (complete) does not meet the criteria for the point."}}}

# ---------- variant A ----------
def variant_a(rec, segs):
    c = _rc(rec, "B")
    qs = {}
    qs.update(row_a_q(rec)); qs.update(row_c_q(rec))
    qs["b_level"] = {"type": "score",
        "instructions": ("You are applying the College Board AP English Language Row B (Evidence and "
          "Commentary, 0-4 points) scoring criteria to the section titled STUDENT RESPONSE (complete). "
          "Choose the level whose verbatim criteria the response meets. College Board decision rules, "
          "verbatim, for each level: 0 -- %s | 1 -- %s | 2 -- %s | 3 -- %s | 4 -- %s\n%s"
          % (c["notes"][0], c["notes"][1], c["notes"][2], c["notes"][3], c["notes"][4], c["additional"])),
        "criteria": list(c["criteria"])}
    return qs

# ---------- variant B ----------
def variant_b(rec, segs):
    c = _rc(rec, "B")
    syn = rec["frq_type"] == "synthesis"
    rhet = rec["frq_type"] == "rhetorical_analysis"
    src = "the provided sources" if syn else ("the passage" if rhet else "the student's own examples")
    qs = {}
    qs.update(row_a_q(rec)); qs.update(row_c_q(rec))

    qs["b_restates"] = {"type": "noul",
        "instructions": ("College Board Row B 0-point criterion, verbatim: \"%s\" Apply it to the section "
          "titled STUDENT RESPONSE (complete)." % c["criteria"][0]),
        "criteria": {"true": "STUDENT RESPONSE (complete) does only that: it simply restates its thesis, "
                             "repeats provided information, or offers irrelevant information.",
                     "false": "STUDENT RESPONSE (complete) does more than that."}}

    qs["b_specific"] = {"type": "noul",
        "instructions": ("College Board distinguishes evidence that is \"mostly general\" (1 point) from "
          "\"specific\" evidence (3 and 4 points). Read the section titled STUDENT RESPONSE (complete). "
          "Decide whether the evidence it draws from %s is specific -- particular quoted words, named "
          "details, figures or concrete examples -- rather than general gestures at what %s say." % (src, src)),
        "criteria": {"true": "The evidence in STUDENT RESPONSE (complete) is specific.",
                     "false": "The evidence in STUDENT RESPONSE (complete) is mostly general."}}

    qs["b_uniform"] = {"type": "noul",
        "instructions": ("College Board Row B decision rule for 3 points, verbatim, first bullet: "
          "\"Uniformly offer evidence to support claims.\" The 2-point decision rule, verbatim, says such "
          "responses \"Consist of a mix of specific evidence and broad generalities.\" Read the section "
          "titled STUDENT RESPONSE (complete) and decide which of the two it matches."),
        "criteria": {"true": "STUDENT RESPONSE (complete) uniformly offers evidence to support its claims.",
                     "false": "STUDENT RESPONSE (complete) consists of a mix of specific evidence and broad "
                              "generalities."}}

    qs["b_multiclaims"] = {"type": "noul",
        "instructions": ("College Board Row B decision rule for 3 points, verbatim: \"Organize an argument as "
          "a line of reasoning composed of multiple supporting claims.\" The 2-point rule, verbatim, says "
          "such responses \"May make one point well but either do not make multiple supporting claims or do "
          "not adequately support more than one claim.\" Read the section titled STUDENT RESPONSE "
          "(complete) and decide which of the two it matches."),
        "criteria": {"true": "STUDENT RESPONSE (complete) makes multiple supporting claims and adequately "
                             "supports more than one of them.",
                     "false": "STUDENT RESPONSE (complete) makes one point well but does not make or "
                              "adequately support multiple claims."}}

    qs["b_lor"] = {"type": "noul",
        "instructions": ("College Board separates level 2 from level 3 by whether a line of reasoning is "
          "established. Level 2, verbatim: \"%s\" Read the section titled STUDENT RESPONSE (complete). A "
          "line of reasoning means its supporting claims connect and progress toward the thesis, rather "
          "than sitting as disconnected observations." % c["criteria"][2]),
        "criteria": {"true": "STUDENT RESPONSE (complete) establishes a line of reasoning that is not faulty.",
                     "false": "STUDENT RESPONSE (complete) establishes no line of reasoning, or its line of "
                              "reasoning is faulty."}}

    qs["b_mech"] = {"type": "noul",
        "instructions": ("College Board Additional Note, verbatim: \"Writing that suffers from grammatical "
          "and/or mechanical errors that interfere with communication cannot earn the fourth point in this "
          "row.\" This bar is about communication breaking down, not about a response merely containing "
          "errors. Read the section titled STUDENT RESPONSE (complete)."),
        "criteria": {"true": "Errors in STUDENT RESPONSE (complete) actually interfere with communication: "
                             "at least one sentence is hard or impossible to understand because of them.",
                     "false": "STUDENT RESPONSE (complete) may contain errors, but every sentence still "
                              "communicates its meaning."}}

    # per-segment ladder: makes "consistently explains" countable in code
    for i in range(1, len(segs) + 1):
        qs["seg%d_ev" % i] = {"type": "noul",
            "instructions": ("Read ONLY the section titled SEGMENT %d. Ignore every other section. Decide "
              "whether SEGMENT %d presents any evidence at all -- a quotation, a named detail, a figure, a "
              "fact or a concrete example drawn from %s." % (i, i, src)),
            "criteria": {"true": "SEGMENT %d presents at least one piece of evidence." % i,
                         "false": "SEGMENT %d presents no evidence; it is only assertion, transition or "
                                  "restatement." % i}}
        qs["seg%d_expl" % i] = {"type": "noul",
            "instructions": ("College Board Row B level 4 requires, verbatim: \"Consistently explains how the "
              "evidence supports a line of reasoning.\" Read ONLY the section titled SEGMENT %d. Ignore every "
              "other section. Decide whether SEGMENT %d itself explains HOW its evidence supports the "
              "argument. Merely summarizing, paraphrasing or restating the evidence is not explaining how." % (i, i)),
            "criteria": {"true": "SEGMENT %d explains how its evidence supports the argument." % i,
                         "false": "SEGMENT %d only summarizes or presents evidence without explaining how it "
                                  "supports the argument, or contains no evidence." % i}}
        if rhet:
            qs["seg%d_rhet" % i] = {"type": "noul",
                "instructions": ("College Board Row B level 4 requires, verbatim: \"Explains how multiple "
                  "rhetorical choices in the passage contribute to the writer's argument, purpose, or "
                  "message.\" The 1-point decision rule, verbatim, describes responses that \"Mention "
                  "rhetorical choices with little or no explanation.\" Read ONLY the section titled SEGMENT "
                  "%d. Ignore every other section." % i),
                "criteria": {"true": "SEGMENT %d names a specific rhetorical choice the passage's writer "
                                     "makes and then explains how that choice contributes to the writer's "
                                     "argument, purpose or message." % i,
                             "false": "SEGMENT %d mentions a rhetorical choice with little or no "
                                      "explanation of its contribution, or names none at all." % i}}
    return qs
