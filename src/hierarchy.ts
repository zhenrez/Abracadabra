/** Source-scoped hierarchy records. Units and native relations remain data, not a universal ontology. */
export const LEGION_SLOT_UNIT = 'catalogue-attributed-legion-membership-slot';
export const LEGION_COMMAND_RELATION = 'commands-catalogue-slot';
export interface HierarchySource {
  id: string; title?: string; path?: string; sha256?: string; kind?: string;
  locator?: unknown; sourceRole?: string; [key: string]: unknown;
}
export interface HierarchyPosition {
  generation: number | string | null; sequence: number | null;
  cyclicCoordinate: number | string | null; orientation: string | null;
}
export interface HierarchyEntity {
  id: string; nativeName: string; aliases: string[]; unit: string;
  tradition: string; witnessId: string; position: HierarchyPosition;
  sourceRefs: string[]; exceptions: string[]; assertionLayer?: string;
  statedExtent?: {value: number; unit: string; [key: string]: unknown};
  [key: string]: unknown;
}
export interface HierarchyRelationship {
  id: string; source: string; target: string; type: string; viewIds: string[];
  sourceRefs: string[]; assertionLayer: string; [key: string]: unknown;
}
export interface HierarchyView {
  id: string; label: string; roots: string[]; relationTypes?: string[];
  orientation?: string | null; witnessIds: string[]; coverage: unknown;
  [key: string]: unknown;
}
export interface HierarchyAtlas {
  sources: HierarchySource[]; entities: HierarchyEntity[];
  relationships: HierarchyRelationship[]; views: HierarchyView[];
  [key: string]: unknown;
}
export interface HierarchyScope {
  viewIds?: string[]; witnessIds?: string[]; traditions?: string[]; units?: string[];
  orientation?: string; relationTypes?: string[];
}
const nonempty = (x: unknown): x is string => typeof x === 'string' && x.trim().length > 0;
const strings = (x: unknown): x is string[] => Array.isArray(x) && x.every(nonempty);
const slot = (x: HierarchyEntity) => x.unit === LEGION_SLOT_UNIT;

/** Checks declared references and record shape. Validity does not certify historical truth. */
export function validateHierarchyAtlas(atlas: HierarchyAtlas) {
  const errors: string[] = [];
  if (!atlas || !['sources', 'entities', 'relationships', 'views'].every(k => Array.isArray(atlas[k]))) {
    return {valid: false, errors: ['atlas requires sources/entities/relationships/views arrays'], scope: 'declared-records-and-references-only'};
  }
  const ids = (rows: {id: string}[], kind: string) => {
    const found = new Set<string>();
    for (const row of rows) {
      if (!row || !nonempty(row.id)) { errors.push(`${kind} has missing id`); continue; }
      if (found.has(row.id)) errors.push(`duplicate ${kind} id: ${row.id}`);
      found.add(row.id);
    }
    return found;
  };
  const sources = ids(atlas.sources, 'source'), entities = ids(atlas.entities, 'entity');
  ids(atlas.relationships, 'relationship'); const views = ids(atlas.views, 'view');
  const checkRefs = (row: {id: string; sourceRefs: string[]}) => {
    if (!strings(row.sourceRefs) || row.sourceRefs.length === 0) {errors.push(`missing source references: ${row.id}`); return;}
    for (const ref of row.sourceRefs) if (!sources.has(ref)) errors.push(`unknown source ${ref}: ${row.id}`);
  };
  for (const source of atlas.sources) {
    if (!source || typeof source !== 'object') continue;
    if (source.sha256 !== undefined && !/^[a-f0-9]{64}$/.test(source.sha256)) errors.push(`invalid source digest: ${source.id}`);
  }
  for (const entity of atlas.entities) {
    if (!entity || typeof entity !== 'object') continue;
    checkRefs(entity);
    for (const key of ['nativeName', 'unit', 'tradition', 'witnessId'] as const) if (!nonempty(entity[key])) errors.push(`missing ${key}: ${entity.id}`);
    if (!strings(entity.aliases) || !Array.isArray(entity.exceptions) || !entity.exceptions.every(x => typeof x === 'string')) errors.push(`invalid aliases/exceptions: ${entity.id}`);
    const p = entity.position;
    if (!p || !['generation', 'sequence', 'cyclicCoordinate', 'orientation'].every(k => Object.hasOwn(p, k))) errors.push(`incomplete position: ${entity.id}`);
    else {
      if (p.sequence !== null && (!Number.isSafeInteger(p.sequence) || p.sequence < 0)) errors.push(`invalid sequence: ${entity.id}`);
      for (const coordinate of [p.generation, p.cyclicCoordinate]) if (coordinate !== null && typeof coordinate !== 'string' && !(typeof coordinate === 'number' && Number.isFinite(coordinate))) errors.push(`invalid coordinate: ${entity.id}`);
      if (p.orientation !== null && !nonempty(p.orientation)) errors.push(`invalid orientation: ${entity.id}`);
    }
    if (entity.statedExtent && (!Number.isSafeInteger(entity.statedExtent.value) || entity.statedExtent.value < 0 || !nonempty(entity.statedExtent.unit))) errors.push(`invalid stated extent: ${entity.id}`);
    if (slot(entity) && entity.assertionLayer !== 'generated') errors.push(`membership slot must be explicitly generated: ${entity.id}`);
  }
  for (const edge of atlas.relationships) {
    if (!edge || typeof edge !== 'object') continue;
    checkRefs(edge);
    if (!entities.has(edge.source) || !entities.has(edge.target)) errors.push(`unresolved edge endpoint: ${edge.id}`);
    if (!nonempty(edge.type) || !nonempty(edge.assertionLayer)) errors.push(`untyped relationship: ${edge.id}`);
    if (!strings(edge.viewIds) || edge.viewIds.length === 0) errors.push(`missing edge views: ${edge.id}`);
    else for (const view of edge.viewIds) if (!views.has(view)) errors.push(`unknown view ${view}: ${edge.id}`);
  }
  for (const view of atlas.views) {
    if (!view || typeof view !== 'object') continue;
    if (!nonempty(view.label) || !strings(view.roots) || !strings(view.witnessIds)) errors.push(`invalid view: ${view.id}`);
    else for (const root of view.roots) if (!entities.has(root)) errors.push(`unresolved view root ${root}: ${view.id}`);
  }
  return {valid: errors.length === 0, errors, scope: 'declared-records-and-references-only'};
}

