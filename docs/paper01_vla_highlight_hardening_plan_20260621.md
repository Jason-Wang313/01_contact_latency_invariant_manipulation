# Paper01 VLA Highlight Hardening Plan

Date: 2026-06-21

## Objective

Make `C:/Users/wangz/Downloads/01.pdf` explicitly match the visible VLA-v4
role model's boxed-link behavior while preserving the final 26-page
contact-age invariant manipulation paper:

- citation links use green one-point boxes;
- internal figure/table/section links use red one-point boxes;
- URL links use green one-point boxes;
- no cyan or oversized link boxes appear;
- the final PDF is rebuilt, copied to Downloads, visually checked, and leaves
  no local `paper/main.pdf`.

## Plan-Start Evidence

Baseline artifact:

- Canonical PDF: `C:/Users/wangz/Downloads/01.pdf`
- Pages: 26
- Size: 1,254,294 bytes
- SHA256: `868532CDE78C4B132F2C945AAEB924E846D50E09694DDB478AB38D32142770FA`
- Duplicate `C:/Users/wangz/Downloads/1.pdf`: absent
- Local `paper/main.pdf`: absent
- Repository branch: `master`
- Repository status: clean before this plan file

Baseline link inventory from the current Downloads PDF:

- Link pages: `[(2, 33), (3, 2), (4, 2), (5, 1), (7, 1), (8, 1), (9, 2), (13, 1), (15, 2), (19, 1), (20, 1), (21, 3), (23, 1), (25, 1)]`
- Annotation colors: green = 35, red = 17, cyan = 0
- Border widths: `(0, 0, 1)` for all link annotations
- Oversized annotation audit: 0 malformed page-edge rectangles

Source finding:

- `paper/main.tex` is the active manuscript source.
- The active manuscript already loads `hyperref`, and the baseline PDF already
  has green citation/URL boxes and red internal-reference boxes.
- The source does not explicitly pin the VLA-v4 `\hypersetup` policy, so this
  pass will make the matching behavior explicit and auditable.
- Use the documented manual LaTeX flow from `paper/`: `pdflatex`, `bibtex`,
  and repeated `pdflatex` passes before export.

## Role-Model Target

Install the same explicit hyperref policy as the visible VLA-v4 role model:

```tex
\hypersetup{
  colorlinks=false,
  pdfborder={0 0 1},
  citebordercolor={0 1 0},
  linkbordercolor={1 0 0},
  urlbordercolor={0 1 0}
}
```

## Execution Plan

1. Add the VLA `\hypersetup` block in the active `paper/main.tex` preamble
   immediately after the existing `\usepackage{hyperref}`.
2. Rebuild manually from `paper/` with `pdflatex`, `bibtex`, and repeated
   `pdflatex` passes.
3. If the log asks for another pass for cross-references, run the final
   canonical pass before recording metadata.
4. Copy the rebuilt `paper/main.pdf` to `C:/Users/wangz/Downloads/01.pdf`.
5. Remove local `paper/main.pdf` after export.
6. Recompute page count, byte size, SHA256, annotation colors, border widths,
   link pages, and oversized annotation count from the final Downloads PDF.
7. Render every page that contains final link annotations into
   `tmp/pdfs/paper01_after`.
8. Visually inspect rendered affected pages:
   - green citation and URL boxes are crisp and aligned;
   - red internal-reference boxes are crisp and aligned;
   - no cyan or oversized page-edge boxes appear;
   - layout, figures, tables, headers, and page count remain stable.
9. Update README/status/audit/version/validation metadata with the new hash and
   VLA-style boxed-link inventory.
10. Supersede stale pre-v3 readiness status text with the v3/final-gate status
    already reflected in the final audit.
11. Validate build logs, diff hygiene, final PDF hash, expected claim markers,
    and absence of local `paper/main.pdf`.
12. Remove Paper01 temp renders, leaving only the shared role-model render
    directory.
13. Stage only Paper01 source and metadata files, commit, push, and verify a
    clean repository.

## Expected Validation Signals

- Final artifact remains at least 20 pages and should remain 26 pages.
- Final annotation colors should remain green/red only, with cyan count zero.
- Final annotation borders should all remain `(0, 0, 1)`.
- Final oversized annotation count must be zero.
- Expected content markers should still include `12,544`, `111.90`, `8.48`,
  `9.22`, `3.1%`, `261.35`, `Contact-Age Invariant Control`, `CAIC`, and
  `claim`.

## Non-Goals

- Do not alter experiment results, claims, figures, tables, bibliography
  content, or page count.
- Do not add or remove citations, references, URLs, or template examples merely
  to change link counts.
- Do not create an additional `1.pdf`; keep the repository's canonical
  Downloads target as `01.pdf`.
- Do not leave intermediate PDFs or render folders behind.

## Completion Evidence

Completed source/build/export actions:

- Added the explicit VLA-v4 `\hypersetup` block immediately after `\usepackage{hyperref}` in `paper/main.tex`.
- Rebuilt from `paper/` with manual `pdflatex`, `bibtex`, `pdflatex`, `pdflatex` passes.
- Copied the verified build to `C:/Users/wangz/Downloads/01.pdf`.
- Removed transient local `paper/main.pdf` after export.

Final canonical artifact:

- PDF: `C:/Users/wangz/Downloads/01.pdf`
- Pages: 26
- Size: 1,254,294 bytes
- SHA256: `92E7BE958E6A5761619853445346A31D3C281FD23EF73D200DB8A4CD16A1F013`

Final link inventory:

- Link pages: `[(2, 33), (3, 2), (4, 2), (5, 1), (7, 1), (8, 1), (9, 2), (13, 1), (15, 2), (19, 1), (20, 1), (21, 3), (23, 1), (25, 1)]`
- Annotation colors: green = 35, red = 17, cyan = 0
- Border widths: `(0, 0, 1)` for all link annotations
- Oversized annotation audit: 0 malformed page-edge rectangles

Visual audit:

- Rendered pages 2, 3, 4, 5, 7, 8, 9, 13, 15, 19, 20, 21, 23, and 25 into the Paper01 temp render folder.
- Inspected the rendered contact sheet and dense citation page: citation and URL boxes are green, internal-reference boxes are red, all boxes are crisp/aligned, and no cyan or page-edge boxes appear.

Cleanup state:

- No duplicate `C:/Users/wangz/Downloads/1.pdf`.
- No local `paper/main.pdf`.
