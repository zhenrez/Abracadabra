/** A small, open constraint representation; no domain ontology or weights are prescribed. */
export type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
export type Verdict = 'pass' | 'fail' | 'unknown';
export interface Rational { numerator: string; denominator: string }
export interface Kernel {
  id: string;
  version: string;
  sha256: string;
  sourceRefs: string[];
}
export interface Candidate {
  id: string;
  assignment: Record<string, Json>;
  sourceRefs: string[];
}
export type Predicate =
  | { op: 'eq' | 'neq'; key: string; value: Json }
  | { op: 'in'; key: string; values: Json[] }
  | { op: 'ratio'; numeratorKey: string; denominatorKey: string; expected: Rational }
  | { op: 'allDifferent'; keys: string[] }
  | { op: 'all' | 'any'; predicates: Predicate[] }
  | { op: 'unknown'; reason: string }
  | { op: 'custom'; name: string; payload: Json };
export interface Constraint {
  id: string;
  kernelSha256: string;
  sourceRefs: string[];
  dependencyGroups?: string[];
  authority: 'assumption' | 'derived' | 'source-assertion';
  predicate: Predicate;
}
export interface Witness {
  verdict: Verdict;
  reason: string;
  keys: string[];
  constraintId?: string;
  sourceRefs?: string[];
  dependencyGroups?: string[];
  authority?: Constraint['authority'];
  children?: Witness[];
}

/** A discovered vocabulary is data, not a list of domain types hard-coded in TS. */
export interface LawProposal {
  id: string;
  revision: string;
  expression: Json;
  assumptions: string[];
  sourceRefs: string[];
  dependencies: { id: string; revision: string }[];
  status: 'candidate' | 'conditional' | 'supported' | 'superseded' | 'retracted';
}

/** Checks the declared revision graph; status labels are never proof certificates. */
export function checkLawDependencies(laws: LawProposal[]) {
  const revisionKey = (law: { id: string; revision: string }) => JSON.stringify([law.id, law.revision]);
  const byRevision = new Map<string, LawProposal>();
  for (const law of laws) {
    id(law.id, 'law id'); id(law.revision, 'law revision');
    const key = revisionKey(law);
    if (byRevision.has(key)) throw new TypeError(`duplicate law revision: ${key}`);
    byRevision.set(key, law);
  }
  const unresolved: { law: string; dependency: string }[] = [];
  const unsupported: string[] = [];
  const cycles: string[][] = [];
  const visited = new Set<string>();
  const path: string[] = [];
  const visit = (key: string): void => {
    const inPath = path.indexOf(key);
    if (inPath !== -1) { cycles.push([...path.slice(inPath), key]); return; }
    if (visited.has(key)) return;
    const law = byRevision.get(key)!;
    if (!refs(law.sourceRefs)) unsupported.push(key);
    path.push(key);
    for (const dependency of law.dependencies) {
      const dependencyKey = revisionKey(dependency);
      if (!byRevision.has(dependencyKey)) unresolved.push({ law: key, dependency: dependencyKey });
      else visit(dependencyKey);
    }
    path.pop();
    visited.add(key);
  };
  for (const key of byRevision.keys()) visit(key);
  return {
    verdict: cycles.length > 0 ? 'fail' : unresolved.length > 0 || unsupported.length > 0 ? 'unknown' : 'pass',
    scope: 'declared-revision-graph-only', unresolved, unsupported, cycles,
    canonicalPromotion: false,
  };
}

export interface PredictionCase {
  id: string;
  probability: number;
  baselineProbability: number;
  observed: boolean;
  frozenAt: string;
  observedAt: string;
  referenceExposure: 'unseen' | 'seen' | 'unknown';
  trainingGroups: string[];
  referenceGroup: string;
  sourceRefs: string[];
}

