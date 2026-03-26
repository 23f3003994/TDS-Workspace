const fs = require("fs");
const path = require("path");

// ---- LOAD FILES ----
const corpusText = fs.readFileSync(path.join(__dirname, "corpus.txt"), "utf8");
const csvText = fs.readFileSync(path.join(__dirname, "questions.csv"), "utf8");

// ---- REFERENCE FUNCTIONS ----
function tokenize(text) {
  return text.toLowerCase().replace(/[^a-z0-9\s]/g, " ")
             .trim().split(/\s+/).filter(w => w.length > 0);
}

function ngrams(tokens, n) {
  const s = new Set();
  for (let i = 0; i <= tokens.length - n; i++)
    s.add(tokens.slice(i, i + n).join(" "));
  return s;
}

function overlapScore(question, corpusNgrams, n = 8) {
  const qt = tokenize(question);
  if (qt.length < n) return 0;
  const qg = ngrams(qt, n);
  let hits = 0;
  for (const g of qg) if (corpusNgrams.has(g)) hits++;
  return qg.size > 0 ? hits / qg.size : 0;
}

// ---- BUILD CORPUS NGRAM SET (once) ----
const corpusNgramSet = ngrams(tokenize(corpusText), 8);

// ---- PARSE CSV ----
const lines = csvText.trim().split("\n").slice(1); // skip header row
const questions = lines.map(line => {
  line = line.trim();
  // handle both quoted and unquoted question fields
  const match = line.match(/^"(.+)",(\d)$/) || line.match(/^(.+),(\d)$/);
  return {
    question: match[1],
    is_correct: parseInt(match[2])
  };
});

// ---- AUDIT EACH QUESTION ----
const threshold = 0.4;
let contaminated_count = 0;
let cleanCorrect = 0;
let cleanCount = 0;
let totalCorrect = 0;

questions.forEach(q => {
  const score = overlapScore(q.question, corpusNgramSet);
  const contaminated = score > threshold;

  totalCorrect += q.is_correct;

  if (contaminated) {
    contaminated_count++;
  } else {
    cleanCount++;
    cleanCorrect += q.is_correct;
  }
});

// ---- COMPUTE THREE VALUES ----
const N = questions.length;
const reported_accuracy = (totalCorrect / N * 100).toFixed(2);
const adjusted_accuracy = (cleanCorrect / cleanCount * 100).toFixed(2);

// ---- OUTPUT ----
console.log(`contaminated_count : ${contaminated_count}`);
console.log(`reported_accuracy  : ${reported_accuracy}%`);
console.log(`adjusted_accuracy  : ${adjusted_accuracy}%`);
console.log(`\nFinal Answer: ${contaminated_count}, ${reported_accuracy}, ${adjusted_accuracy}`);