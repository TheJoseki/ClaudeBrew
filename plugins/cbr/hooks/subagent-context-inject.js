#!/usr/bin/env node
// subagent-context-inject.js — SubagentStart hook
// Auto-injects CAO (Context-Aware Orchestration) context into ClaudeKit agents.
// Ported from .claude/skills/context-inject/SKILL.md with scoring + token budget.
//
// Event: SubagentStart (matcher: .*-agent)
// Cannot block agent creation — inject only.
// Output: JSON { hookSpecificOutput: { hookEventName: "SubagentStart", additionalContext: "..." } }
//
// Scoring: domain_match(0.4) + recency(0.3) + importance(0.3)
// Token budget: ≤1500 tokens (~6000 chars)

const fs = require('fs');
const path = require('path');

const projectDir = process.env.CLAUDE_PROJECT_DIR || process.cwd();

// ─── Read stdin JSON ─────────────────────────────────────────────────────────
let rawInput = '';
try { rawInput = fs.readFileSync(0, 'utf8'); } catch { process.exit(0); }

let input;
try { input = JSON.parse(rawInput); } catch { process.exit(0); }

const agentType = input.agent_type || '';
if (!agentType || !agentType.endsWith('-agent')) process.exit(0);

// ─── Agent Role → Domain Mapping ─────────────────────────────────────────────
const AGENT_DOMAINS = {
  'orchestrator-agent':     ['all'],
  'ba-agent':               ['requirements', 'process', 'business'],
  'architect-agent':        ['schema', 'api', 'design', 'architecture'],
  'developer-agent':        ['implementation', 'code', 'testing'],
  'code-review-agent':      ['quality', 'security', 'code'],
  'unit-test-agent':        ['testing', 'code', 'quality'],
  'integration-test-agent': ['testing', 'api', 'e2e'],
  'bug-fix-agent':          ['debugging', 'code', 'testing'],
  'ui-designer-agent':      ['ui', 'design', 'frontend'],
  'security-tester-agent':  ['security', 'vulnerability'],
};

// Related domain clusters (for 0.5 partial match)
const RELATED_DOMAINS = {
  'auth': ['security', 'permission', 'api'],
  'api': ['schema', 'design', 'implementation'],
  'schema': ['api', 'design', 'architecture'],
  'testing': ['code', 'quality', 'debugging'],
  'security': ['vulnerability', 'auth', 'quality'],
  'design': ['architecture', 'ui', 'schema'],
  'code': ['implementation', 'quality', 'debugging'],
  'ui': ['design', 'frontend'],
  'frontend': ['ui', 'design'],
};

// Backlog types per agent role (from skill Step 3)
const BACKLOG_TYPES = {
  'developer-agent':        ['CODE_QUALITY', 'DESIGN_DEBT'],
  'code-review-agent':      null, // all types
  'unit-test-agent':        ['CODE_QUALITY', 'BUG_DEFERRED'],
  'integration-test-agent': ['CODE_QUALITY', 'BUG_DEFERRED'],
  'security-tester-agent':  ['SECURITY'],
  'architect-agent':        ['DESIGN_DEBT', 'PROCESS'],
  'ba-agent':               ['PROCESS', 'DESIGN_DEBT'],
  'orchestrator-agent':     null, // all types
  'bug-fix-agent':          ['CODE_QUALITY', 'BUG_DEFERRED'],
  'ui-designer-agent':      ['DESIGN_DEBT'],
};

const agentDomains = AGENT_DOMAINS[agentType] || [];
const isAll = agentDomains.includes('all');
const TOKEN_BUDGET = 1500; // ~6000 chars
const CHAR_BUDGET = TOKEN_BUDGET * 4;

// ─── Scoring Function ────────────────────────────────────────────────────────
function scoreDecision(decision) {
  // Domain match
  let domainMatch = 0;
  if (isAll) {
    domainMatch = 1.0;
  } else if (decision.domain) {
    const dLower = decision.domain.toLowerCase();
    if (agentDomains.some(d => dLower.includes(d))) {
      domainMatch = 1.0;
    } else if (agentDomains.some(d => (RELATED_DOMAINS[d] || []).some(r => dLower.includes(r)))) {
      domainMatch = 0.5;
    }
  }

  // Recency
  let recency = 0.3;
  if (decision.date) {
    const daysSince = (Date.now() - decision.date.getTime()) / 86400000;
    recency = daysSince < 1 ? 1.0 : daysSince < 3 ? 0.7 : daysSince < 7 ? 0.5 : 0.3;
  }

  // Importance
  const status = (decision.status || '').toUpperCase();
  const importance = status.includes('CONTESTED') ? 1.0 :
                     status.includes('ACTIVE') ? 0.7 : 0.3;

  return domainMatch * 0.4 + recency * 0.3 + importance * 0.3;
}

