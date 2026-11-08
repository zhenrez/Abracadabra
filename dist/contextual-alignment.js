/** Exact cyclic-difference constraints on a declared adapter, not a native ontology. */
import { createHash } from 'node:crypto';
import { predictOverCandidates } from './prediction.js';
const mod = (x, m) => ((x % m) + m) % m;
function nonempty(s, label) {
    if (typeof s !== 'string' || !s.trim() || s.length > 2048)
        throw new TypeError(`${label} needs nonempty bounded text`);
}
function references(refs) {
    if (!Array.isArray(refs) || !refs.length || refs.length > 256)
        throw new TypeError('source references are required');
    for (const ref of refs)
        nonempty(ref, 'source reference');
}
function validate(spec) {
    nonempty(spec.id, 'case id');
    references(spec.sourceRefs);
    if (!Number.isSafeInteger(spec.modulus) || spec.modulus < 2 || spec.modulus > 1_000_000)
        throw new RangeError('modulus must be an integer in[2,1000000]');
    if (!Array.isArray(spec.variables) || !spec.variables.length || spec.variables.length > 256)
        throw new TypeError('variables must be a bounded nonempty list');
    spec.variables.forEach(v => nonempty(v, 'variable'));
    if (new Set(spec.variables).size !== spec.variables.length)
        throw new TypeError('variables must be unique');
    if (!Array.isArray(spec.links) || spec.links.length > 4096)
        throw new TypeError('links must be a bounded list');
    const variables = new Set(spec.variables), ids = new Set();
    for (const e of spec.links) {
        nonempty(e.id, 'link id');
        if (ids.has(e.id))
            throw new TypeError('link ids must be unique');
        ids.add(e.id);
        if (!variables.has(e.from) || !variables.has(e.to))
            throw new TypeError('link refers to an undeclared variable');
        if (!Number.isSafeInteger(e.offset))
            throw new TypeError('offset must be an exact safe integer');
        references(e.sourceRefs);
    }
    if (!Array.isArray(spec.assumptions) || spec.assumptions.some(a => typeof a !== 'string'))
        throw new TypeError('assumptions must be declared as text');
    const targets = spec.targets ?? [];
    if (new Set(targets.map(t => t.id)).size !== targets.length)
        throw new TypeError('target ids must be unique');
    for (const t of targets) {
        nonempty(t.id, 'target id');
        if (t.kind === 'value') {
            if (!variables.has(t.variable))
                throw new TypeError('target variable is undeclared');
        }
        else if (t.kind === 'difference') {
            if (!variables.has(t.from) || !variables.has(t.to))
                throw new TypeError('target variable is undeclared');
        }
        else
            throw new TypeError('unsupported target kind');
    }
}
/** Potentials give a complete solution family for these equality constraints. */
function analyze(variables, links, m) {
    const adjacency = new Map(variables.map(v => [v, []]));
    for (const e of links) {
        const offset = mod(e.offset, m);
        adjacency.get(e.from).push({ edgeId: e.id, from: e.from, to: e.to, offset, sign: 1, sourceRefs: [...e.sourceRefs] });
        adjacency.get(e.to).push({ edgeId: e.id, from: e.to, to: e.from, offset: mod(-offset, m), sign: -1, sourceRefs: [...e.sourceRefs] });
    }
    const values = new Map(), component = new Map(), parents = new Map(), roots = [];
    const path = (v) => { const steps = []; while (parents.has(v)) {
        const e = parents.get(v);
        steps.push(e);
        v = e.from;
    } return steps.reverse(); };
    for (const root of variables) {
        if (values.has(root))
            continue;
        const componentId = roots.length;
        roots.push(root);
        values.set(root, 0);
        component.set(root, componentId);
        const queue = [root];
        for (let i = 0; i < queue.length; i++) {
            const from = queue[i];
            for (const step of adjacency.get(from)) {
                const expected = mod(values.get(from) + step.offset, m);
                if (!values.has(step.to)) {
                    values.set(step.to, expected);
                    component.set(step.to, componentId);
                    parents.set(step.to, step);
                    queue.push(step.to);
                }
                else if (values.get(step.to) !== expected) {
                    const reverse = path(step.to).reverse().map(e => ({ ...e, from: e.to, to: e.from, offset: mod(-e.offset, m), sign: (-e.sign) }));
                    const steps = [...path(from), step, ...reverse];
                    const residue = steps.reduce((sum, e) => mod(sum + e.offset, m), 0);
                    return { consistent: false, values, component, roots, cycle: { steps, residue, modulus: m } };
                }
            }
        }
    }
    return { consistent: true, values, component, roots, cycle: null };
}
/**
 * Reuses SUNNY's candidate/prediction engine after quotienting the equality
 * graph by its freely translated connected components. Each origin survives;
 * root=0 is a coordinate section, never an elected historical orientation.
 */
