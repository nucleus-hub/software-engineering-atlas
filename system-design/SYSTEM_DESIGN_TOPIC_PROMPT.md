# Prompt: Generate One System Design Topic

```text
Create concise, visual-first system design interview notes for one topic.

INPUT
- Topic number: [NN]
- Topic: [TOPIC]
- Tier: [basics|advanced]

SOURCE OF TRUTH
1. Read system-design/README.md and cover every checklist item under [TOPIC].
2. Match the structure, density, tone, and presentation of:
   system-design/basics/01_System_Design_Interview_Framework_And_Capacity_Estimation.md
3. Import the shared diagram style module:
   system-design/_support/tools/figure_style.py
   Use its palette constants and canvas/heading/box/arrow helpers. If a new
   primitive is needed, add it to that module. Never re-declare colors, fonts,
   or DPI inside a topic script. Treat system-design/basics/assets/topic-01/ as
   a rendered reference only, not as a source to copy values from.

OUTPUT
- Write exactly one canonical note directly to:
  system-design/[TIER]/[NN]_[Topic_Name].md
- Put rendered diagrams in:
  system-design/[TIER]/assets/topic-[NN]/
  and embed them with tier-relative links: assets/topic-[NN]/name.png
- If diagrams need a generator, put it in:
  system-design/_support/tools/plot_topic_[NN]_figures.py
- Do not create docs/ or notes/, and do not leave a generated site/ directory.
- Keep system-design/ to four entries only: README.md, the prompt file,
  basics/, and advanced/. Shared tooling and styles live in _support/.

AUDIENCE AND GOAL
Target Senior, Staff, and Principal Engineer interviews. Help the reader build a
mental model, visualize mechanics, compare choices, reason about failure, and
defend architectural decisions. Write an interview reference—not a textbook.

REQUIRED NOTE STRUCTURE
Use these eight top-level sections, adapting subsections to the topic:

1. One-page visual summary
2. Core mental model
3. Important concepts
4. Decision and trade-off tables
5. Failure scenarios
6. One focused worked example
7. Senior/Principal interview signals
8. Final revision checklist

WRITING RULES
- Aim for 200–300 lines; never exceed 350 without a strong reason.
- Prefer diagrams, compact tables, checklists, and short explanations.
- Introduce each idea once. Do not repeat it in overview, example, interview
  discussion, and takeaways using slightly different hats.
- Cover all curriculum checklist items, but do not add unrelated topic breadth.
- Explain intuition before mechanics and mechanics before trade-offs.
- For every choice, state what it optimizes for, what it costs, and when it
  should change.
- Be technically precise and vendor-neutral; products are examples, not answers.
- Use plain-text code blocks for calculations or formulas.
- Do not add a Common Interview Questions section, formula cheat sheet, diagram
  regeneration section, or generic filler.

DIAGRAM RULES
- Do not use Mermaid.
- Generate high-resolution PNG diagrams when a visual improves understanding.
- Follow Topic 1's style: white canvas, navy headings, blue/light-blue primary
  elements, restrained semantic red/green/amber, generous spacing, short labels,
  bordered panels, and clean directional arrows.
- Use comparison panels, timelines, annotated flows, decision trees, sequence
  views, or architecture diagrams according to the concept—not generic boxes
  for everything.
- Embed each image with descriptive alt text and explain its key insight in one
  short paragraph.
- Inspect every rendered image. Fix clipped text, overlaps, ambiguous arrows,
  incorrect direction, tiny labels, and excessive whitespace before finishing.
- Keep diagrams readable at normal GitHub and MkDocs page width.

WORKED EXAMPLE RULES
- Use one example that exercises the topic's most important trade-offs.
- State scope and assumptions before the design.
- Include only calculations that influence a decision.
- Show the critical path and at least one degraded or failure path.
- Finish with a compact choice / optimization / cost table.

REPOSITORY RULES
- Preserve the existing root curriculum README unless explicitly asked to edit it.
- Keep basics/ and advanced/ for canonical Markdown topic files and their
  per-tier assets/ folder only.
- Keep shared supporting content in _support/tools/ and _support/stylesheets/.
- Update mkdocs-system-design.yml navigation for the new topic.
- Run a strict MkDocs build from the repository root:

  uv run --with mkdocs-material \
    --index-url https://pypi.ci.artifacts.walmart.com/artifactory/api/pypi/external-pypi/simple \
    --allow-insecure-host pypi.ci.artifacts.walmart.com \
    mkdocs build --strict -f mkdocs-system-design.yml

- Remove generated site/ output after validation.
- Validate image links, heading order, line count, and Markdown whitespace.
- Do not commit or push unless I explicitly ask.

Before finishing, report:
- note path and line count;
- curriculum checklist coverage;
- diagrams created and visually inspected;
- strict MkDocs build result;
- Git status, explicitly noting that changes remain uncommitted.
```