/** Descriptive scoring of declared held-out records; no significance or calibration claim. */
export function scorePredictionBatch(cases: PredictionCase[]) {
  uniqueIds(cases, 'prediction');
  const excluded: { id: string; reasons: string[] }[] = [];
  const scored: { id: string; brier: number; baselineBrier: number; referenceGroup: string }[] = [];
  for (const item of cases) {
    const reasons: string[] = [];
    if (![item.probability, item.baselineProbability].every(p => Number.isFinite(p) && p >= 0 && p <= 1)) reasons.push('probability is outside [0,1]');
    if (typeof item.observed !== 'boolean') reasons.push('binary observation is missing');
    const frozenAt = Date.parse(item.frozenAt), observedAt = Date.parse(item.observedAt);
    if (!Number.isFinite(frozenAt) || !Number.isFinite(observedAt) || frozenAt >= observedAt) reasons.push('declared freeze must precede observation');
    if (item.referenceExposure !== 'unseen') reasons.push('reference was seen or exposure is unknown');
    if (!item.referenceGroup || item.trainingGroups.includes(item.referenceGroup)) reasons.push('reference group is missing or overlaps training groups');
    if (!refs(item.sourceRefs)) reasons.push('prediction record source is unresolved');
    if (reasons.length > 0) excluded.push({ id: item.id, reasons });
    else {
      const y = Number(item.observed);
      scored.push({ id: item.id, brier: (item.probability - y) ** 2, baselineBrier: (item.baselineProbability - y) ** 2, referenceGroup: item.referenceGroup });
    }
  }
  const count = scored.length;
  const meanBrier = count > 0 ? scored.reduce((sum, item) => sum + item.brier, 0) / count : null;
  const meanBaselineBrier = count > 0 ? scored.reduce((sum, item) => sum + item.baselineBrier, 0) / count : null;
  return {
    schema: 'sunny.binary-prediction-score.v1',
    count, totalSubmitted: cases.length, excluded, scored,
    meanBrier, meanBaselineBrier,
    improvement: meanBrier === null || meanBaselineBrier === null ? null : meanBaselineBrier - meanBrier,
    referenceGroups: [...new Set(scored.map(item => item.referenceGroup))],
    aggregation: 'one-vote-per-case; repeated reference groups are not independent evidence',
    actualBlindness: 'not-established-by-declared-metadata',
    calibration: 'not-established', statisticalSignificance: 'not-tested', canonicalPromotion: false,
  };
}

function id(value: unknown, name: string): asserts value is string {
  if (typeof value !== 'string' || value.trim() === '') throw new TypeError(`${name} is required`);
}
function uniqueIds(items: readonly { id: string }[], name: string): void {
  const seen = new Set<string>();
  for (const item of items) {
    id(item.id, `${name} id`);
    if (seen.has(item.id)) throw new TypeError(`duplicate ${name} id: ${item.id}`);
    seen.add(item.id);
  }
}
function refs(value: unknown): value is string[] {
  return Array.isArray(value) && value.length > 0 && value.every(x => typeof x === 'string' && x.trim() !== '');
}
function jsonValid(value: unknown, seen = new Set<unknown>(), depth = 0): value is Json {
  if (depth > 64) return false;
  if (value === null || typeof value === 'boolean' || typeof value === 'string') return true;
  if (typeof value === 'number') return Number.isFinite(value);
  if (typeof value !== 'object' || seen.has(value)) return false;
  const proto = Object.getPrototypeOf(value);
  if (!Array.isArray(value) && proto !== Object.prototype && proto !== null) return false;
  seen.add(value);
  const valid = Object.values(value).every(v => jsonValid(v, seen, depth + 1));
  seen.delete(value);
  return valid;
}
function canonical(value: Json): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k]!)}`).join(',')}}`;
}
function integer(value: number | string | bigint): bigint {
  if (typeof value === 'bigint') return value;
  if (typeof value === 'number' && !Number.isSafeInteger(value)) throw new TypeError('integer must be safe or supplied as a decimal string');
  if (typeof value === 'string' && !/^-?\d+$/.test(value)) throw new TypeError('invalid integer string');
  return BigInt(value);
}
export function rational(numerator: number | string | bigint, denominator: number | string | bigint): Rational {
  let n = integer(numerator);
  let d = integer(denominator);
  if (d === 0n) throw new RangeError('zero rational denominator');
  if (d < 0n) { n = -n; d = -d; }
  let a = n < 0n ? -n : n;
  let b = d;
  while (b !== 0n) { const remainder = a % b; a = b; b = remainder; }
  return { numerator: String(n / a), denominator: String(d / a) };
}
function asRational(value: Json): Rational {
  if (typeof value === 'number' || typeof value === 'string') return rational(value, 1);
  if (value && typeof value === 'object' && !Array.isArray(value) &&
      typeof value.numerator === 'string' && typeof value.denominator === 'string') {
    return rational(value.numerator, value.denominator);
  }
  throw new TypeError('ratio requires exact integers or explicit rational objects');
}
const unknown = (reason: string, keys: string[] = []): Witness => ({ verdict: 'unknown', reason, keys });

