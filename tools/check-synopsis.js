#!/usr/bin/env node
// Mechanical house-style gates for synopsis installments (EN: synopsis/, RU: конспект/).
// Run:  npx -y -p markdown-it@14 node tools/check-synopsis.js
// Exit 0 = all gates green, 1 = at least one failure.
//
// Strict gates (single-<em> abstract, ## I. … ## Coda/Кода) apply to Section III
// installments only (NN >= 10). Universal gates (no-LaTeX math, README entry) apply to all.

const fs = require('fs');
const path = require('path');

const repo = path.join(__dirname, '..');

// markdown-it gives the precise single-<em> render check. Resolve it locally, or from the
// sibling science-of-logic repo (the repos are mirrors). If neither resolves, the abstract
// gate is skipped with a warning rather than producing a false failure.
let md = null;
for (const p of ['markdown-it', path.join(repo, '..', 'science-of-logic', 'node_modules', 'markdown-it')]) {
  try { md = new (require(p))({ html: true, linkify: true, typographer: true }); break; } catch { /* try next */ }
}

const dir = ['synopsis', 'конспект']
  .map(d => path.join(repo, d))
  .find(d => fs.existsSync(d));
if (!dir) {
  console.error('No synopsis/ or конспект/ directory found.');
  process.exit(1);
}

const readmePath = path.join(repo, 'README.md');
const readme = fs.existsSync(readmePath) ? fs.readFileSync(readmePath, 'utf8') : '';

// Canon denylist: locked-terminology violations as mechanical gates. Optional file; each rule is
// { "pattern": "<regex>", "flags": "<opt>", "message": "<why + fix>" }.
const denyPath = path.join(repo, 'tools', 'canon-denylist.json');
let denyRules = [];
if (fs.existsSync(denyPath)) {
  try {
    denyRules = JSON.parse(fs.readFileSync(denyPath, 'utf8'))
      .map(r => ({ re: new RegExp(r.pattern, r.flags || ''), message: r.message }));
  } catch (e) {
    console.error('canon-denylist.json could not be parsed:', e.message);
    process.exit(1);
  }
}

const files = fs.readdirSync(dir).filter(f => /^\d+.*\.md$/.test(f)).sort();

let failures = 0;
const fail = (file, msg) => { console.log(`  ✗ ${file}: ${msg}`); failures++; };

// Scan a source string line-by-line against the canon denylist; report under `label`.
const scanCanon = (label, text) => {
  const lines = text.split(/\r?\n/);
  for (const rule of denyRules) {
    lines.forEach((ln, i) => { if (rule.re.test(ln)) fail(label, `canon: ${rule.message} — line ${i + 1}`); });
  }
};

for (const f of files) {
  const nn = parseInt(f, 10);
  const sectionIII = nn >= 10;
  const src = fs.readFileSync(path.join(dir, f), 'utf8');
  const html = md ? md.render(src) : null;

  // --- Strict gates (Section III only) ---
  if (sectionIII) {
    // 1. Abstract = a single outer <em> span (first <p> after the <h1>).
    if (md) {
      const pMatch = html.match(/<p>[\s\S]*?<\/p>/);
      if (!pMatch) {
        fail(f, 'no abstract paragraph found');
      } else {
        const ab = pMatch[0];
        const opens = (ab.match(/<em>/g) || []).length;
        const closes = (ab.match(/<\/em>/g) || []).length;
        const wraps = /^<p><em>/.test(ab) && /<\/em><\/p>$/.test(ab);
        if (!wraps || opens !== closes) {
          fail(f, `abstract is not a single <em> span (wraps:${wraps}, em ${opens}/${closes})`);
        }
      }
    }

    // 2. Section skeleton: Roman-numeral headings form a contiguous run I, II, …, N (no gaps,
    //    no repeats, in order) — N varies per installment — followed by a Coda/Кода.
    const heads = src.match(/^##\s+.*$/gm) || [];
    const romanToInt = (r) => {
      const v = { I: 1, V: 5, X: 10 };
      let n = 0, prev = 0;
      for (let i = r.length - 1; i >= 0; i--) {
        const d = v[r[i]];
        if (!d) return NaN;
        if (d < prev) n -= d; else { n += d; prev = d; }
      }
      return n;
    };
    const romans = heads.map(h => (h.match(/^##\s+([IVX]+)\.\s/) || [])[1]).filter(Boolean);
    if (!romans.length) {
      fail(f, 'no "## I." … roman-numeral sections found');
    } else if (!romans.map(romanToInt).every((n, i) => n === i + 1)) {
      fail(f, `roman sections not a contiguous I..N run (got ${romans.join(', ')})`);
    }
    if (!heads.some(h => /^##\s+(Coda|Кода)\s*$/.test(h))) fail(f, 'missing "## Coda"/"## Кода"');
  }

  // --- Universal gates ---
  // 3. No LaTeX-delimited math (math must be italic-plain).
  if (/\$[^$\n]+\$/.test(src) || /\\\([^)]*\\\)/.test(src) || /\\\[[^\]]*\\\]/.test(src)) {
    fail(f, 'LaTeX math delimiters found ($…$ / \\(…\\)) — use italic-plain math');
  }

  // 4. README has an entry linking this file.
  if (readme && !readme.includes(f)) {
    fail(f, 'no README entry links this file');
  }

  // 5. Canon denylist (locked-terminology violations).
  scanCanon(f, src);
}

// The README is held to the canon denylist too.
if (readme) scanCanon('README.md', readme);

console.log(`\nabstract check: ${md ? 'markdown-it (precise)' : 'SKIPPED — markdown-it not resolvable (install it, or run beside the science-of-logic repo)'}`);
if (failures) {
  console.log(`FAIL — ${failures} issue(s) across ${files.length} file(s) in ${path.basename(dir)}/.`);
  process.exit(1);
}
console.log(`PASS — ${files.length} file(s) in ${path.basename(dir)}/ passed all mechanical gates.`);
