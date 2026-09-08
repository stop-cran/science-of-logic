#!/usr/bin/env node
// Mirror audits: compare an installment set against its translation, line for line.
//
// Run:  node tools/check-mirror.js [path-to-sibling-repo] [--tol 0.22] [--file NN]
//
// The two repos are strict 1:1 line mirrors (synopsis/ ↔ конспект/, essays/ ↔ очерки/).
// Line-count parity is already checked elsewhere and is not sufficient: content can diverge
// *inside* a line while the counts stay equal, which is invisible to every parity check the
// project ran for thirteen rounds. Two complementary audits are needed, and neither suffices:
//
//   1. Cross-reference multiset — the bag of §NN pointers on each line must match. Catches
//      wrong and missing pointers. Blind to length-only loss (a dropped guardrail that
//      happens to cite nothing).
//   2. Length ratio — each line's translated/source character ratio, against that file's own
//      median ratio. Catches dropped qualifications and guardrails. Blind to divergence where
//      the two lengths happen to coincide.
//
// Exit 0 = no structural divergence, 1 = line-count or cross-reference divergence.
// Ratio outliers are advisory: they are candidates for reading, not defects by themselves.

const fs = require('fs');
const path = require('path');

const repo = path.join(__dirname, '..');

const args = process.argv.slice(2);
const optOf = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
};
const tol = parseFloat(optOf('--tol', '0.22'));
const onlyFile = optOf('--file', null);
const siblingArg = args.find(a => !a.startsWith('--') && args[args.indexOf(a) - 1] !== '--tol' && args[args.indexOf(a) - 1] !== '--file');

// Lines below this length are skipped by the ratio audit: headings and one-clause lines have
// natural variance far wider than the signal we are looking for.
const MIN_LEN = 60;

// Pair the content directories by role. Either repo may be the one we are run from.
const PAIRS = [['synopsis', 'конспект'], ['essays', 'очерки']];

const siblingCandidates = siblingArg
  ? [path.resolve(siblingArg)]
  : [path.join(repo, '..', 'nauka-logiki'), path.join(repo, '..', 'science-of-logic')];

const sibling = siblingCandidates.find(p => fs.existsSync(p) && p !== repo);
if (!sibling) {
  console.error('Sibling repo not found. Pass its path: node tools/check-mirror.js ../nauka-logiki');
  process.exit(1);
}

// Installments key on their leading number (NN-…); essays on their leading date (YYYY-MM-DD-…).
const keyOf = f => {
  const d = f.match(/^\d{4}-\d{2}-\d{2}/);
  if (d) return d[0];
  const n = f.match(/^(\d+)/);
  return n ? n[1] : f;
};
const readLines = p => fs.readFileSync(p, 'utf8').replace(/\r\n/g, '\n').split('\n');
const refsOf = line => (line.match(/§\s*\d{2}/g) || []).map(s => s.replace(/\s+/g, '')).sort();
const median = xs => {
  const s = [...xs].sort((a, b) => a - b);
  if (!s.length) return 0;
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};

let structural = 0;
let advisory = 0;

for (const [aName, bName] of PAIRS) {
  // Work out which side lives here and which lives in the sibling.
  let srcDir = path.join(repo, aName), dstDir = path.join(sibling, bName);
  if (!fs.existsSync(srcDir) || !fs.existsSync(dstDir)) {
    srcDir = path.join(repo, bName); dstDir = path.join(sibling, aName);
  }
  if (!fs.existsSync(srcDir) || !fs.existsSync(dstDir)) continue;

  const srcFiles = fs.readdirSync(srcDir).filter(f => /^\d+.*\.md$/.test(f)).sort();
  const dstFiles = fs.readdirSync(dstDir).filter(f => /^\d+.*\.md$/.test(f));
  const dstByNum = new Map(dstFiles.map(f => [keyOf(f), f]));

  for (const sf of srcFiles) {
  const n = keyOf(sf);
    if (onlyFile && n !== onlyFile.padStart(2, '0')) continue;

    const df = dstByNum.get(n);
    if (!df) { console.log(`  ✗ ${sf}: no mirror in ${path.basename(sibling)}/${path.basename(dstDir)}`); structural++; continue; }

    const srcLines = readLines(path.join(srcDir, sf));
    const dstLines = readLines(path.join(dstDir, df));

    if (srcLines.length !== dstLines.length) {
      console.log(`  ✗ ${sf}: ${srcLines.length} lines vs ${dstLines.length} in mirror`);
      structural++;
      continue;
    }

    // Audit 1 — cross-reference multiset.
    const xrefHits = [];
    for (let i = 0; i < srcLines.length; i++) {
      const a = refsOf(srcLines[i]).join(' ');
      const b = refsOf(dstLines[i]).join(' ');
      if (a !== b) xrefHits.push({ line: i + 1, a: a || '—', b: b || '—' });
    }

    // Audit 2 — per-line length ratio against this file's own median ratio.
    const ratios = [];
    for (let i = 0; i < srcLines.length; i++) {
      const s = srcLines[i].trim(), d = dstLines[i].trim();
      if (s.length < MIN_LEN || /^#/.test(s)) continue;
      ratios.push({ line: i + 1, r: d.length / s.length, sLen: s.length, dLen: d.length });
    }
    const med = median(ratios.map(x => x.r));
    const ratioHits = ratios.filter(x => med > 0 && Math.abs(x.r - med) / med > tol);

    if (xrefHits.length || ratioHits.length) {
      console.log(`\n  ${sf}   (median ratio ${med.toFixed(2)})`);
      for (const h of xrefHits) {
        console.log(`    ✗ :${h.line}  refs differ — source [${h.a}]  mirror [${h.b}]`);
        structural++;
      }
      for (const h of ratioHits) {
        const dir = h.r < med ? 'mirror shorter' : 'mirror longer';
        console.log(`    · :${h.line}  ratio ${h.r.toFixed(2)} vs ${med.toFixed(2)} — ${dir} (${h.sLen}→${h.dLen})`);
        advisory++;
      }
    }
  }
}

console.log('');
if (structural) {
  console.log(`FAIL — ${structural} structural divergence(s); ${advisory} ratio outlier(s) to read.`);
  process.exit(1);
}
console.log(`PASS — no structural divergence; ${advisory} ratio outlier(s) to read.`);
