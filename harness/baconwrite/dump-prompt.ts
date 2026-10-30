#!/usr/bin/env tsx
/** Renders (does NOT send) the exact system+user prompt for one essay, so a
 *  reader can audit what their grader was handed. No API call. */
import fs from "node:fs";
import { A1_PARAGRAPH_SYSTEM } from "@/server/content/private/tasks/a1/paragraph-system-prompt";
import { renderUserPrompt } from "@/server/grading/prompt";

const D = "/Users/jackjiang-work/Documents/GitHub/APPLAT/_bakeoff_baconwrite/data";
const blind = fs.readFileSync(`${D}/blind.jsonl`, "utf8").trim().split("\n").map((l) => JSON.parse(l));
const rubrics = JSON.parse(fs.readFileSync(`${D}/rubrics.json`, "utf8"));
const b = blind.find((x) => x.essay_id === (process.argv[2] ?? blind[0].essay_id));
const rows = rubrics[`${b.year}|${b.set}|${b.question}`];
const rubric = {
  rubricId: `AP_LANG_${b.year}_S${b.set}_Q${b.question}`,
  description: `AP English Language and Composition ${b.year}, Set ${b.set}, Question ${b.question} (${b.frq_type}). Official College Board analytic rubric, 6 points total: Row A Thesis 0-1, Row B Evidence and Commentary 0-4, Row C Sophistication 0-1.`,
  minWords: 0, maxScore: 6,
  criteria: [
    { id: "row_a_thesis", name: "Row A - Thesis (0-1 points)", description: rows.row_a, weight: 1 },
    { id: "row_b_evidence_commentary", name: "Row B - Evidence and Commentary (0-4 points)", description: rows.row_b, weight: 4 },
    { id: "row_c_sophistication", name: "Row C - Sophistication (0-1 points)", description: rows.row_c, weight: 1 },
  ],
  commonPitfalls: [],
};
const ctx = {
  courseKey: "AP_LANG", lessonKey: `${b.year}_SET${b.set}`, taskKey: `Q${b.question}_${b.frq_type}`,
  title: `AP English Language and Composition - Free Response Question ${b.question}`,
  summary: `Timed exam essay. Free-response type: ${b.frq_type}. Scored on the official College Board 6-point analytic rubric (Rows A/B/C).`,
  taskContext: { promptText: b.prompt_text, ...(b.stimulus_text ? { providedSources: b.stimulus_text } : {}), ...(b.source_titles?.length ? { sourceTitles: b.source_titles } : {}) },
};
const user = renderUserPrompt(
  { templateId: "AP_LANG_bakeoff.criteria.v1", systemInstructions: A1_PARAGRAPH_SYSTEM,
    userTemplate: ["Lesson context:", "<< lessonContext >>", "", "Rubric (JSON):", "<< rubricJson >>", "", "Student submission:", "<< studentText >>"].join("\n"),
    requiredVariables: ["lessonContext", "rubricJson", "studentText"] },
  { lessonContext: JSON.stringify(ctx, null, 2), rubricJson: JSON.stringify(rubric, null, 2), studentText: b.essay_text },
);
fs.writeFileSync(`${D}/rendered-prompt-${b.essay_id}.txt`,
  `===== SYSTEM (A1_PARAGRAPH_SYSTEM, production, byte-for-byte) =====\n${A1_PARAGRAPH_SYSTEM}\n\n===== USER (renderUserPrompt, production template) =====\n${user}\n`);
console.log(`wrote rendered-prompt-${b.essay_id}.txt  system=${A1_PARAGRAPH_SYSTEM.length}ch user=${user.length}ch`);
