"""Reuse the existing source collector for this bounded Western method packet."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import importlib.util, json, sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
SYMBOL_COLLECTOR = ROOT.parent / "symbols" / "collect_sources.py"
spec = importlib.util.spec_from_file_location("sunny_existing_source_collector", SYMBOL_COLLECTOR)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
collector.ROOT = ROOT
sources = [
 ("praat_source_filter", "https://www.fon.hum.uva.nl/praat/manual/Source-filter_synthesis.html", ".html"),
 ("praat_spectrogram", "https://www.fon.hum.uva.nl/praat/manual/Sound__To_Spectrogram___.html", ".html"),
 ("praat_bada", "https://www.fon.hum.uva.nl/praat/manual/Source-filter_synthesis_3__The_ba-da_continuum.html", ".html"),
 ("garellek2013", "https://pages.ucsd.edu/~mgarellek/files/Garellek_dissertation.pdf", ".pdf"),
]
if __name__ == "__main__":
 with ThreadPoolExecutor(max_workers=4) as executor:
  results = list(executor.map(collector.fetch, sources))
 (ROOT / "source-fetch-manifest-02.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf8")
 print(json.dumps(results, ensure_ascii=False, indent=2))