/** Custom predicates are retained as unknown until a versioned evaluator is implemented. */
export function evaluatePredicate(predicate: Predicate, assignment: Record<string, Json>, depth = 0): Witness {
  if (depth === 0 && !jsonValid(assignment)) return unknown('assignment is not finite JSON');
  if (depth > 32) return unknown('predicate nesting exceeds 32');
  const has = (key: string) => Object.hasOwn(assignment, key);
  switch (predicate.op) {
    case 'eq': case 'neq': {
      if (!has(predicate.key)) return unknown('assignment is missing', [predicate.key]);
      if (!jsonValid(predicate.value)) return unknown('comparison value is not finite JSON', [predicate.key]);
      const same = canonical(assignment[predicate.key]!) === canonical(predicate.value);
      const passed = predicate.op === 'eq' ? same : !same;
      return { verdict: passed ? 'pass' : 'fail', reason: `exact ${predicate.op} comparison`, keys: [predicate.key] };
    }
    case 'in': {
      if (!has(predicate.key)) return unknown('assignment is missing', [predicate.key]);
      if (!Array.isArray(predicate.values) || !predicate.values.every(v => jsonValid(v))) return unknown('membership values are invalid', [predicate.key]);
      return { verdict: predicate.values.some(v => canonical(v) === canonical(assignment[predicate.key]!)) ? 'pass' : 'fail', reason: 'exact membership comparison', keys: [predicate.key] };
    }
    case 'ratio': {
      const keys = [predicate.numeratorKey, predicate.denominatorKey];
      if (!keys.every(has)) return unknown('ratio assignment is missing', keys);
      try {
        const a = asRational(assignment[predicate.numeratorKey]!);
        const b = asRational(assignment[predicate.denominatorKey]!);
        const actual = rational(BigInt(a.numerator) * BigInt(b.denominator), BigInt(a.denominator) * BigInt(b.numerator));
        const expected = rational(predicate.expected.numerator, predicate.expected.denominator);
        return { verdict: canonical(actual as unknown as Json) === canonical(expected as unknown as Json) ? 'pass' : 'fail', reason: `exact ratio ${actual.numerator}/${actual.denominator}; expected ${expected.numerator}/${expected.denominator}`, keys };
      } catch (error) { return unknown(`undefined exact ratio: ${error instanceof Error ? error.message : String(error)}`, keys); }
    }
    case 'allDifferent': {
      if (predicate.keys.length === 0 || new Set(predicate.keys).size !== predicate.keys.length) return unknown('allDifferent needs distinct nonempty keys', predicate.keys);
      if (!predicate.keys.every(has)) return unknown('assignment is missing', predicate.keys);
      const values = predicate.keys.map(k => canonical(assignment[k]!));
      return { verdict: new Set(values).size === values.length ? 'pass' : 'fail', reason: 'exact distinctness comparison', keys: [...predicate.keys] };
    }
    case 'all': case 'any': {
      if (predicate.predicates.length === 0) return unknown('empty predicate group is not evidential support');
      const children = predicate.predicates.map(p => evaluatePredicate(p, assignment, depth + 1));
      const statuses = children.map(x => x.verdict);
      const verdict = predicate.op === 'all'
        ? statuses.includes('fail') ? 'fail' : statuses.includes('unknown') ? 'unknown' : 'pass'
        : statuses.includes('pass') ? 'pass' : statuses.includes('unknown') ? 'unknown' : 'fail';
      return { verdict, reason: `three-valued ${predicate.op}`, keys: [...new Set(children.flatMap(c => c.keys))], children };
    }
    case 'unknown': return unknown(predicate.reason);
    case 'custom': return unknown(`custom operator not evaluated: ${predicate.name}`);
    default: return unknown('unsupported predicate operator');
  }
}

