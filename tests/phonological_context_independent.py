"""Independent source-extraction and symbolic countermodel checks."""
from pathlib import Path
import hashlib,json,unicodedata,unittest
import pypdfium2
import sympy as S
ROOT=Path(__file__).resolve().parents[1]

class ContextChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'state/reconstruction/phonological-context-constraints.json').read_text(encoding='utf8'))
    def test_second_extractor_confirms_published_forms_not_manuscript_truth(self):
        path=ROOT/'state/delivery-2026-11-07/symbol-contact/root/howard-2026-qames.pdf'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),self.data['source']['pdfSha256'])
        doc=pypdfium2.PdfDocument(path);page=doc[4];text=page.get_textpage().get_text_bounded()
        normalize=lambda x:unicodedata.normalize('NFC',''.join(x.split()))
        for row in self.data['sourceCases']:self.assertIn(normalize(row['publishedGreekForm']),normalize(text))
        self.assertIn('θεσαδηνι',normalize(text))
        doc.close()
    def test_exact_continuous_countermodels_to_date_transfer(self):
        # Normalize the local event to0 and consonantal change to1. No historical date is assigned.
        g=S.Symbol('g',real=True)
        self.assertEqual(S.reduce_inequalities([g>0,g>1],g).as_set(),S.Interval.open(1,S.oo))
        self.assertEqual(S.reduce_inequalities([g>0,g<1],g).as_set(),S.Interval.open(0,1))
        orders=self.data['chronology']['allStrictLinearExtensions'];self.assertEqual(len(orders),2)
        self.assertEqual({tuple(o) for o in orders},{('L_local_pre_waw_rounding','V_w_to_v','G_general_syllable_shift'),('L_local_pre_waw_rounding','G_general_syllable_shift','V_w_to_v')})
    def test_disputed_reading_keeps_all_branches_and_scope(self):
        cases=self.data['conditionalExecutions'];self.assertEqual([c['checkedContexts'] for c in cases],[6,6,5])
        self.assertEqual([len(c['simpleSuffixConditionConflicts']) for c in cases],[0,1,0])
        self.assertEqual(cases[1]['simpleSuffixConditionConflicts'],['Ps18:36'])
        self.assertTrue(self.data['disputedThemeVowel']['primaryCollationPending'])
        self.assertFalse(self.data['originalSoundRecovered']);self.assertFalse(self.data['historicalGenealogySelected'])

if __name__=='__main__':unittest.main()