export function solveContextualAlignment(spec, options = {}) {
    validate(spec);
    const limit = options.maxAssignments ?? 10000;
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 1_000_000)
        throw new RangeError('maxAssignments must be in[1,1000000]');
    const m = spec.modulus, graph = analyze(spec.variables, spec.links, m);
    const boundary = { scope: 'declared-finite-cyclic-adapter-only', assumptions: [...spec.assumptions],
        sourceRefs: [...spec.sourceRefs], sourceAuthenticity: 'requires-source-binding-audit',
        canonicalPromotion: false, globalOrientationSelected: false, blindPrediction: false };
    if (!graph.consistent) {
        let core = [...spec.links];
        for (let i = 0; i < core.length;) {
            const trial = core.filter((_, j) => j !== i);
            if (!analyze(spec.variables, trial, m).consistent)
                core = trial;
            else
                i++;
        }
        return { ...boundary, status: 'inconsistent', assignmentCount: '0', cycle: graph.cycle,
            inclusionMinimalCore: core.map(e => e.id), minimality: 'inclusion-minimal; minimum cardinality not claimed',
            assignments: null, prediction: null, freeOrigins: [] };
    }
    const count = BigInt(m) ** BigInt(graph.roots.length);
    const freeOrigins = graph.roots.map((root, i) => ({ component: i, referenceVariable: root, domain: { kind: 'cyclic-residues', modulus: m },
        members: spec.variables.filter(v => graph.component.get(v) === i).map(variable => ({ variable, relativeValue: graph.values.get(variable) })) }));
    if (count > BigInt(limit))
        return { ...boundary, status: 'symbolic-family', assignmentCount: String(count), cycle: null,
            inclusionMinimalCore: [], assignments: null, prediction: null, freeOrigins, materializationLimit: limit };
    const assignments = [], candidates = [];
    const targets = spec.targets ?? spec.variables.map(variable => ({ id: variable, kind: 'value', variable }));
    const kernel = { id: spec.id, version: 'cyclic-difference-v1', sourceRefs: [...spec.sourceRefs],
        sha256: createHash('sha256').update(JSON.stringify(spec)).digest('hex') };
    const constraints = spec.links.map(e => ({ id: e.id, kernelSha256: kernel.sha256, sourceRefs: [...e.sourceRefs],
        authority: 'assumption', predicate: { op: 'eq', key: 'link:' + e.id, value: true } }));
    for (let index = 0; index < Number(count); index++) {
        let digits = index;
        const origins = graph.roots.map(() => { const n = digits % m; digits = Math.floor(digits / m); return n; });
        const values = Object.create(null);
        for (const v of spec.variables)
            values[v] = mod(graph.values.get(v) + origins[graph.component.get(v)], m);
        assignments.push(values);
        const assignment = {};
        for (const e of spec.links)
            assignment['link:' + e.id] = mod(values[e.to] - values[e.from], m) === mod(e.offset, m);
        for (const t of targets)
            assignment['target:' + t.id] = t.kind === 'value' ? values[t.variable] : mod(values[t.to] - values[t.from], m);
        candidates.push({ id: spec.id + ':origin:' + origins.join('.'), assignment, sourceRefs: [...spec.sourceRefs] });
    }
    const prediction = predictOverCandidates(candidates, constraints, kernel, targets.map(t => ({ id: t.id, keys: ['target:' + t.id], sourceRefs: [...spec.sourceRefs] })));
    return { ...boundary, status: 'admissible-family', assignmentCount: String(count), cycle: null, inclusionMinimalCore: [],
        assignments, prediction, freeOrigins, materializationLimit: limit };
}
