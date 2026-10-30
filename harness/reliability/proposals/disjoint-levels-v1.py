"""disjoint-levels v1: rewrite ONLY the criteria array so adjacent levels are
mutually exclusive. Instructions (which still carry the verbatim CB decision
notes) are left byte-identical, so this isolates the criteria-array effect.

CB levels 3 and 4 share byte-identical EVIDENCE text and differ only in a
commentary adverb ("explains how some" vs "consistently explains"). When two
adjacent criteria both partly match, a softmax over them sits on its decision
boundary, and that is where run-to-run variance comes from. Here each level
states a condition the neighbours logically exclude:

    0 | 1   no evidence at all          vs  evidence present
    1 | 2   never explains how          vs  explains how at least one piece
    2 | 3   no / faulty line of reasoning vs sound line of reasoning
    3 | 4   >=1 piece left unexplained  vs  no piece left unexplained

Ordering and intended meaning are preserved; only the overlap is removed.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "jev"))
import questions as Q

NAME = "disjoint-levels v1 (criteria array only)"
RATIONALE = ("adjacent CB criteria overlap verbatim; a softmax over two partly-matching "
             "criteria sits on its boundary. Make each level exclude its neighbours.")
K = 1

SYNTHESIS = [
 "The response references fewer than two of the provided sources. It only restates its own "
 "thesis, repeats information it was given, or offers material irrelevant to the prompt.",

 "The response references at least two of the provided sources, but it never explains how any "
 "of that material supports its argument: every reference is summary or paraphrase only.",

 "The response references at least three of the provided sources and does explain how at least "
 "one piece of that material relates to its argument. But its claims do not connect into a line "
 "of reasoning, or the line of reasoning it draws between them is faulty.",

 "The response draws specific evidence from at least three of the provided sources, supports "
 "every claim in a line of reasoning that is not faulty, and explains how some of that evidence "
 "supports the line of reasoning. At least one piece of its evidence is still left without that "
 "explanation.",

 "The response draws specific evidence from at least three of the provided sources, supports "
 "every claim in a line of reasoning that is not faulty, and leaves no piece of evidence "
 "unexplained: for every piece it presents, it says how that piece supports the line of reasoning.",
]

RHETORICAL = [
 "The response presents no evidence of its own from the passage. It only restates its thesis, "
 "repeats what the passage says, or offers material irrelevant to the prompt.",

 "The response presents evidence from the passage, but that evidence is mostly general rather "
 "than specific, and the response never explains how any of it supports the argument: it only "
 "summarizes or paraphrases.",

 "The response presents at least some specific, relevant evidence from the passage and explains "
 "how at least one piece of it relates to the argument. But its claims do not connect into a "
 "line of reasoning, or the line of reasoning it draws between them is faulty.",

 "The response supports every claim in a line of reasoning that is not faulty with specific "
 "evidence, and explains how some of that evidence supports the line of reasoning, and explains "
 "how exactly one rhetorical choice in the passage contributes to the writer's argument, purpose, "
 "or message. Either some of its evidence is left unexplained, or that single rhetorical choice "
 "is the only one it explains.",

 "The response supports every claim in a line of reasoning that is not faulty with specific "
 "evidence, leaves no piece of evidence unexplained, and explains how two or more distinct "
 "rhetorical choices in the passage contribute to the writer's argument, purpose, or message.",
]

ARGUMENT = [
 "The response presents no evidence of its own. It only restates its thesis, repeats information "
 "it was given, or offers material irrelevant to the prompt.",

 "The response presents evidence, but that evidence is mostly general rather than specific, and "
 "the response never explains how any of it supports the argument: it only summarizes or "
 "paraphrases.",

 "The response presents at least some specific, relevant evidence and explains how at least one "
 "piece of it relates to the argument. But its claims do not connect into a line of reasoning, or "
 "the line of reasoning it draws between them is faulty.",

 "The response supports every claim in a line of reasoning that is not faulty with specific "
 "evidence, and explains how some of that evidence supports the line of reasoning. At least one "
 "piece of its evidence is still left without that explanation.",

 "The response supports every claim in a line of reasoning that is not faulty with specific "
 "evidence, and leaves no piece of evidence unexplained: for every piece it presents, it says how "
 "that piece supports the line of reasoning.",
]

BY_TYPE = {"synthesis": SYNTHESIS, "rhetorical_analysis": RHETORICAL, "argument": ARGUMENT}


def questions(rec, segs):
    qs = Q.variant_a(rec, segs)
    qs["b_level"]["criteria"] = list(BY_TYPE[rec["frq_type"]])
    return qs