/** View selections form a union; other explicit scope filters intersect it. No ABC/witness pairing exists. */
export function filterHierarchy(atlas: HierarchyAtlas, scope: HierarchyScope = {}) {
  const viewIds = scope.viewIds ? new Set(scope.viewIds) : undefined;
  const selectedViews = atlas.views.filter(v => !viewIds || viewIds.has(v.id));
  const active = new Set(selectedViews.map(v => v.id));
  const permittedByView = new Set(selectedViews.flatMap(v => v.roots));
  for (const edge of atlas.relationships) if (edge.viewIds.some(v => active.has(v))) {
    permittedByView.add(edge.source); permittedByView.add(edge.target);
  }
  const selectedEntities = atlas.entities.filter(e => (!viewIds || permittedByView.has(e.id)) &&
    (!scope.witnessIds || scope.witnessIds.includes(e.witnessId)) &&
    (!scope.traditions || scope.traditions.includes(e.tradition)) &&
    (!scope.units || scope.units.includes(e.unit)) &&
    (!scope.orientation || e.position.orientation === null || e.position.orientation === scope.orientation));
  const ids = new Set(selectedEntities.map(e => e.id));
  const selectedRelationships = atlas.relationships.filter(e => ids.has(e.source) && ids.has(e.target) &&
    (!viewIds || e.viewIds.some(v => active.has(v))) &&
    (!scope.relationTypes || scope.relationTypes.includes(e.type)));
  return {entities: selectedEntities, relationships: selectedRelationships, views: selectedViews};
}

/** Counts records and typed occurrences. Cross-witness or cross-command identity is never inferred. */
export function hierarchyCensus(atlas: HierarchyAtlas, scope: HierarchyScope = {}) {
  const selected = filterHierarchy(atlas, scope), byUnit: Record<string, number> = {}, byWitness: Record<string, {entityRecords: number; chiefRecords: number; generatedSlots: number}> = {};
  for (const e of selected.entities) {
    byUnit[e.unit] = (byUnit[e.unit] ?? 0) + 1;
    const witness = byWitness[e.witnessId] ??= {entityRecords: 0, chiefRecords: 0, generatedSlots: 0};
    if (slot(e)) witness.generatedSlots++; else witness.entityRecords++;
    if (e.unit === 'catalogue-chief') witness.chiefRecords++;
  }
  const generatedSlots = selected.entities.filter(slot).length;
  return {entityRecords: selected.entities.length - generatedSlots, generatedMembershipSlots: generatedSlots,
    chiefRecords: selected.entities.filter(e => e.unit === 'catalogue-chief').length,
    nativeSourceEntityRecords: selected.entities.filter(e => !slot(e) && e.assertionLayer === 'source-assertion').length,
    proposedEntityRecords: selected.entities.filter(e => !slot(e) && e.assertionLayer === 'research-hypothesis').length,
    rankMembershipOccurrences: selected.relationships.filter(e => e.type === 'has-rank-member').length,
    byUnit, byWitness, uniqueLegions: null, uniquePersonnel: null, uniqueEntitiesAcrossWitnesses: null,
    boundary: 'Entity records are witness/context scoped. Generated slots are membership occurrences, not named individuals or established distinct legions. Shared names and sums do not identify records across witnesses.'};
}

