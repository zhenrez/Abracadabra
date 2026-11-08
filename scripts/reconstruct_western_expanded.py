"""Execute witness-scoped Western register, range-profile and GM1 expansions."""
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'state/research/western-expanded'
OUT = ROOT / 'state/reconstruction/western-expanded.json'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def build():
    original_path = 'state/reconstruction/musical-hierarchies.json'
    original = read(original_path)
    reading = read('state/research/western-expanded/source-readings.json')
    gm = read('state/research/western-expanded/gm-acquisition/gm-tables.json')
    receipt_path = 'state/jev-receipts/000064-fc22fe7cfcff.json'
    jev = read(receipt_path)
    assert jev['response']['results'][0]['answers'][0]['value'] == 'source_defined_class_expansion_first'
    for image in reading['images'].values():
        assert sha(image['path']) == image['sha256']
    assert sha(gm['sourcePdf']) == gm['pdfSha256']
    preserved = [copy.deepcopy(e) for e in original['entities'] if e.get('tradition') == 'Western']
    preserved_ids = {e['id'] for e in preserved}
    preserved_relations = [copy.deepcopy(r) for r in original['relationships']
                           if r['source'] in preserved_ids and r['target'] in preserved_ids]
    entities = preserved[:]
    relations = preserved_relations[:]
    ids = {e['id']: e for e in entities}
    sources = copy.deepcopy(original['sources'])
    sources.extend([
        {'id': 'western:source:four-rows', 'title': 'Supplied music_chart3 (1).jpg', **reading['images']['scale']},
        {'id': 'western:source:key-range', 'title': 'Supplied Analysis output 7.png', **reading['images']['range']},
        {'id': 'western:source:gm1', 'title': 'MMA0007 / RP003 General MIDI System Level 1',
         'path': gm['sourcePdf'], 'sha256': gm['pdfSha256'],
         'officialPage': 'https://midi.org/general-midi-level-1',
         'downloadUrl': 'https://drive.google.com/uc?export=download&id=1TTM2HI2JAp_XiTJYEJ8gPNvuJpIjJiTP',
         'printedPageOffset': 2, 'role': 'Original official public specification PDF; sound-address standard, not physical instrument census'}])
    new_view = 'music:western:registered-expansion'
    range_view = 'music:western:range-profiles'
    gm_view = 'music:western:gm1'

    def edge(source, target, kind, view, refs, **extra):
        relations.append({'id': 'western-expanded:edge:' + str(len(relations) - len(preserved_relations)),
                          'source': source, 'target': target, 'type': kind, 'viewIds': [view],
                          'sourceRefs': refs, 'assertionLayer': 'source-rule-expansion', **extra})

    def add(eid, name, unit, parent, view, refs, **extra):
        assert eid not in ids
        row = {'id': eid, 'nativeName': name, 'aliases': [], 'unit': unit, 'tradition': 'Western',
               'witnessId': '+'.join(refs), 'sourceRefs': refs, 'parent': parent,
               'position': {'generation': None, 'sequence': None, 'cyclicCoordinate': None, 'orientation': None},
               'globalAddress': {'status': 'unresolved', 'generationClass': None, 'placement': None},
               'assertionLayer': 'source-rule-expansion', 'exceptions': [], **extra}
        entities.append(row)
        ids[eid] = row
        if parent:
            edge(parent, eid, 'has-source-defined-member', view, refs)
        return row

    prefix = 'music:western-expanded'
    refs = ['western:source:four-rows', 'western:source:key-range']
    top = prefix + ':registered'
    add(top, 'Registered scale-degree addresses within the supplied 88-key range',
        'witness-scoped-registered-note-system', 'music:western:root', new_view, refs)
    natural = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    letters = 'CDEFGAB'
    # Representatives are explicit implementation choices within source pitch classes.
    roots = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    physical_names = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
    for pc, root in enumerate(roots):
        add(prefix + ':root:' + str(pc), physical_names[pc], 'native-transposition-pitch-class', top,
            new_view, refs, nativeCoordinates={'pitchClass': pc},
            spellingRepresentative=root, representativeStatus='Computational representative; enharmonic class is not a unique notation role')
    key_parent = prefix + ':keyboard'
    add(key_parent, '88-key keyboard address range A0–C8', 'source-keyboard-range', top, new_view,
        ['western:source:key-range'], firstMidiKey=21, lastMidiKey=108, physicalInstrumentInstance=None)
    for midi in range(21, 109):
        octave, pc = midi // 12 - 1, midi % 12
        add(prefix + ':key:' + str(midi), physical_names[pc] + str(octave), 'keyboard-key-position',
            key_parent, new_view, ['western:source:key-range'],
            nativeCoordinates={'midiKey': midi, 'keyOrdinalOneBased': midi - 20, 'pitchClass': pc, 'octave': octave},
            etReference={'a4Hz': 440, 'derivedHz': 440 * 2 ** ((midi - 69) / 12),
                         'status': 'Equal-temperament reference calculation, not a measured or performed sound'},
            physicalInstrumentInstance=None)

    registered = []
    for form in reading['forms']:
        fid = prefix + ':form:' + form['key']
        add(fid, form['name'], 'source-heptatonic-form', top, new_view, ['western:source:four-rows'],
            sourceReading=form, cardinality=7)
        for pc, root in enumerate(roots):
            cid = fid + ':root:' + str(pc)
            add(cid, root + ' · ' + form['name'], 'root-qualified-scale-form-context', fid, new_view, refs,
                nativeCoordinates={'rootPitchClass': pc, 'form': form['key']},
                spellingRepresentative=root, direction=form['direction'])
            edge(prefix + ':root:' + str(pc), cid, 'selects-transposition-root', new_view, refs)
            for degree, offset in enumerate(form['offsets'], 1):
                target = (pc + offset) % 12
                letter = letters[(letters.index(root[0]) + degree - 1) % 7]
                accidental = (target - natural[letter] + 6) % 12 - 6
                assert -2 <= accidental <= 2
                spelling = letter + ('#' * accidental if accidental > 0 else 'b' * -accidental)
                did = cid + ':degree:' + str(degree)
                add(did, spelling + ' · degree ' + str(degree), 'transposition-qualified-scale-degree', cid,
                    new_view, refs, nativeCoordinates={'rootPitchClass': pc, 'form': form['key'], 'degree': degree,
                                                       'pitchClass': target, 'relativeSemitones': offset},
                    notationRole={'letter': letter, 'accidental': accidental, 'spelling': spelling},
                    spellingStatus='Diatonic degree spelling derived under the explicit root representative')
                for midi in range(21, 109):
                    if midi % 12 != target:
                        continue
                    notation_octave = (midi - natural[letter] - accidental) // 12 - 1
                    nid = did + ':key:' + str(midi)
                    row = add(nid, root + ' ' + form['name'] + ' · degree ' + str(degree) + ' · ' + spelling + str(notation_octave),
                              'registered-scale-degree-occurrence', did, new_view, refs,
                              nativeCoordinates={'form': form['key'], 'rootPitchClass': pc, 'degree': degree,
                                                 'midiKey': midi, 'keyOrdinalOneBased': midi - 20},
                              registeredNote={'writtenPitch': spelling + str(notation_octave), 'letter': letter,
                                              'accidental': accidental, 'notationOctave': notation_octave,
                                              'physicalKeyAddress': midi, 'physicalKeyPitchClass': target},
                              direction=form['direction'], physicalOccurrence=False,
                              etReference={'a4Hz': 440, 'referenceKeyId': prefix + ':key:' + str(midi),
                                           'notMeasuredSound': True})
                    registered.append(row)
                    edge(nid, prefix + ':key:' + str(midi), 'realizes-on-equal-tempered-key-position', new_view, refs)

    range_root = prefix + ':ranges'
    add(range_root, '31 supplied voice and instrument range profiles', 'source-range-profile-system',
        'music:western:root', range_view, ['western:source:key-range'])
    for family, names in reading['rangeProfiles'].items():
        family_id = range_root + ':' + family.lower()
        add(family_id, family, 'source-range-profile-family', range_root, range_view, ['western:source:key-range'])
        for index, name in enumerate(names):
            add(family_id + ':' + str(index), name, 'source-visible-range-profile', family_id, range_view,
                ['western:source:key-range'], sourceLabel=name, rangeLow=None, rangeHigh=None,
                endpointsStatus='Unknown: blurred graphical endpoints are not assigned absolute pitches',
                profileKind='voice register' if family == 'Voices' else 'timpani size profile' if family == 'Timpani' else 'instrument range profile',
                physicalInstrumentInstance=None)

    gm_root = prefix + ':gm1'
    gm_ref = ['western:source:gm1']
    add(gm_root, 'General MIDI System Level 1 sound-address hierarchy', 'modern-sound-realization-system',
        'music:western:root', gm_view, gm_ref, exactAcousticTimbresDefined=False,
        exceptions=['Program addresses and percussion mappings are not physical instrument types or all Western instruments.'])
    for family in gm['families']:
        gid = gm_root + ':group:' + str(family['familyOrdinalOneBased'])
        add(gid, family['name'], 'gm1-program-family', gm_root, gm_view, gm_ref,
            nativeCoordinates={'familyOrdinalOneBased': family['familyOrdinalOneBased'],
                               'programRangeOneBased': family['programRangeOneBased']},
            sourceLocator={'printedPage': 5, 'pdfPageOneBased': 7, 'table': 1})
    for program in gm['programs']:
        n = program['programNumberOneBased']
        add(gm_root + ':program:' + str(n), program['observedName'], 'gm1-sound-program',
            gm_root + ':group:' + str((n - 1) // 8 + 1), gm_view, gm_ref,
            nativeCoordinates={'programNumberOneBased': n, 'zeroBasedProgramIndex': n - 1, 'channelsExceptOneBased': [10]},
            sourceLocator={'printedPage': 5, 'pdfPageOneBased': 7, 'table': 2},
            sourceReading=program, exactAcousticTimbre=None, physicalInstrumentTypeIdentity=None,
            clippingStatus='Observed original clipping retained; missing characters not reconstructed' if program['clippedInOriginalImage'] else None)
    percussion_root = gm_root + ':percussion'
    add(percussion_root, 'GM1 channel 10 percussion map', 'gm1-percussion-map', gm_root, gm_view, gm_ref,
        nativeCoordinates={'channelOneBased': 10, 'midiKeyRange': [35, 81]})
    for percussion in gm['percussion']:
        add(percussion_root + ':key:' + str(percussion['midiKey']), percussion['name'], 'gm1-percussion-sound-address',
            percussion_root, gm_view, gm_ref, nativeCoordinates={'channelOneBased': 10, 'midiKey': percussion['midiKey']},
            sourceLocator={'printedPage': 6, 'pdfPageOneBased': 8, 'table': 3},
            exactAcousticTimbre=None, physicalInstrumentTypeIdentity=None)

    checks = []

    def check(name, condition):
        assert condition, name
        checks.append({'name': name, 'status': 'passed'})

    check('Source-image/PDF hashes and actual Jev64 selection verified',
          len(reading['forms']) == 4 and gm['pdfSha256'] == sha(gm['sourcePdf']))
    check('All 875 existing Western records and 1059 internal relationships preserved exactly',
          len(preserved) == 875 and len(preserved_relations) == 1059 and
          all(canonical(ids[e['id']]) == canonical(e) for e in preserved))
    check('Four source forms produce 48 contexts and 336 distinct degree classes',
          sum(e['unit'] == 'root-qualified-scale-form-context' for e in entities) == 48 and
          sum(e['unit'] == 'transposition-qualified-scale-degree' for e in entities) == 336 and
          len({tuple(f['offsets']) for f in reading['forms']}) == 4)
    counts = Counter((r['nativeCoordinates']['midiKey'], r['nativeCoordinates']['form']) for r in registered)
    check('2464 unique registered addresses give every one of 88 keys seven roots per form',
          len(registered) == 2464 and len({canonical(e['nativeCoordinates']) for e in registered}) == 2464 and
          len(counts) == 352 and set(counts.values()) == {7})
    check('Enharmonic notation roles round-trip to key addresses without collapsing spelling',
          all(12 * (r['registeredNote']['notationOctave'] + 1) + natural[r['registeredNote']['letter']] +
              r['registeredNote']['accidental'] == r['nativeCoordinates']['midiKey'] for r in registered) and
          any(r['registeredNote']['writtenPitch'].startswith('E#') for r in registered) and
          any(r['registeredNote']['writtenPitch'].startswith('Cb') for r in registered))
    profiles = [e for e in entities if e['unit'] == 'source-visible-range-profile']
    check('All 31 source profiles retain family counts 6/12/4/3/6 and unknown endpoints',
          len(profiles) == 31 and [len(v) for v in reading['rangeProfiles'].values()] == [6, 12, 4, 3, 6] and
          all(p['rangeLow'] is None and p['rangeHigh'] is None for p in profiles))
    check('Complete GM1 tables retain 16 families, 128 programs, 47 percussion keys and two clipped labels',
          len(gm['families']) == 16 and [p['programNumberOneBased'] for p in gm['programs']] == list(range(1, 129)) and
          {p['midiKey'] for p in gm['percussion']} == set(range(35, 82)) and
          [p['programNumberOneBased'] for p in gm['programs'] if p['clippedInOriginalImage']] == [25, 29] and
          all(len([p for p in gm['programs'] if f['programRangeOneBased'][0] <= p['programNumberOneBased'] <= f['programRangeOneBased'][1]]) == 8 for f in gm['families']))
    new_entities = entities[len(preserved):]
    check('All graph endpoints/parents resolve; new global GEN remains unknown and units remain separate',
          len(ids) == len(entities) and all(r['source'] in ids and r['target'] in ids for r in relations) and
          all(e['parent'] in ids for e in new_entities) and
          all(e['position']['generation'] is None and e['globalAddress']['generationClass'] is None for e in new_entities) and
          2464 + 31 + 128 + 47 == 2670)

    views = [copy.deepcopy(v) for v in original['views'] if v['id'] == 'music:western']
    views.extend([
        {'id': new_view, 'label': 'Western registered scale-degree addresses', 'roots': [top], 'witnessIds': refs},
        {'id': range_view, 'label': '31 source voice and instrument range profiles', 'roots': [range_root], 'witnessIds': ['western:source:key-range']},
        {'id': gm_view, 'label': 'GM1 sound programs and percussion addresses', 'roots': [gm_root], 'witnessIds': gm_ref}])
    result = {'schema': 'sunny.western-expanded.v1', 'status': 'bounded source-defined expansion; all-Western completeness open',
              'sources': sources, 'entities': entities, 'relationships': relations, 'views': views,
              'decisionReceipt': {'path': receipt_path, 'sha256': sha(receipt_path), 'model': jev['server_info']['model'],
                                  'selected': 'source_defined_class_expansion_first', 'historicalProof': False},
              'preservedInput': {'path': original_path, 'sha256': sha(original_path), 'westernRecords': 875,
                                 'internalRelations': 1059, 'entitySemanticsChanged': False},
              'generators': {'fourForms': reading['forms'], 'transpositionClasses': 12, 'rootFormContexts': 48,
                             'keyboardRange': [21, 108], 'registeredOccurrenceCount': 2464,
                             'proofOfCount': '4 forms x 88 key positions x 7 compatible transposition roots = 2464',
                             'representativeRootSpellings': roots, 'rootSpellingSelectionHistorical': False},
              'census': {'entityRecords': len(entities), 'relationshipRecords': len(relations), 'byUnit': dict(sorted(Counter(e['unit'] for e in entities).items())),
                         'preservedWesternRecords': 875, 'newRecords': len(new_entities),
                         'declaredLowerUnits': {'registeredScaleDegreeOccurrences': 2464, 'rangeProfiles': 31,
                                                'gm1Programs': 128, 'gm1PercussionAddresses': 47, 'sum': 2670},
                         'requestedRange': [2500, 2700], 'withinRequestedRange': True,
                         'unitsAreHeterogeneous': True, 'structuralRecordsNotAddedToLowerCount': True,
                         'wholeWesternMusicComplete': False},
              'sourceScope': {'fourRowsRead': True, 'rangeAll31VisibleLabelsRead': True,
                              'rangeEndpointsReliablyRead': False, 'gmOriginalPdfAcquired': True,
                              'gmTables1_2_3CompleteAgainstIdentifiedWitness': True,
                              'gmExactAcousticCharacteristicsDefined': False},
              'boundaries': ['Registered scale-degree occurrences are relational addresses, not 2464 distinct physical frequencies.',
                             '88 keyboard positions are the supplied range, not the complete Western note universe or 128 MIDI addresses.',
                             'Voice ranges, timpani sizes, instrument range profiles and GM sound addresses are different unit classes.',
                             'Instrument and voice endpoints remain unknown; no bounds reconstructed from blurred bars.',
                             'Source melodic-minor row supplies its raised-sixth/seventh collection, not a descending performance rule.',
                             'Computational root representatives preserve degree spellings and do not select a historical enharmonic identity.',
                             'GM1 sound programs include worldwide names and effects; they are not a Western physical-instrument catalogue.',
                             'Existing chords, modes, rhythm, form and source concept branches remain preserved.',
                             'Global SUNNY generation, orientation and common geometry alignment remain unresolved.'],
              'checks': checks, 'wholeMusicalSystemsComplete': False, 'missionIComplete': False}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {'status': 'passed', 'entityRecords': len(entities), 'relationshipRecords': len(relations),
               'views': len(views), 'checks': checks, 'lowerUnits': result['census']['declaredLowerUnits'],
               'outputSha256': sha(OUT.relative_to(ROOT)), 'inputOriginalUnchanged': sha(original_path) == result['preservedInput']['sha256']}
    (PACK / 'validation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    build()
