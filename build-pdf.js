// Builds a single HTML file from all synopsis markdown parts.
// Run: npx -y -p markdown-it@14 node build-pdf.js
const fs = require('fs');
const path = require('path');
const MarkdownIt = require('markdown-it');

const md = new MarkdownIt({ html: true, linkify: true, typographer: true });

const synopsisDir = path.join(__dirname, 'synopsis');
const files = fs.readdirSync(synopsisDir)
  .filter(f => f.endsWith('.md'))
  .sort();

const sections = files.map((f, i) => {
  const src = fs.readFileSync(path.join(synopsisDir, f), 'utf8');
  const html = md.render(src);
  const breakStyle = i === 0 ? '' : ' style="page-break-before: always;"';
  return `<section${breakStyle} data-file="${f}">\n${html}\n</section>`;
}).join('\n');

const css = `
  @page { size: A4; margin: 22mm 20mm; }
  html { -webkit-print-color-adjust: exact; }
  body {
    font-family: "Georgia", "Cambria", "Times New Roman", serif;
    font-size: 11.5pt;
    line-height: 1.55;
    color: #1a1a1a;
    max-width: 100%;
    margin: 0;
  }
  h1, h2, h3, h4 {
    font-family: "Helvetica Neue", "Segoe UI", Arial, sans-serif;
    color: #111;
    line-height: 1.25;
  }
  h1 { font-size: 22pt; margin: 0 0 0.6em; border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }
  h2 { font-size: 16pt; margin-top: 1.4em; }
  h3 { font-size: 13pt; margin-top: 1.2em; }
  p { margin: 0.6em 0; text-align: justify; hyphens: auto; }
  blockquote {
    margin: 1em 0;
    padding: 0.4em 1em;
    border-left: 3px solid #888;
    color: #333;
    background: #f6f6f6;
  }
  code { font-family: "Consolas", "Menlo", monospace; font-size: 0.92em; background: #f2f2f2; padding: 0 0.25em; border-radius: 3px; }
  pre { background: #f2f2f2; padding: 0.8em; overflow: auto; border-radius: 4px; }
  hr { border: 0; border-top: 1px solid #bbb; margin: 1.6em 0; }
  ul, ol { margin: 0.5em 0 0.5em 1.4em; }
  a { color: #0b4b8f; text-decoration: none; }
  section { page-break-inside: auto; }
  h1, h2, h3 { page-break-after: avoid; }
  .cover {
    text-align: center;
    padding-top: 30vh;
    page-break-after: always;
  }
  .cover h1 { border: none; font-size: 30pt; }
  .cover .subtitle { font-style: italic; color: #555; margin-top: 1em; }
`;

const cover = `
<div class="cover">
  <h1>Hegel's Science of Logic</h1>
  <div class="subtitle">A Synopsis</div>
</div>`;

const htmlDoc = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Science of Logic — Synopsis</title>
<style>${css}</style>
</head>
<body>
${cover}
${sections}
</body>
</html>`;

const outPath = path.join(__dirname, 'synopsis.html');
fs.writeFileSync(outPath, htmlDoc, 'utf8');
console.log(`Wrote ${outPath} (${files.length} sections)`);
