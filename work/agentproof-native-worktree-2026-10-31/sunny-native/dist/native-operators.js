/** Bounded source-native mechanisms. Execution is conditional on supplied data. */
import { createHash } from 'node:crypto';
import { rational } from './law.js';
export const NATIVE_GG_SHA256 = '6a92f9710fa6cd2937b9b07c42315b7d9c80644bd453c659f17318f95c55f95d';
const SCOPES = {
    'MEC-01': 'Exact positive rational scalar action; carrier/unit supplied. Irrational root extensions need a separate representation.',
    'MEC-02': 'Abstract D12 affine action on Z/12; PLR triad realization is not inferred from the abstract isomorphism.',
    'MEC-03': 'Exact reversal of a finite supplied sequence; fixed-point status is a predicate, not another generator.',
    'MEC-04': 'Only an explicitly admissible partial map preserving supplied object identity and shared pitch.',
    'MEC-05': 'Finite supplied cyclic index rotation; no native origin or historical mapping inferred.',
    'MEC-06': 'Exact mechanical Euclidean constructor modulo all cyclic rotations; no selected lawful phase.',
    'MEC-07': 'Boolean residue sieve restricted to the explicitly supplied finite integer universe.',
    'MEC-08': 'Explicit positive added duration, dot factor3/2 or supplied positive-duration inserted event; unit retained.',
    'MEC-09': 'Declared higher-arity constitution witness with every required input; not an acoustic realization.',
    'MEC-10': 'Evaluation of an actual supplied finite conditional kernel row; no training, sampling or invented winner.',
};
function validJson(value, depth = 0, seen = new Set()) {
    if (depth > 24)
        return false;
    if (value === null || typeof value === 'string' || typeof value === 'boolean')
        return true;
    if (typeof value === 'number')
        return Number.isFinite(value);
    if (typeof value !== 'object' || seen.has(value) || Object.getOwnPropertySymbols(value).length)
        return false;
    const proto = Object.getPrototypeOf(value);
    if (proto !== Object.prototype && proto !== null && proto !== Array.prototype)
        return false;
    const descriptors = Object.getOwnPropertyDescriptors(value);
    if (Object.values(descriptors).some(d => d.get || d.set))
        return false;
    seen.add(value);
    const good = Object.keys(value).every(key => validJson(descriptors[key].value, depth + 1, seen));
    seen.delete(value);
    return good;
}
function obj(value, name) {
    if (!value || typeof value !== 'object' || Array.isArray(value))
        throw new TypeError(`${name} must be an object`);
    return value;
}
function text(value, name) {
    if (typeof value !== 'string' || !value.trim() || value.length > 2048)
        throw new TypeError(`${name} must be nonempty text`);
    return value;
}
function list(value, name, max = 512) {
    if (!Array.isArray(value) || value.length > max)
        throw new TypeError(`${name} must be an array of at most ${max} items`);
    return value;
}
function int(value, name, limit = 1_000_000_000) {
    if (typeof value !== 'number' || !Number.isSafeInteger(value) || Math.abs(value) > limit)
        throw new TypeError(`${name} must be a bounded exact integer`);
    return value;
}
function refs(value) {
    const result = list(value, 'sourceRefs', 64).map(x => text(x, 'source reference'));
    if (!result.length)
        throw new TypeError('declared sourceRefs cannot be empty');
    return result;
}
function rat(value, name) {
    const v = obj(value, name);
    if (typeof v.numerator !== 'string' || typeof v.denominator !== 'string' ||
        v.numerator.length > 512 || v.denominator.length > 512)
        throw new TypeError(`${name} needs bounded exact integer strings`);
    return rational(v.numerator, v.denominator);
}
function add(a, b) { return rational(BigInt(a.numerator) * BigInt(b.denominator) + BigInt(b.numerator) * BigInt(a.denominator), BigInt(a.denominator) * BigInt(b.denominator)); }
function mul(a, b) { return rational(BigInt(a.numerator) * BigInt(b.numerator), BigInt(a.denominator) * BigInt(b.denominator)); }
function positive(a, name) { if (BigInt(a.numerator) <= 0n)
    throw new RangeError(`${name} must be positive`); return a; }