// ─── Parse Decision Ledger ───────────────────────────────────────────────────
function parseDecisions(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, 'utf8');
  const decisions = [];

  // Parse ### D-XXX entries
  const blocks = content.split(/^### /m).slice(1);
  for (const block of blocks) {
    const lines = block.split('\n');
    const id = lines[0]?.trim() || '';
    if (!id.startsWith('D-')) continue;

    let status = '', domain = '', date = null, summary = '';

    for (const line of lines.slice(1, 10)) {
      const l = line.trim();
      if (l.startsWith('status:')) status = l.replace('status:', '').trim();
      else if (l.startsWith('domain:')) domain = l.replace('domain:', '').trim();
      else if (l.startsWith('date:')) {
        const d = new Date(l.replace('date:', '').trim());
        if (!isNaN(d.getTime())) date = d;
      }
      else if (l && !l.startsWith('---') && !summary) summary = l;
    }

    decisions.push({ id, status, domain, date, summary: summary.slice(0, 120) });
  }
  return decisions;
}

// ─── Parse Backlog Registry ──────────────────────────────────────────────────
function parseBacklog(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, 'utf8');
  const items = [];

  const blocks = content.split(/^### /m).slice(1);
  const allowedTypes = BACKLOG_TYPES[agentType];

  for (const block of blocks) {
    const lines = block.split('\n');
    const id = lines[0]?.trim() || '';

    let type = '', priority = '', status = '', summary = '';

    for (const line of lines.slice(1, 8)) {
      const l = line.trim();
      if (l.startsWith('type:')) type = l.replace('type:', '').trim();
      else if (l.startsWith('priority:')) priority = l.replace('priority:', '').trim();
      else if (l.startsWith('status:')) status = l.replace('status:', '').trim();
      else if (l && !l.startsWith('---') && !summary) summary = l;
    }

    // Filter: OPEN only, matching types
    if (!status.includes('OPEN')) continue;
    if (allowedTypes && !allowedTypes.some(t => type.toUpperCase().includes(t))) continue;

    items.push({ id, type, priority, summary: summary.slice(0, 100) });
  }

  // Sort: HIGH first, then MEDIUM, then LOW
  const pOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
  items.sort((a, b) => (pOrder[a.priority?.toUpperCase()] ?? 3) - (pOrder[b.priority?.toUpperCase()] ?? 3));

  return items.slice(0, 5);
}

// ─── Parse Project Memory ────────────────────────────────────────────────────
function parseMemory(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, 'utf8');
  const entries = [];

  // Simple: extract non-empty, non-header, non-frontmatter lines
  const lines = content.split('\n').filter(l =>
    l.trim() && !l.startsWith('#') && !l.startsWith('---') && !l.startsWith('|')
  );

  for (const line of lines.slice(0, 20)) {
    const trimmed = line.trim().replace(/^[-*]\s*/, '');
    if (trimmed.length > 10) {
      entries.push(trimmed.slice(0, 150));
    }
  }

  return entries.slice(0, 5);
}

// ─── Active Plan Summary ─────────────────────────────────────────────────────
function getActivePlan() {
  const plansDir = path.join(projectDir, 'docs', 'plans');
  if (!fs.existsSync(plansDir)) return null;

  try {
    const files = fs.readdirSync(plansDir).filter(f => f.startsWith('PLAN-') && f.endsWith('.md'));
    for (const f of files) {
      const content = fs.readFileSync(path.join(plansDir, f), 'utf8');
      if (content.includes('status: ACTIVE')) {
        const feature = content.match(/feature:\s*(.+)/)?.[1]?.trim() || 'unknown';
        const phase = content.match(/⏳.*$/m)?.[0]?.trim() || 'N/A';
        return { file: f, feature, phase };
      }
    }
  } catch {}
  return null;
}