/** Exhaustive only over this explicit supplied family, conditional on these constraints. */
export function evaluateCandidates(candidates: Candidate[], constraints: Constraint[], kernel: Kernel) {
  id(kernel.id, 'kernel id'); id(kernel.version, 'kernel version');
  if (!/^[a-fA-F0-9]{64}$/.test(kernel.sha256) || !refs(kernel.sourceRefs)) throw new TypeError('kernel requires a SHA256 and source references');
  uniqueIds(candidates, 'candidate'); uniqueIds(constraints, 'constraint');
  const results = candidates.map(candidate => {
    if (!jsonValid(candidate.assignment) || Array.isArray(candidate.assignment) || candidate.assignment === null) throw new TypeError(`invalid candidate assignment: ${candidate.id}`);
    const witnesses = constraints.map(constraint => {
      let witness: Witness;
      if (!refs(candidate.sourceRefs)) witness = unknown('candidate has no source or derivation references');
      else if (constraint.kernelSha256.toLowerCase() !== kernel.sha256.toLowerCase()) witness = unknown('constraint belongs to a different kernel');
      else if (!refs(constraint.sourceRefs)) witness = unknown('constraint source is unresolved');
      else witness = evaluatePredicate(constraint.predicate, candidate.assignment);
      return { ...witness, constraintId: constraint.id, sourceRefs: [...(constraint.sourceRefs ?? [])], authority: constraint.authority, dependencyGroups: [...(constraint.dependencyGroups ?? [])] };
    });
    const status = witnesses.some(w => w.verdict === 'fail') ? 'rejected'
      : witnesses.length === 0 || witnesses.some(w => w.verdict === 'unknown') ? 'unresolved' : 'admissible';
    return { candidateId: candidate.id, status, witnesses };
  });
  return {
    schema: 'sunny.constraint-evaluation.v1', kernel: { ...kernel, sourceRefs: [...kernel.sourceRefs] },
    scope: 'supplied-candidate-family-only', exhaustiveOverSuppliedCandidates: true,
    familyCompleteness: 'not-established', canonicalPromotion: false,
    admissible: results.filter(r => r.status === 'admissible').map(r => r.candidateId),
    rejected: results.filter(r => r.status === 'rejected').map(r => r.candidateId),
    unresolved: results.filter(r => r.status === 'unresolved').map(r => r.candidateId),
    results,
    // Repeated dependent statements never become separate confidence votes.
    dependencyGroups: [...new Set(constraints.flatMap(c => c.dependencyGroups ?? []))],
    probability: null,
  };
}