/** Iterative typed-edge ancestry terminates on cycles; it never equates different relation meanings. */
export function ancestorsOf(atlas: HierarchyAtlas, entityId: string, scope: HierarchyScope = {}) {
  const selected = filterHierarchy(atlas, scope), ids = new Set(selected.entities.map(e => e.id));
  if (!ids.has(entityId)) return {status: 'unavailable', ancestorIds: [], cycles: [], reason: 'entity is missing or outside the selected scope'};
  const parents = new Map<string, string[]>();
  for (const edge of selected.relationships) {
    const ps = parents.get(edge.target) ?? []; ps.push(edge.source); parents.set(edge.target, ps);
  }
  const found = new Set<string>(), done = new Set<string>(), active = new Map<string, number>();
  const path: string[] = [], cycles: string[][] = [], stack = [{id: entityId, next: 0}];
  while (stack.length) {
    const frame = stack[stack.length - 1]!;
    if (!active.has(frame.id)) {active.set(frame.id, path.length); path.push(frame.id);}
    const ps = parents.get(frame.id) ?? [];
    if (frame.next >= ps.length) {done.add(frame.id); active.delete(frame.id); path.pop(); stack.pop(); continue;}
    const parent = ps[frame.next++]!;
    if (parent !== entityId) found.add(parent);
    if (active.has(parent)) {cycles.push([...path.slice(active.get(parent)!), parent]); continue;}
    if (!done.has(parent)) stack.push({id: parent, next: 0});
  }
  return {status: cycles.length ? 'cycle-detected' : 'traced', ancestorIds: [...found].sort(), cycles,
    relationTypes: [...new Set(selected.relationships.map(e => e.type))],
    boundary: 'Traversal follows selected directed relation types. Production, appointment, membership and command remain distinguishable edge labels.'};
}

/** Reconciles addressable occurrence slots to each exact catalogue count without assuming disjointness. */
export function reconcileLegionCatalogue(atlas: HierarchyAtlas, witnessId: string) {
  const selected = filterHierarchy(atlas, {witnessIds: [witnessId]});
  const chiefs = selected.entities.filter(e => e.unit === 'catalogue-chief');
  const slots = selected.entities.filter(slot), byId = new Map(atlas.entities.map(e => [e.id, e]));
  const chiefIds = new Set(chiefs.map(e => e.id)), slotIds = new Set(slots.map(e => e.id)), errors: string[] = [];
  const commandEdges = atlas.relationships.filter(e => e.type === LEGION_COMMAND_RELATION &&
    (chiefIds.has(e.source) || slotIds.has(e.target)));
  const incoming = new Map<string, HierarchyRelationship[]>(), outgoing = new Map<string, HierarchyEntity[]>();
  for (const edge of commandEdges) {
    const child = byId.get(edge.target), parent = byId.get(edge.source);
    if (!child || !parent || !chiefIds.has(parent.id) || !slot(child) || child.witnessId !== witnessId) {errors.push(`invalid command-slot link: ${edge.id}`); continue;}
    if (!parent.sourceRefs.some(ref => child.sourceRefs.includes(ref) && edge.sourceRefs.includes(ref))) errors.push(`slot source differs from commander: ${child.id}`);
    const inc = incoming.get(child.id) ?? []; inc.push(edge); incoming.set(child.id, inc);
    const out = outgoing.get(parent.id) ?? []; out.push(child); outgoing.set(parent.id, out);
  }
  for (const s of slots) if ((incoming.get(s.id)?.length ?? 0) !== 1) errors.push(`slot must have exactly one catalogue commander: ${s.id}`);
  const chiefChecks = chiefs.map(chief => {
    const expected = chief.statedExtent?.unit === 'primary-legion-command-count' ? chief.statedExtent.value : null;
    const children = outgoing.get(chief.id) ?? [], sequences = new Set(children.map(x => x.position.sequence));
    const valid = expected !== null && Number.isSafeInteger(expected) && expected >= 0 && children.length === expected && sequences.size === expected &&
      children.every(x => Number.isSafeInteger(x.position.sequence) && x.position.sequence! >= 1 && x.position.sequence! <= expected);
    if (!valid) errors.push(`stated count and occurrence slots disagree: ${chief.id}`);
    return {chiefId: chief.id, statedCount: expected, generatedSlotCount: children.length, valid};
  });
  if (chiefs.length === 0) errors.push('no catalogue chiefs in selected witness');
  return {witnessId, valid: errors.length === 0, errors, chiefCount: chiefs.length,
    primaryCommandCountSum: chiefChecks.reduce((sum, x) => sum + (x.statedCount ?? 0), 0),
    generatedMembershipSlotCount: slots.length, chiefChecks,
    uniqueLegions: null, uniquePersonnel: null, membershipDisjointness: 'unknown',
    boundary: 'Slots enumerate each catalogue command extent separately; they do not assert named members, individual identity, disjoint commands, cross-witness identity or a universal legion size.'};
}
