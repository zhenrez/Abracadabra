/** Bounded comparison contract, selected by live Jev receipt39. No ontology is imposed. */
import { createHash } from 'node:crypto';
import { evaluateCandidates } from './law.js';
function object(value, label) {
    if (!value || typeof value !== 'object' || Array.isArray(value))
        throw new TypeError(`${label} must be an object`);
    return value;
}
function text(value, label) {
    if (typeof value !== 'string' || !value.trim() || value.length > 1000)
        throw new TypeError(`${label} must be nonempty text of at most 1,000 characters`);
    return value;
}
function references(value, label) {
    if (!Array.isArray(value) || value.length > 128)
        throw new TypeError(`${label} must be an array of at most 128 source IDs`);
    return value.map(v => text(v, label));
}
function jsonValue(value, depth = 0) {
    if (depth > 32)
        throw new TypeError('JSON value exceeds the bounded nesting depth');
    if (value === null || typeof value === 'string' || typeof value === 'boolean')
        return value;
    if (typeof value === 'number' && Number.isFinite(value))
        return value;
    if (Array.isArray(value))
        return value.map(v => jsonValue(v, depth + 1));
    const obj = object(value, 'JSON value');
    const out = Object.create(null);
    for (const [key, item] of Object.entries(obj))
        out[key] = jsonValue(item, depth + 1);
    return out;
}
function predicate(value, depth = 0) {
    if (depth > 16)
        throw new TypeError('Predicate nesting exceeds 16 levels');
    const p = object(value, 'predicate');
    switch (p.op) {
        case 'eq':
        case 'neq': return { op: p.op, key: text(p.key, 'predicate key'), value: jsonValue(p.value) };
        case 'in': {
            if (!Array.isArray(p.values) || p.values.length > 128)
                throw new TypeError('in requires at most 128 declared values');
            return { op: 'in', key: text(p.key, 'predicate key'), values: p.values.map(v => jsonValue(v)) };
        }
        case 'ratio': {
            const expected = object(p.expected, 'expected ratio');
            const numerator = text(expected.numerator, 'ratio numerator'), denominator = text(expected.denominator, 'ratio denominator');
            if (!/^-?\d+$/.test(numerator) || !/^-?\d+$/.test(denominator) || BigInt(denominator) === 0n)
                throw new TypeError('Exact ratios require integer strings and a nonzero denominator');
            return { op: 'ratio', numeratorKey: text(p.numeratorKey, 'numerator key'), denominatorKey: text(p.denominatorKey, 'denominator key'), expected: { numerator, denominator } };
        }
        case 'allDifferent': return { op: 'allDifferent', keys: references(p.keys, 'assignment keys') };
        case 'all':
        case 'any': {
            if (!Array.isArray(p.predicates) || p.predicates.length > 128)
                throw new TypeError('A compound predicate needs at most 128 members');
            return { op: p.op, predicates: p.predicates.map(v => predicate(v, depth + 1)) };
        }
        case 'unknown': return { op: 'unknown', reason: text(p.reason, 'unknown reason') };
        case 'custom': return { op: 'custom', name: text(p.name, 'custom operator name'), payload: jsonValue(p.payload) };
        default: throw new TypeError('Unknown predicate representation; use custom for an undeclared operator');
    }
}
export function parseComparison(value) {
    const body = object(value, 'comparison');
    if (Buffer.byteLength(JSON.stringify(value), 'utf8') > 48000)
        throw new TypeError('Comparison exceeds 48,000 UTF-8 bytes');
    const k = object(body.kernel, 'kernel');
    const sha256 = text(k.sha256, 'kernel SHA-256');
    if (!/^[a-f0-9]{64}$/.test(sha256))
        throw new TypeError('kernel SHA-256 must contain 64 lowercase hexadecimal characters');
    const kernel = { id: text(k.id, 'kernel ID'), version: text(k.version, 'kernel version'), sha256, sourceRefs: references(k.sourceRefs, 'kernel source IDs') };
    if (!Array.isArray(body.candidates) || body.candidates.length < 1 || body.candidates.length > 128)
        throw new TypeError('Supply 1–128 explicit candidates');
    if (!Array.isArray(body.constraints) || body.constraints.length > 128)
        throw new TypeError('Supply at most 128 explicit constraints');
    const candidates = body.candidates.map(v => {
        const c = object(v, 'candidate');
        return { id: text(c.id, 'candidate ID'), assignment: jsonValue(object(c.assignment, 'candidate assignment')), sourceRefs: references(c.sourceRefs, 'candidate source IDs') };
    });
    const constraints = body.constraints.map(v => {
        const c = object(v, 'constraint');
        if (!['assumption', 'derived', 'source-assertion'].includes(String(c.authority)))
            throw new TypeError('Declare constraint authority as assumption, derived or source-assertion');
        return { id: text(c.id, 'constraint ID'), kernelSha256: text(c.kernelSha256, 'constraint kernel hash'), sourceRefs: references(c.sourceRefs, 'constraint source IDs'), authority: c.authority, predicate: predicate(c.predicate), ...(c.dependencyGroups === undefined ? {} : { dependencyGroups: references(c.dependencyGroups, 'dependency groups') }) };
    });
    for (const [items, label] of [[candidates, 'candidate'], [constraints, 'constraint']]) {
        if (new Set(items.map(v => v.id)).size !== items.length)
            throw new TypeError(`Duplicate ${label} IDs cannot be collapsed`);
    }
    return { kernel, candidates, constraints };
}
export function prepareComparison(value, lookup) {
    const input = parseComparison(value);
    const ids = [...new Set([...input.kernel.sourceRefs, ...input.candidates.flatMap(c => c.sourceRefs), ...input.constraints.flatMap(c => c.sourceRefs)])];
    const bindings = ids.map(id => ({ id, source: lookup(id) ?? null }));
    const missing = bindings.filter(b => !b.source).map(b => b.id);
    const kernelBound = bindings.some(b => input.kernel.sourceRefs.includes(b.id) && b.source?.sha256 === input.kernel.sha256);
    const everyRecordCited = input.kernel.sourceRefs.length > 0 && input.candidates.every(c => c.sourceRefs.length > 0) && input.constraints.every(c => c.sourceRefs.length > 0);
    const sourceBindings = { status: missing.length === 0 && kernelBound && everyRecordCited ? 'resolved' : 'unknown', missing, kernelBound, everyRecordCited, sources: bindings, semantics: 'Literal source-ID and kernel-byte-hash resolution only. Does not establish citation entailment, law authority or source independence.' };
    const inputSha256 = createHash('sha256').update(JSON.stringify(input)).digest('hex');
    const reviewRequest = {
        state: { goal: 'Select whether a bounded, conditional structural comparison should execute; no canonical promotion is permitted.', decision_scope: 'Eligibility of deterministic calculation only. The full source bodies and mathematical truth are not being adjudicated by this model request.', input_sha256: inputSha256, kernel: { id: input.kernel.id, version: input.kernel.version, sha256: input.kernel.sha256 }, candidate_count: input.candidates.length, constraint_count: input.constraints.length, source_binding_status: sourceBindings.status, missing_source_count: missing.length, kernel_hash_bound: kernelBound, rule: 'Unknown/missing source bindings or predicates must remain unknown. Preserve exact input, all candidates and witnesses.' },
        questions: [{ id: 'comparison_action', type: 'choice', question: 'Which action should apply to this declared conditional calculation?', options: { evaluate_conditional: 'Run only the exact supplied candidate/constraint calculation when literal source bindings are resolved; return unknown for missing bindings. Retain every witness and no canonical winner.', defer_review: 'Defer the calculation for further source/constraint review; retain the exact submitted input hash and model receipt without promoting any law.' } }],
    };
    return { input, inputSha256, sourceBindings, reviewRequest };
}
export function completeComparison(prepared, action) {
    const common = { inputSha256: prepared.inputSha256, sourceBindings: prepared.sourceBindings, canonicalPromotion: false, scope: 'Exact declared constraints and supplied candidate family only; not a universal correspondence or scientific truth certificate.' };
    if (action === 'defer_review')
        return { status: 'deferred', ...common, evaluation: null };
    if (action !== 'evaluate_conditional')
        throw new TypeError('No accepted live Jev calculation action was supplied');
    if (prepared.sourceBindings.status !== 'resolved')
        return { status: 'source_unresolved', ...common, evaluation: null };
    return { status: 'evaluated', ...common, evaluation: evaluateCandidates(prepared.input.candidates, prepared.input.constraints, prepared.input.kernel) };
}