export interface OperatorSignature {
  id: string;
  domain: string[];
  codomain: string;
  invariants: string[];
  sourceRefs: string[];
}
export interface NativeSystem {
  id: string;
  revision: string;
  objectTypes: string[];
  operators: OperatorSignature[];
  sourceRefs: string[];
}
export interface Correspondence {
  id: string;
  fromSystemId: string;
  toSystemId: string;
  fromRevision: string;
  toRevision: string;
  objectMap: Record<string, string>;
  operatorMap: Record<string, string>;
  sourceRefs: string[];
  /** Explicit supplied evidence; checker does not turn name matches into dynamics. */
  witnesses: { fromOperator: string; toOperator: string; obligation: string; verdict: Verdict; sourceRefs: string[] }[];
}
export function checkComposition(first: OperatorSignature, second: OperatorSignature): Witness {
  if (!refs(first.sourceRefs) || !refs(second.sourceRefs)) return unknown('operator source is unresolved');
  if (second.domain.length !== 1) return unknown('multi-input composition requires an explicit substitution map');
  return {
    verdict: second.domain[0] === first.codomain ? 'pass' : 'fail',
    reason: `declared output ${first.codomain} to declared input ${second.domain[0]}`,
    keys: [first.id, second.id],
  };
}
export function checkCorrespondence(correspondence: Correspondence, systems: NativeSystem[]) {
  uniqueIds(systems, 'native system');
  const source = systems.find(s => s.id === correspondence.fromSystemId);
  const target = systems.find(s => s.id === correspondence.toSystemId);
  const checks: Witness[] = [];
  if (!source || !target) checks.push(unknown('native system is unresolved'));
  else if (source.revision !== correspondence.fromRevision || target.revision !== correspondence.toRevision) checks.push(unknown('native system revision mismatch'));
  else if (!refs(source.sourceRefs) || !refs(target.sourceRefs) || !refs(correspondence.sourceRefs)) checks.push(unknown('native grammar or correspondence source is unresolved'));
  else {
    uniqueIds(source.operators, 'source operator'); uniqueIds(target.operators, 'target operator');
    for (const [from, to] of Object.entries(correspondence.objectMap)) {
      checks.push({ verdict: source.objectTypes.includes(from) && target.objectTypes.includes(to) ? 'pass' : 'fail', reason: 'declared native object type exists', keys: [from, to] });
    }
    for (const [from, to] of Object.entries(correspondence.operatorMap)) {
      const a = source.operators.find(o => o.id === from);
      const b = target.operators.find(o => o.id === to);
      if (!a || !b) { checks.push({ verdict: 'fail', reason: 'mapped operator is absent from native grammar', keys: [from, to] }); continue; }
      if (!refs(a.sourceRefs) || !refs(b.sourceRefs)) { checks.push(unknown('mapped operator source is unresolved', [from, to])); continue; }
      const mappedDomain = a.domain.map(d => correspondence.objectMap[d]);
      const mappedCodomain = correspondence.objectMap[a.codomain];
      if (mappedDomain.some(d => d === undefined) || mappedCodomain === undefined) { checks.push(unknown('object mapping is incomplete for operator signature', [from, to])); continue; }
      checks.push({ verdict: mappedDomain.length === b.domain.length && mappedDomain.every((d, i) => d === b.domain[i]) && mappedCodomain === b.codomain ? 'pass' : 'fail', reason: 'declared domain/codomain signature commutes', keys: [from, to] });
      for (const obligation of ['dynamics', ...a.invariants.map(name => `invariant:${name}`)]) {
        const evidence = correspondence.witnesses.filter(w => w.fromOperator === from && w.toOperator === to && w.obligation === obligation);
        if (evidence.length === 0) checks.push(unknown(`missing ${obligation} witness`, [from, to]));
        else for (const witness of evidence) checks.push({ verdict: refs(witness.sourceRefs) ? witness.verdict : 'unknown', reason: `supplied ${obligation} witness (not independently proved by this checker)`, keys: [from, to], sourceRefs: [...witness.sourceRefs] });
      }
      for (const [nextFrom, nextTo] of Object.entries(correspondence.operatorMap)) {
        const nextA = source.operators.find(o => o.id === nextFrom);
        const nextB = target.operators.find(o => o.id === nextTo);
        if (!nextA || !nextB || nextA.domain.length !== 1 || nextA.domain[0] !== a.codomain) continue;
        checks.push(checkComposition(b, nextB));
        const obligation = `composition:${nextFrom}`;
        const evidence = correspondence.witnesses.filter(w => w.fromOperator === from && w.toOperator === to && w.obligation === obligation);
        if (evidence.length === 0) checks.push(unknown(`missing ${obligation} witness`, [from, to]));
        else for (const witness of evidence) checks.push({ verdict: refs(witness.sourceRefs) ? witness.verdict : 'unknown', reason: `supplied ${obligation} witness (not independently proved by this checker)`, keys: [from, to], sourceRefs: [...witness.sourceRefs] });
      }
    }
    if (Object.keys(correspondence.operatorMap).length === 0) checks.push(unknown('no operator mapping; shared counts or names alone do not check dynamics'));
  }
  return {
    correspondenceId: correspondence.id,
    verdict: checks.some(c => c.verdict === 'fail') ? 'fail' : checks.some(c => c.verdict === 'unknown') || checks.length === 0 ? 'unknown' : 'pass',
    scope: 'declared-signatures-and-supplied-witnesses-only',
    nativeSystemIds: [correspondence.fromSystemId, correspondence.toSystemId], checks,
    canonicalPromotion: false,
  };
}
