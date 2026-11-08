const scope = 'Exact admitted finite relation only; no universal linguistic law inferred';
const value = (row, key) => Object.hasOwn(row.values, key) ? row.values[key] ?? null : null;
const key = (v) => JSON.stringify(v);
function names(fields) {
    if (!Array.isArray(fields) || fields.some(f => typeof f !== 'string' || !f.length) || new Set(fields).size !== fields.length)
        throw new TypeError('field names must be distinct nonempty strings');
}
function checked(rows) {
    if (!Array.isArray(rows) || rows.length > 10000)
        throw new RangeError('at most10000admitted rows supported');
    const ids = new Set();
    for (const row of rows) {
        if (!row || typeof row.id !== 'string' || !row.id || ids.has(row.id) || !row.values || typeof row.values !== 'object' || Array.isArray(row.values)
            || !Array.isArray(row.sourceRefs) || !row.sourceRefs.length || row.sourceRefs.some(r => typeof r !== 'string' || !r))
            throw new TypeError('unique source-bound row required');
        ids.add(row.id);
        for (const v of Object.values(row.values))
            if (v !== null && typeof v !== 'string')
                throw new TypeError('native values must be exact strings or explicit unknown null');
    }
}
export function readingDependency(rows, inputs, output) {
    checked(rows);
    names(inputs);
    names([output]);
    const cells = new Map();
    const unresolvedRows = [];
    for (const row of rows) {
        const tuple = inputs.map(f => value(row, f)), out = value(row, output);
        if (tuple.includes(null) || out === null) {
            unresolvedRows.push(row.id);
            continue;
        }
        const encoded = key(tuple);
        let cell = cells.get(encoded);
        if (!cell) {
            cell = { input: tuple, outputs: new Map(), rowIds: [] };
            cells.set(encoded, cell);
        }
        cell.rowIds.push(row.id);
        const witnesses = cell.outputs.get(out) ?? [];
        witnesses.push(row.id);
        cell.outputs.set(out, witnesses);
    }
    const counterexamples = [];
    for (const cell of cells.values())
        if (cell.outputs.size > 1) {
            const first = [...cell.outputs.entries()].slice(0, 2);
            counterexamples.push({ left: first[0][1][0], right: first[1][1][0], input: cell.input, outputs: first.map(x => x[0]) });
        }
    return { status: counterexamples.length ? 'contradicted' : cells.size ? 'no-counterexample-on-complete-rows' : 'no-complete-rows',
        inputs, output, cells: [...cells.values()].map(c => ({ input: c.input, outputs: [...c.outputs.keys()], rowIds: c.rowIds })),
        unresolvedRows, counterexamples, scope };
}
/** Enumerate all inclusion-minimal refinements in the explicitly admitted candidate vocabulary. */
export function minimalReadingRefinements(rows, base, candidates, output) {
    checked(rows);
    names(base);
    names(candidates);
    names([output]);
    if (candidates.length > 12 || candidates.some(c => base.includes(c) || c === output))
        throw new RangeError('at most12distinct additional input fields, excluding the target');
    const subsets = Array.from({ length: 2 ** candidates.length }, (_, mask) => candidates.filter((_, i) => Boolean(mask & (1 << i))))
        .sort((a, b) => a.length - b.length);
    const result = [];
    for (const extra of subsets) {
        if (result.some(prior => prior.every(f => extra.includes(f))))
            continue;
        const test = readingDependency(rows, [...base, ...extra], output);
        if (test.status === 'no-counterexample-on-complete-rows' && !test.unresolvedRows.length)
            result.push(extra);
    }
    return result;
}
/** Unknown source values retain candidates; they never act as evidence of absence. */
export function queryReadings(rows, conditions, output) {
    if (!conditions || typeof conditions !== 'object' || Array.isArray(conditions))
        throw new TypeError('query conditions must be an object map');
    checked(rows);
    names(Object.keys(conditions));
    names([output]);
    if (Object.values(conditions).some(v => typeof v !== 'string'))
        throw new TypeError('query values must be exact strings');
    const retained = rows.filter(row => Object.entries(conditions).every(([field, wanted]) => value(row, field) === null || value(row, field) === wanted));
    const unresolved = retained.filter(row => Object.keys(conditions).some(f => value(row, f) === null) || value(row, output) === null).map(r => r.id);
    const outputs = [...new Set(retained.map(r => value(r, output)).filter((v) => v !== null))];
    return { rowIds: retained.map(r => r.id), outputs, unresolvedRows: unresolved,
        status: !retained.length ? 'no-admitted-match' : unresolved.length ? 'unresolved-source-values' : outputs.length === 1 ? 'single-output-in-admitted-sample' : 'multiple-admitted-outputs', scope };
}
/** Compare a projection/rejoin against the complete known rows of this finite relation. */
export function readingJoinResidual(rows, left, right) {
    checked(rows);
    names(left);
    names(right);
    const fields = [...new Set([...left, ...right])], common = left.filter(f => right.includes(f));
    const known = rows.filter(r => fields.every(f => value(r, f) !== null));
    const unresolvedRows = rows.filter(r => !known.includes(r)).map(r => r.id);
    const project = (columns) => {
        const groups = new Map();
        for (const row of known) {
            const tuple = columns.map(f => value(row, f)), k = key(tuple);
            const group = groups.get(k) ?? { tuple, rowIds: [] };
            group.rowIds.push(row.id);
            groups.set(k, group);
        }
        return [...groups.values()];
    };
    const originals = new Set(known.map(r => key(fields.map(f => value(r, f)))));
    const leftProjection = project(left), rightProjection = project(right);
    if (leftProjection.length * rightProjection.length > 1000000)
        throw new RangeError('projection join exceeds one million tuple comparisons; partition the declared source scope explicitly');
    const joined = new Map();
    for (const a of leftProjection)
        for (const b of rightProjection) {
            if (!common.every(f => a.tuple[left.indexOf(f)] === b.tuple[right.indexOf(f)]))
                continue;
            const values = Object.fromEntries([...left.map((f, i) => [f, a.tuple[i]]), ...right.map((f, i) => [f, b.tuple[i]])]);
            joined.set(key(fields.map(f => values[f])), { values, leftRowIds: a.rowIds, rightRowIds: b.rowIds });
        }
    const excess = [...joined.entries()].filter(([k]) => !originals.has(k)).map(([, v]) => v);
    return { fields, common, knownOriginalDistinctTuples: originals.size, rejoinedDistinctTuples: joined.size,
        excessCombinations: excess, unresolvedRows, scope,
        boundary: 'Excess is relative to the admitted finite relation. Missing corpus cases remain unknown; a cross-pair is not a newly proved historical entity.' };
}