// ─── Main ────────────────────────────────────────────────────────────────────
try {
  const sections = [];

  // 1. Active Plan
  const plan = getActivePlan();
  if (plan) {
    sections.push(`[PLAN] ${plan.file} | Feature: ${plan.feature} | Phase: ${plan.phase}`);
  }

  // 2. Decisions (scored, top 10)
  const ledgerPath = path.join(projectDir, 'docs', 'plans', 'DECISION-LEDGER.md');
  const allDecisions = parseDecisions(ledgerPath);

  // Score and sort
  const scored = allDecisions.map(d => ({ ...d, score: scoreDecision(d) }));
  scored.sort((a, b) => b.score - a.score);

  // CONTESTED always first (regardless of score)
  const contested = scored.filter(d => d.status.toUpperCase().includes('CONTESTED'));
  const others = scored.filter(d => !d.status.toUpperCase().includes('CONTESTED'));
  const topDecisions = [...contested, ...others].slice(0, 10);

  if (topDecisions.length > 0) {
    const dLines = topDecisions.map(d => {
      const emoji = d.status.includes('CONTESTED') ? '⚠️' : d.status.includes('ACTIVE') ? '✅' : '❌';
      return `  ${emoji} ${d.id}: ${d.summary} [${d.domain || 'N/A'}]`;
    });
    sections.push(`[DECISIONS] ${topDecisions.length} relevant:\n${dLines.join('\n')}`);
  }

  // 3. Backlog (filtered by role, top 5)
  const backlogPath = path.join(projectDir, 'docs', 'plans', 'BACKLOG-REGISTRY.md');
  const backlogItems = parseBacklog(backlogPath);

  if (backlogItems.length > 0) {
    const bLines = backlogItems.map(b => `  [${b.priority}] ${b.id}: ${b.summary} (${b.type})`);
    sections.push(`[BACKLOG] ${backlogItems.length} open items:\n${bLines.join('\n')}`);
  }

  // 4. Project Memory (top 5)
  const memoryPath = path.join(projectDir, 'docs', 'memory', 'PROJECT-MEMORY.md');
  const memoryEntries = parseMemory(memoryPath);

  if (memoryEntries.length > 0) {
    const mLines = memoryEntries.map(m => `  - ${m}`);
    sections.push(`[PROJECT-MEMORY]\n${mLines.join('\n')}`);
  }

  // Nothing to inject
  if (sections.length === 0) process.exit(0);

  // ─── Token Budget Enforcement ──────────────────────────────────────────────
  let context = `== CAO Context (auto-injected for ${agentType}) ==\n${sections.join('\n\n')}\n== END CAO ==`;

  if (context.length > CHAR_BUDGET) {
    // Downsize: reduce memory to 3, decisions to 5, backlog to 3
    const reducedSections = [];
    if (plan) reducedSections.push(`[PLAN] ${plan.file} | ${plan.feature} | ${plan.phase}`);
    if (topDecisions.length > 0) {
      const top5 = [...contested, ...others].slice(0, 5);
      reducedSections.push(`[DECISIONS] ${top5.map(d => `${d.id}: ${d.summary}`).join('; ')}`);
    }
    if (backlogItems.length > 0) {
      reducedSections.push(`[BACKLOG] ${backlogItems.slice(0, 3).map(b => `${b.id}(${b.priority})`).join(', ')}`);
    }
    if (memoryEntries.length > 0) {
      reducedSections.push(`[MEMORY] ${memoryEntries.slice(0, 3).join('; ')}`);
    }
    context = `== CAO Context (auto-injected, budget-reduced) ==\n${reducedSections.join('\n')}\n== END CAO ==`;
  }

  // Final truncation safety net
  if (context.length > CHAR_BUDGET) {
    context = context.slice(0, CHAR_BUDGET - 20) + '\n... [truncated for budget]';
  }

  // ─── Output JSON ───────────────────────────────────────────────────────────
  const output = {
    hookSpecificOutput: {
      hookEventName: 'SubagentStart',
      additionalContext: context
    }
  };

  process.stdout.write(JSON.stringify(output));
  process.stderr.write(`[subagent-context-inject] Injected ${context.length} chars for ${agentType}\n`);

} catch (err) {
  process.stderr.write(`[subagent-context-inject] Error: ${err.message}\n`);
  process.exit(0); // Don't block agent on error
}
