"""Faithful glyph/IPA transcription of the user's supplied table, not a historical edition."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMMON = 'ʔ b g d h w z ħ tˤ j k l m n s ʕ p sˤ q r ʃ t'
PHOENICIAN = '𐤀𐤁𐤂𐤃𐤄𐤅𐤆𐤇𐤈𐤉𐤊𐤋𐤌𐤍𐤎𐤏𐤐𐤑𐤒𐤓𐤔𐤕'
ROWS = [
 ('Proto-Sinaitic (proxy)', PHOENICIAN, COMMON, 'proxy', 'semitic'),
 ('Ugaritic', '𐎀𐎁𐎂𐎃𐎄𐎅𐎆𐎇𐎈𐎉𐎊𐎋𐎌𐎍𐎎𐎏𐎐𐎑𐎒𐎓𐎔𐎕𐎖𐎗𐎘𐎙𐎚𐎛𐎜𐎝', 'ʔa b g x d h w z ħ tˤ j k ʃ l m ð n zˤ s ʕ p sˤ q r θ ɣ t ʔi ʔu s', 'historical_table_values', 'semitic'),
 ('Phoenician', PHOENICIAN, COMMON, 'historical_table_values', 'semitic'),
 ('Paleo-Hebrew', PHOENICIAN, COMMON, 'unicode_proxy', 'semitic'),
 ('Sabaic / South Arabian', '𐩠𐩡𐩢𐩣𐩤𐩥𐩦𐩧𐩨𐩩𐩪𐩫𐩬𐩭𐩮𐩯𐩰𐩱𐩲𐩳𐩴𐩵𐩶𐩷𐩸𐩹𐩺𐩻𐩼', 'h l ħ m q w ʃ r b t s k n x sˤ ɬˤ f ʔ ʕ ðˤ g d ɣ tˤ z ð j θ s³', 'historical_table_values', 'semitic'),
 ('Imperial Aramaic', '𐡀𐡁𐡂𐡃𐡄𐡅𐡆𐡇𐡈𐡉𐡊𐡋𐡌𐡍𐡎𐡏𐡐𐡑𐡒𐡓𐡔𐡕', COMMON, 'historical_table_values', 'semitic'),
 ('Ancient Greek (Ionic)', 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ', 'a b g d e zd ɛː tʰ i k l m n ks o p r s t y pʰ kʰ ps ɔː', 'period_specific_table_values', 'greek_derived'),
 ('Etruscan (26-character model)', '𐌀𐌁𐌂𐌃𐌄𐌅𐌆𐌇𐌈𐌉𐌊𐌋𐌌𐌍𐌎𐌏𐌐𐌑𐌒𐌓𐌔𐌕𐌖𐌗𐌘𐌙', 'a ? k ? e v z h tʰ i k l m n ʃ u p ? kʷ r s t u kʰ f ?', 'model_with_unknowns', 'greek_derived'),
 ('Old Latin (21-character convention)', 'ABCDEFZHIKLMNOPQRSTVX', 'a b k d e f z h i k l m n o p kʷ r s t u ks', 'convention', 'greek_derived'),
 ('Old Persian', '𐎠𐎡𐎢𐎣𐎤𐎥𐎦𐎧𐎨𐎩𐎪𐎫𐎬𐎭𐎮𐎯𐎰𐎱𐎲𐎳𐎴𐎵𐎶𐎷𐎸𐎹𐎺𐎻𐎼𐎽𐎾𐎿𐏀𐏁𐏂𐏃', 'a i u ka ku ga gu xa ca ja ji ta tu da di du θa pa ba fa na nu ma mi mu ja va vi ra ru la sa za ʃa ʃːa ha', 'syllabic_table_values', 'old_persian'),
 ('Square Hebrew', 'אבגדהוזחטיכלמנסעפצקרשת', 'ʔ b/v g/ɣ d/ð h v/w z χ/ħ t j k/x l m n s ʔ/ʕ p/f ts q r ʃ/s t/θ', 'mixed_period_alternatives', 'semitic'),
 ('Syriac', 'ܐܒܓܕܗܘܙܚܛܝܟܠܡܢܣܥܦܨܩܪܫܬ', 'ʔ b/v g/ɣ d/ð h w z ħ tˤ j k/x l m n s ʕ p/f sˤ q r ʃ t/θ', 'alternatives', 'semitic'),
 ('Old English (Futhorc)', 'ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ', 'f u θ/ð o r tʃ/k g/j w h n i j eo p ks s t b e m l ŋ œ d ɑ æ y io æɑ', 'period_specific_alternatives', 'greek_derived'),
 ('Old Arabic (28-letter proxy)', 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي', 'ʔ/aː b t θ dʒ ħ x d ð r z s ʃ sˤ dˤ tˤ ðˤ ʕ ɣ f q k l m n h w/uː j/iː', 'proxy', 'semitic'),
 ('English', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'eɪ biː siː diː iː ɛf dʒiː eɪtʃ aɪ dʒeɪ keɪ ɛl ɛm ɛn oʊ piː kjuː ɑɹ ɛs tiː juː viː ˈdʌbəljuː ɛks waɪ ziː', 'letter_names', 'greek_derived'),
]

def dataset():
    cells = []
    for name, glyphs, ipa, role, block in ROWS:
        values = ipa.split()
        if len(glyphs) != len(values) or len(values) > 36:
            raise ValueError((name, len(glyphs), len(values)))
        for column in range(1, 37):
            present = column <= len(values)
            cells.append(dict(script=name, column=column, glyph=glyphs[column-1] if present else None,
                              ipa=values[column-1] if present else None, role=role, block=block,
                              historical_validation='not_independently_validated', graph=None))
    return dict(schema='ariadne.user-table.v1', source='Current user-supplied table; manual glyph/IPA transcription; English gloss rows not used as IPA.',
                conversation_reference='6ae9304f-c5c8-83e8-9993-26deecd505e6', cells=cells)

if __name__ == '__main__':
    (ROOT / 'table.json').write_text(json.dumps(dataset(), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines=['\t'.join(['Alphabet']+[str(i) for i in range(1,37)])]
    for name,glyphs,ipa,_,_ in ROWS:
        lines.append('\t'.join([name]+list(glyphs)+['']*(36-len(glyphs))))
        values=ipa.split(); lines.append('\t'.join(['IPA']+values+['']*(36-len(values))))
    (ROOT/'table.tsv').write_text('\n'.join(lines)+'\n',encoding='utf-8')
