/** Conditional consequences of the supplied family; no domain vocabulary or weights. */
import {evaluateCandidates, type Candidate, type Constraint, type Json, type Kernel} from './law.js';

export interface PredictionTarget {
  id: string;
  keys: string[];
  sourceRefs: string[];
}

function canonical(value: Json): string {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  return '{' + Object.keys(value).sort().map(k => JSON.stringify(k) + ':' + canonical(value[k]!)).join(',') + '}';
}

/**
 * Unknown constraints leave candidates possible. Missing target values prevent
 * unanimity. Agreement is a consequence of this explicit family and premises,
 * never evidence of family completeness, real-world truth, or actual blindness.
 */
export function predictOverCandidates(
  candidates: Candidate[], constraints: Constraint[], kernel: Kernel, targets: PredictionTarget[],
) {
  const evaluation = evaluateCandidates(candidates, constraints, kernel);
  const possible = new Set([...evaluation.admissible, ...evaluation.unresolved]);
  const retained = candidates.filter(c => possible.has(c.id));
  const seen = new Set<string>();
  const predictions = targets.map(target => {
    if (!target.id.trim() || seen.has(target.id)) throw new TypeError('prediction target IDs must be nonempty and unique');
    seen.add(target.id);
    if (target.keys.length === 0 || new Set(target.keys).size !== target.keys.length ||
        target.keys.some(k => !k.trim())) throw new TypeError('target keys must be nonempty and unique');
    const sourceBound = target.sourceRefs.length > 0 && target.sourceRefs.every(s => s.trim().length > 0);
    const missing: string[] = [];
    const alternatives = new Map<string, {value: Json[]; candidateIds: string[]}>();
    for (const candidate of retained) {
      if (!sourceBound || candidate.sourceRefs.length === 0 ||
          candidate.sourceRefs.some(s => !s.trim()) ||
          target.keys.some(key => !Object.hasOwn(candidate.assignment, key))) {
        missing.push(candidate.id);
        continue;
      }
      const value = target.keys.map(key => candidate.assignment[key]!);
      const key = canonical(value);
      const group = alternatives.get(key) ?? {value, candidateIds: []};
      group.candidateIds.push(candidate.id);
      alternatives.set(key, group);
    }
    const status = retained.length === 0 ? 'no-surviving-candidates'
      : !sourceBound || missing.length > 0 ? 'unknown'
      : alternatives.size === 1 ? 'determined-within-supplied-family' : 'alternatives';
    return {
      targetId: target.id, keys: [...target.keys], sourceRefs: [...target.sourceRefs],
      status, alternatives: [...alternatives.values()], missingCandidateIds: missing,
      sourceRefsSyntacticallyPresent: sourceBound,
    };
  });
  return {
    schema: 'sunny.conditional-prediction-set.v1',
    scope: 'supplied-family-and-declared-premises-only',
    evaluation, retainedCandidateIds: retained.map(c => c.id), predictions,
    familyCompleteness: 'not-established',
    sourceAuthenticity: 'requires-source-binding-audit',
    globalOrientationSelected: false, canonicalPromotion: false,
    blindPrediction: false, probability: null,
  };
}