function stable(v) {
    if (!v || typeof v !== 'object')
        return JSON.stringify(v);
    if (Array.isArray(v))
        return `[${v.map(stable).join(',')}]`;
    return `{${Object.keys(v).sort().map(k => `${JSON.stringify(k)}:${stable(v[k])}`).join(',')}}`;
}
function copy(v) { return JSON.parse(JSON.stringify(v)); }
function equal(a, b) { return stable(a) === stable(b); }
function rjson(value) { return { numerator: value.numerator, denominator: value.denominator }; }
function mod(x, n) { return ((x % n) + n) % n; }
/** Loads the exact original GG bytes; a differently bound registry requires explicit review. */
export function createNativeExecutor(raw, sourceId) {
    if (!sourceId.trim())
        throw new TypeError('source occurrence ID is required');
    const bytes = typeof raw === 'string' ? Buffer.from(raw, 'utf8') : Buffer.from(raw);
    if (createHash('sha256').update(bytes).digest('hex') !== NATIVE_GG_SHA256)
        throw new TypeError('native GG bytes differ from the pinned source');
    const graph = JSON.parse(bytes.toString('utf8').replace(/^\uFEFF/, ''));
    const native = graph.generative_registry;
    if (!Array.isArray(native) || native.length !== 10 || new Set(native.map(x => x.id)).size !== 10 || native.some(x => !SCOPES[String(x.id)]))
        throw new TypeError('native mechanism registry mismatch');
    const entries = new Map(native.map((value, index) => [String(value.id), { value, index }]));
    const registry = () => native.map((value, index) => ({ id: String(value.id), name: String(value.name), canonical: value.canonical,
        sourceStatus: value.status, source: { sourceId, sha256: NATIVE_GG_SHA256, pointer: `/generative_registry/${index}` }, executionScope: SCOPES[String(value.id)],
        families: list(value.members, 'native members').map((member, i) => ({ id: `${String(value.id)}:member:${i}`, mechanismId: String(value.id), system: String(obj(member, 'member').system), sourcePointer: `/generative_registry/${index}/members/${i}`, sourceMember: copy(member), executionScope: SCOPES[String(value.id)] })) }));
    function execute(mechanismId, payload) {
        const entry = entries.get(mechanismId);
        const source = { sourceId, sha256: NATIVE_GG_SHA256, pointer: entry ? `/generative_registry/${entry.index}` : '/generative_registry' };
        const result = (status, output, reason) => ({ status, mechanismId, source, scope: SCOPES[mechanismId] ?? 'Unimplemented native mechanism', output, ...(reason ? { reason } : {}), canonicalPromotion: false });
        const unknown = (why) => result('unknown', null, why);
        if (!entry)
            return unknown('The source-defined mechanism is not implemented.');
        try {
            if (!validJson(payload) || Buffer.byteLength(JSON.stringify(payload), 'utf8') > 48000)
                throw new TypeError('input must be finite JSON within48000UTF8bytes');
            const input = obj(payload, 'input');
            switch (mechanismId) {
                case 'MEC-01': {
                    const value = positive(rat(input.value, 'value'), 'value'), factor = positive(rat(input.factor, 'factor'), 'factor');
                    const carrier = text(input.carrier, 'carrier');
                    return result('executed', { value: rjson(mul(value, factor)), factor: rjson(factor), carrier, unit: input.unit ?? null });
                }
                case 'MEC-02': {
                    if (input.realization !== undefined && input.realization !== 'Z12_affine')
                        return unknown('This source family needs its own declared native action; abstract D12 does not supply a triad map.');
                    const action = obj(input.action, 'action'), sign = int(action.sign, 'sign'), offset = mod(int(action.offset, 'offset'), 12);
                    if (sign !== 1 && sign !== -1)
                        throw new RangeError('D12 sign must be1or-1');
                    const values = list(input.values, 'values').map(v => mod(int(v, 'pitch class'), 12));
                    return result('executed', { values: values.map(v => mod(sign * v + offset, 12)), action: { sign, offset }, modulus: 12 });
                }
                case 'MEC-03': {
                    const values = list(input.values, 'values'), reversed = [...values].reverse();
                    return result('executed', { values: copy(reversed), isFixedPoint: equal(values, reversed) });
                }
                case 'MEC-04': {
                    if (input.mapping === undefined)
                        return unknown('An explicit source-qualified admissible shared-pitch mapping is required.');
                    const state = obj(input.state, 'state'), mapping = list(input.mapping, 'mapping', 256);
                    if (!Object.hasOwn(state, 'identity') || !Object.hasOwn(state, 'pitch') || !Object.hasOwn(state, 'address'))
                        throw new TypeError('state needs identity,pitch,address');
                    const targets = [];
                    for (const row of mapping) {
                        const m = obj(row, 'mapping row');
                        refs(m.sourceRefs);
                        const from = obj(m.from, 'from'), to = obj(m.to, 'to');
                        if (!Object.hasOwn(from, 'identity') || !Object.hasOwn(from, 'pitch') || !Object.hasOwn(from, 'address') || !Object.hasOwn(to, 'identity') || !Object.hasOwn(to, 'pitch') || !Object.hasOwn(to, 'address'))
                            throw new TypeError('map endpoints need identity,pitch,address');
                        if (equal(from, state)) {
                            if (m.admissible !== true)
                                return unknown('The matching partial-map entry is not declared admissible.');
                            if (!equal(from.identity, to.identity) || !equal(from.pitch, to.pitch))
                                return unknown('Native mutation must preserve object identity and shared pitch.');
                            targets.push(to);
                        }
                    }
                    if (!targets.length)
                        return unknown('The supplied state is outside the declared partial-map domain.');
                    if (new Set(targets.map(stable)).size !== 1)
                        return unknown('Conflicting declared partial-map targets remain unresolved.');
                    return result('executed', { state: copy(targets[0]), mapping: copy(mapping), admissibility: 'caller-declared; not an independent source proof' });
                }
                case 'MEC-05': {
                    const values = list(input.values, 'values');
                    if (!values.length)
                        return unknown('Cyclic index rotation needs a nonempty cyclic carrier.');
                    const k = mod(int(input.shift, 'shift'), values.length);
                    return result('executed', { values: copy([...values.slice(k), ...values.slice(0, k)]), shift: k, modulus: values.length });
                }
                case 'MEC-06': {
                    const n = int(input.slots, 'slots', 256), k = int(input.onsets, 'onsets', 256);
                    if (n < 1 || k < 0 || k > n)
                        throw new RangeError('Euclidean constructor requires1<=slots<=256 and0<=onsets<=slots');
                    const word = Array.from({ length: n }, (_, i) => Math.floor((i + 1) * k / n) - Math.floor(i * k / n));
                    const rotations = [];
                    const seen = new Set();
                    for (let i = 0; i < n; i++) {
                        const w = [...word.slice(i), ...word.slice(0, i)];
                        const key = w.join('');
                        if (!seen.has(key)) {
                            seen.add(key);
                            rotations.push(w);
                        }
                    }
                    return result('executed', { rotations, onsets: k, slots: n, phase: 'unspecified; complete cyclic orbit, no selected lawful origin' });
                }
                case 'MEC-07': {
                    if (input.universe === undefined)
                        return unknown('Complement and finite execution require an explicit integer universe.');
                    const universe = list(input.universe, 'universe', 2048).map(x => int(x, 'universe integer'));
                    if (new Set(universe).size !== universe.length)
                        throw new TypeError('universe entries must be distinct');
                    let nodes = 0;
                    // Compile every branch before evaluation, including short-circuited branches
                    // and expressions over an empty universe.
                    const compile = (expression, depth = 0) => {
                        if (++nodes > 4096 || depth > 16)
                            throw new RangeError('sieve expression exceeds bounded depth/work');
                        const e = obj(expression, 'sieve expression');
                        if (e.op === 'residue') {
                            const modulus = int(e.modulus, 'modulus'), residue = int(e.residue, 'residue');
                            if (modulus < 1)
                                throw new RangeError('modulus must be positive');
                            return x => ((BigInt(x) - BigInt(residue)) % BigInt(modulus)) === 0n;
                        }
                        if (e.op === 'complement') {
                            const child = compile(e.child, depth + 1);
                            return x => !child(x);
                        }
                        if (e.op !== 'union' && e.op !== 'intersection')
                            throw new TypeError('unsupported sieve operation');
                        const children = list(e.children, 'children', 128);
                        if (!children.length)
                            throw new TypeError('Boolean sieve operation needs children');
                        const predicates = children.map(child => compile(child, depth + 1));
                        return e.op === 'union' ? x => predicates.some(child => child(x)) : x => predicates.every(child => child(x));
                    };
                    const predicate = compile(input.expression);
                    if (nodes * Math.max(1, universe.length) > 1_000_000)
                        throw new RangeError('sieve expression exceeds bounded total work');
                    const values = universe.filter(predicate);
                    return result('executed', { values, universe, expression: copy(input.expression), complementScope: 'explicit finite universe only' });
                }
                case 'MEC-08': {
                    const unit = text(input.unit, 'duration unit'), events = list(input.events, 'events', 256).map(x => copy(obj(x, 'event')));
                    const ids = events.map(e => text(e.id, 'event id'));
                    if (new Set(ids).size !== ids.length)
                        throw new TypeError('event IDs must be distinct');
                    events.forEach(e => positive(rat(e.duration, 'duration'), 'duration'));
                    const index = int(input.index, 'index', 256), mode = text(input.mode, 'mode');
                    if (mode === 'insert') {
                        if (index < 0 || index > events.length)
                            throw new RangeError('insert index outside event sequence');
                        const event = copy(obj(input.event, 'inserted event'));
                        const eventId = text(event.id, 'inserted event id');
                        positive(rat(event.duration, 'inserted duration'), 'inserted duration');
                        if (ids.includes(eventId))
                            throw new TypeError('inserted event ID already exists');
                        events.splice(index, 0, event);
                    }
                    else {
                        if (index < 0 || index >= events.length)
                            throw new RangeError('index outside event sequence');
                        const duration = rat(events[index].duration, 'duration');
                        if (mode === 'dot')
                            events[index].duration = rjson(mul(duration, rational(3, 2)));
                        else if (mode === 'add') {
                            const delta = rat(input.delta, 'delta');
                            if (BigInt(delta.numerator) <= 0n)
                                return unknown('Source added-value subset requires a positive added duration.');
                            events[index].duration = rjson(add(duration, delta));
                        }
                        else
                            return unknown('This local-duration operation is not implemented by the source added-value subset.');
                    }
                    return result('executed', { events, unit, mode, index });
                }
                case 'MEC-09': {
                    if (input.rule === undefined)
                        return unknown('A declared source-qualified joint constitution rule is required.');
                    const rule = obj(input.rule, 'rule'), ruleId = text(rule.id, 'rule id');
                    refs(rule.sourceRefs);
                    if (rule.admissible !== true)
                        return unknown('Joint constitution admissibility is not declared.');
                    const required = list(rule.inputs, 'required inputs', 256).map(x => text(x, 'required input'));
                    if (required.length < 2 || new Set(required).size !== required.length)
                        throw new TypeError('joint inputs must be at least two distinct references');
                    const supplied = list(input.available, 'available inputs', 256).map(x => text(x, 'available input'));
                    if (new Set(supplied).size !== supplied.length)
                        throw new TypeError('available input references must be distinct');
                    const missing = required.filter(x => !supplied.includes(x));
                    if (missing.length)
                        return unknown('Missing joint antecedents: ' + missing.join(', '));
                    if (!Object.hasOwn(rule, 'output'))
                        return unknown('The declared composite output is absent; no realization is invented.');
                    return result('executed', { ruleId, inputs: required, arity: required.length, declaredComposite: copy(rule.output), sourceRefs: copy(rule.sourceRefs), semantics: 'all required inputs jointly witness the declared composite; no pairwise edges or acoustic waveform inferred' });
                }
                case 'MEC-10': {
                    if (input.kernel === undefined)
                        return unknown('An actual source-qualified conditional kernel is required.');
                    const kernel = obj(input.kernel, 'kernel');
                    const kernelId = text(kernel.id, 'kernel id'), revision = text(kernel.revision, 'kernel revision');
                    refs(kernel.sourceRefs);
                    if (!Object.hasOwn(input, 'context'))
                        throw new TypeError('context is required');
                    const matches = list(kernel.rows, 'kernel rows', 256).map(x => obj(x, 'kernel row')).filter(row => Object.hasOwn(row, 'context') && equal(row.context, input.context));
                    if (matches.length !== 1)
                        return unknown(matches.length ? 'Multiple matching kernel rows remain unresolved.' : 'The actual supplied kernel has no row for this context.');
                    const distribution = list(matches[0].distribution, 'distribution', 256);
                    if (!distribution.length)
                        throw new TypeError('kernel distribution cannot be empty');
                    let total = rational(0, 1);
                    const outcomes = new Set();
                    const exact = [];
                    for (const item of distribution) {
                        const p = obj(item, 'outcome');
                        if (!Object.hasOwn(p, 'event'))
                            throw new TypeError('kernel event is missing');
                        const key = stable(p.event);
                        if (outcomes.has(key))
                            throw new TypeError('duplicate kernel event');
                        outcomes.add(key);
                        const probability = rat(p.probability, 'probability');
                        const n = BigInt(probability.numerator), d = BigInt(probability.denominator);
                        if (n < 0n || n > d)
                            throw new RangeError('probability outside[0,1]');
                        total = add(total, probability);
                        exact.push({ event: copy(p.event), probability: rjson(probability) });
                    }
                    if (total.numerator !== '1' || total.denominator !== '1')
                        throw new RangeError('supplied probabilities must sum to exactly1; no renormalization');
                    return result('executed', { kernelId, revision, context: copy(input.context), distribution: exact, sourceRefs: copy(kernel.sourceRefs), semantics: 'actual supplied conditional distribution; no deterministic outcome selected' });
                }
                default: return unknown('Native mechanism implementation is absent.');
            }
        }
        catch (error) {
            return result('invalid', null, error instanceof Error ? error.message : 'Invalid native operator input.');
        }
    }
    return { registry, execute };
}
