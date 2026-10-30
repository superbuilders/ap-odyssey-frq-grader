#!/usr/bin/env tsx
/**
 * AP Lang bake-off — BaconWrite production grader arm, out of the box.
 *
 * Runs THEIR criteria-mode path unmodified:
 *   A1_PARAGRAPH_SYSTEM  (production system instructions)
 *   + renderUserPrompt   (production template renderer)
 *   + runGrader          (production grader entry point, runtime.ts)
 *   + anthropicProvider  (production provider, structured output, max_tokens 2048, temperature 0)
 *   + criteriaResultSchema (ONE schema, reused for all 54 essays)
 *
 * Nothing in their repo is edited. This file is a sibling of their own
 * scripts/engine-compare.ts and imports the same symbols its claude leg does.
 *
 * Input is the BLIND projection only (data/blind.jsonl). Labels are never read here.
 */
import fs from "node:fs";
import path from "node:path";

import type { GradingRubric, PromptRecipe } from "@/server/content/private/types";
import { A1_PARAGRAPH_SYSTEM } from "@/server/content/private/tasks/a1/paragraph-system-prompt";
import { getGraderModel } from "@/server/grading/model";
import { renderUserPrompt } from "@/server/grading/prompt";
import { anthropicProvider } from "@/server/grading/providers/anthropic";
import { runGrader } from "@/server/grading/runtime";

const DATA = "/Users/jackjiang-work/Documents/GitHub/APPLAT/_bakeoff_baconwrite/data";

type Blind = {
  essay_id: string; essay_text: string; prompt_text: string; stimulus_text: string | null;
  frq_type: string; source_titles: string[] | null; word_count: number;
  cited_sources: string[] | null; year: string; set: number; question: number;
};
type RubricRows = { row_a: string; row_b: string; row_c: string };

/** THE MAPPING. One criterion per AP row; weights 1/4/1 = the AP point values;
 *  description = College Board's verbatim row text, byte-for-byte from the
 *  official scoring guidelines. No pitfalls, no paraphrase, nothing of ours. */
function apRubric(b: Blind, rows: RubricRows): GradingRubric {
  return {
    rubricId: `AP_LANG_${b.year}_S${b.set}_Q${b.question}` as GradingRubric["rubricId"],
    description:
      `AP English Language and Composition ${b.year}, Set ${b.set}, Question ${b.question} ` +
      `(${b.frq_type}). Official College Board analytic rubric, 6 points total: ` +
      `Row A Thesis 0-1, Row B Evidence and Commentary 0-4, Row C Sophistication 0-1.`,
    // AP imposes no minimum length, so no phantom word-count gate is introduced.
    minWords: 0,
    maxScore: 6,
    criteria: [
      { id: "row_a_thesis", name: "Row A - Thesis (0-1 points)", description: rows.row_a, weight: 1 },
      { id: "row_b_evidence_commentary", name: "Row B - Evidence and Commentary (0-4 points)", description: rows.row_b, weight: 4 },
      { id: "row_c_sophistication", name: "Row C - Sophistication (0-1 points)", description: rows.row_c, weight: 1 },
    ],
    commonPitfalls: [],
  };
}

/** Stands in for buildLessonPromptContext: the same role (the task the student
 *  was answering), carrying only blind-projection fields. */
function apContext(b: Blind): Record<string, unknown> {
  return {
    courseKey: "AP_LANG", lessonKey: `${b.year}_SET${b.set}`, taskKey: `Q${b.question}_${b.frq_type}`,
    title: `AP English Language and Composition - Free Response Question ${b.question}`,
    summary: `Timed exam essay. Free-response type: ${b.frq_type}. Scored on the official College Board 6-point analytic rubric (Rows A/B/C).`,
    taskContext: {
      promptText: b.prompt_text,
      ...(b.stimulus_text ? { providedSources: b.stimulus_text } : {}),
      ...(b.source_titles?.length ? { sourceTitles: b.source_titles } : {}),
    },
  };
}

