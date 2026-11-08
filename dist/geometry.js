export const GEOMETRY_SCOPE = Object.freeze({
    mode: 'illustrative-projection',
    generationDegrees: 720,
    infiniteLimitRendered: false,
    soundWaveTopologyEstablished: false,
    radiusLaw: 'not-inferred',
});
function finite(value, name) {
    if (!Number.isFinite(value))
        throw new TypeError(`${name} must be finite`);
}
/** Half-open [0,720) generational phase; the second rotation remains distinguishable. */
export function wheelAddress(absolutePhaseDegrees) {
    finite(absolutePhaseDegrees, 'absolutePhaseDegrees');
    if (Math.abs(absolutePhaseDegrees) > Number.MAX_SAFE_INTEGER) {
        throw new RangeError('phase exceeds safe integer precision');
    }
    const generation = Math.floor(absolutePhaseDegrees / 720);
    const phaseDegrees = absolutePhaseDegrees - generation * 720;
    return {
        generation: Object.is(generation, -0) ? 0 : generation,
        phaseDegrees: Object.is(phaseDegrees, -0) ? 0 : phaseDegrees,
        rotation: phaseDegrees < 360 ? 0 : 1,
        dialDegrees: phaseDegrees % 360,
        // One turn represents twelve dial positions, without assuming clock time.
        dialPosition: (phaseDegrees % 360) / 30,
        semantics: 'configured-phase-coordinate',
    };
}
export function torusPoint(u, v, majorRadius, tubeRadius) {
    for (const [name, value] of Object.entries({ u, v, majorRadius, tubeRadius }))
        finite(value, name);
    if (!(majorRadius > tubeRadius && tubeRadius > 0)) {
        throw new RangeError('ring torus requires majorRadius > tubeRadius > 0');
    }
    const radial = majorRadius + tubeRadius * Math.cos(v);
    return [radial * Math.cos(u), radial * Math.sin(u), tubeRadius * Math.sin(v)];
}
/** A radius remains unresolved until supplied; no growth or rebound law is invented. */
export function wheelPoint(phaseDegrees, radius, height) {
    finite(phaseDegrees, 'phaseDegrees');
    if (radius === null || height === null)
        return null;
    finite(radius, 'radius');
    finite(height, 'height');
    if (radius < 0)
        throw new RangeError('radius must be nonnegative');
    const angle = phaseDegrees * Math.PI / 180;
    return [radius * Math.cos(angle), radius * Math.sin(angle), height];
}
const ROOT_TETRAHEDRON = [
    [1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1],
];
/** Four half-scale homotheties per stage. Depth is finite and bounded for memory. */
export function sierpinskiTetrahedron(depth) {
    if (!Number.isInteger(depth) || depth < 0 || depth > 7) {
        throw new RangeError('depth must be an integer from 0 to 7 (finite approximation)');
    }
    let cells = [ROOT_TETRAHEDRON];
    for (let level = 0; level < depth; level++) {
        const next = [];
        for (const cell of cells) {
            for (const anchor of cell) {
                const points = cell.map(p => [
                    (p[0] + anchor[0]) / 2,
                    (p[1] + anchor[1]) / 2,
                    (p[2] + anchor[2]) / 2,
                ]);
                next.push(points);
            }
        }
        cells = next;
    }
    // Return fresh arrays so a consumer cannot corrupt the next construction.
    return cells.map(cell => cell.map(p => [...p]));
}