const RECIPE: PromptRecipe = {
  templateId: "AP_LANG_bakeoff.criteria.v1",
  systemInstructions: A1_PARAGRAPH_SYSTEM, // production, byte-for-byte
  userTemplate: [
    "Lesson context:", "<< lessonContext >>", "",
    "Rubric (JSON):", "<< rubricJson >>", "",
    "Student submission:", "<< studentText >>",
  ].join("\n"), // production PARAGRAPH_USER_TEMPLATE, byte-for-byte
  requiredVariables: ["lessonContext", "rubricJson", "studentText"],
};

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function gradeOne(b: Blind, rows: RubricRows, model: string) {
  const rubric = apRubric(b, rows);
  const userPrompt = renderUserPrompt(RECIPE, {
    lessonContext: JSON.stringify(apContext(b), null, 2),
    rubricJson: JSON.stringify(rubric, null, 2),
    studentText: b.essay_text,
  });
  for (let attempt = 1; attempt <= 4; attempt++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 180_000);
    const t0 = performance.now();
    try {
      const result = await runGrader({
        systemInstructions: RECIPE.systemInstructions,
        userPrompt,
        modelIdentifier: model,
        abortSignal: controller.signal,
        provider: anthropicProvider,
      });
      const latencyMs = Math.round(performance.now() - t0);
      if (result.kind === "ok") {
        return { ok: true as const, parsed: result.parsed, latencyMs, attempt,
          tokensIn: result.trace.tokensIn, tokensOut: result.trace.tokensOut };
      }
      const why = result.kind === "providerFailure"
        ? `${result.error.code}: ${result.error.message.slice(0, 200)}`
        : result.kind === "schemaFailure" ? `schema: ${JSON.stringify(result.zodIssues).slice(0, 200)}` : "timeout";
      console.error(`  ${b.essay_id} attempt ${attempt} -> ${result.kind} (${why})`);
      if (attempt === 4) return { ok: false as const, why, latencyMs, attempt };
      await sleep(4000 * attempt);
    } finally { clearTimeout(timer); }
  }
  return { ok: false as const, why: "exhausted", latencyMs: 0, attempt: 4 };
}

async function main() {
  const model = getGraderModel();
  const blind: Blind[] = fs.readFileSync(path.join(DATA, "blind.jsonl"), "utf8")
    .trim().split("\n").map((l) => JSON.parse(l) as Blind);
  const limit = Number(process.env.LIMIT ?? 0);
  if (limit > 0) blind.length = Math.min(blind.length, limit);
  const rubrics = JSON.parse(fs.readFileSync(path.join(DATA, "rubrics.json"), "utf8")) as Record<string, RubricRows>;
  console.log(`model=${model} base=${process.env.ANTHROPIC_BASE_URL} essays=${blind.length}`);

  const out: unknown[] = [];
  const CONCURRENCY = 3;
  let cursor = 0;
  async function worker(id: number) {
    await sleep(id * 1200); // stagger: pace the run against the grammar-compilation limit
    for (;;) {
      const i = cursor++;
      if (i >= blind.length) return;
      const b = blind[i];
      const rows = rubrics[`${b.year}|${b.set}|${b.question}`];
      if (!rows) throw new Error(`no rubric for ${b.essay_id}`);
      const r = await gradeOne(b, rows, model);
      if (r.ok) {
        const met = Object.fromEntries(r.parsed.criteria_results.map((c) => [c.id, c.met]));
        // CONVERSION BACK TO AP ROWS. This is exactly their own
        // weightedCriteriaScore math (metWeight/totalWeight x 6 points):
        // a met criterion earns its full weight, an unmet one earns 0.
        const row_a = met["row_a_thesis"] === true ? 1 : 0;
        const row_b = met["row_b_evidence_commentary"] === true ? 4 : 0;
        const row_c = met["row_c_sophistication"] === true ? 1 : 0;
        out.push({ essay_id: b.essay_id, ok: true, row_a, row_b, row_c, total: row_a + row_b + row_c,
          met, latencyMs: r.latencyMs, attempt: r.attempt, tokensIn: r.tokensIn, tokensOut: r.tokensOut,
          criteria_results: r.parsed.criteria_results, overall_feedback: r.parsed.overall_feedback,
          next_step: r.parsed.next_step, word_count: r.parsed.word_count, word_count_met: r.parsed.word_count_met });
        console.log(`[${out.length}/${blind.length}] ${b.essay_id} -> A${row_a} B${row_b} C${row_c} (${r.latencyMs}ms, in ${r.tokensIn}/out ${r.tokensOut})`);
      } else {
        out.push({ essay_id: b.essay_id, ok: false, why: r.why, attempt: r.attempt });
        console.log(`[${out.length}/${blind.length}] ${b.essay_id} -> FAILED ${r.why}`);
      }
      fs.writeFileSync(path.join(DATA, "raw-grades.json"), JSON.stringify(out, null, 1));
      await sleep(600);
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCY }, (_, i) => worker(i)));
  fs.writeFileSync(path.join(DATA, "raw-grades.json"), JSON.stringify(out, null, 1));
  console.log(`done: ${out.filter((r) => (r as { ok: boolean }).ok).length}/${blind.length} graded`);
}

main().catch((e: unknown) => { console.error("FAIL", e); process.exit(1); });
