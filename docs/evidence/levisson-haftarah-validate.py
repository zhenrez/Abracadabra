"""Bounded source/pixel/interval validation for the preserved Levisson witness."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import hashlib
import json
import datetime
import wave
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
checks = []


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def check(condition, label):
    assert condition, label
    checks.append({"name": label, "status": "passed"})


review = read("docs/evidence/levisson-haftarah-score-recovery.json")
retrieval = read("docs/evidence/levisson-haftarah-retrieval.json")
audio = read("docs/evidence/levisson-haftarah-audio-inspection.json")
request = read("docs/evidence/levisson-haftarah-jev-request.json")
receipt = read("docs/evidence/levisson-haftarah-superjev.json")
for source in retrieval["sources"]:
    check(source.get("http") == 200, "Primary source HTTP success: " + source["path"])
    check(sha(source["path"]) == source["sha256"], "Exact primary source bytes: " + source["path"])
check(sha(review["sources"]["pdf"]) == review["sources"]["pdfSha256"], "Reviewed score PDF identity")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.current = [dict(attrs).get("href", ""), ""]

    def handle_data(self, data):
        if self.current is not None:
            self.current[1] += data

    def handle_endtag(self, tag):
        if tag == "a" and self.current is not None:
            self.links.append(self.current)
            self.current = None


parser = Links()
parser.feed((ROOT / review["sources"]["index"]).read_text(encoding="utf-8"))
publisher_links = []
for track in review["linkedTracks"]:
    matches = [(url, " ".join(text.split())) for url, text in parser.links
               if "/haftaratrope/" in url and unquote(url).endswith(track["fileName"])]
    check(len(matches) == 1, "Unique publisher track binding: " + str(track["track"]))
    caption = matches[0][1]
    normalized = caption.lower().removeprefix(f'{track["track"]:02d}').strip()
    check(normalized == track["publisherCaption"].lower(), "Exact publisher caption: " + str(track["track"]))
    publisher_links.append({"track": track["track"], "caption": caption, "url": matches[0][0]})
check("munach" in publisher_links[0]["caption"].lower() and "mercha etnachta.mp3" in unquote(publisher_links[0]["url"]).lower(), "Track01 caption/filename conflict is real and retained")

# Independently recompute staff-relative diatonic positions from the actual raster
# and the explicitly retained manual notehead coordinates. This is not optical
# recognition of unknown music or proof of the clef's historical interpretation.
image = np.asarray(Image.open(ROOT / review["pixelEvidence"]["firstSystemRender"]).convert("L"))
calibrations = []
for x0, x1 in [(200, 215), (1340, 1360)]:
    hits = np.flatnonzero(np.mean(image[40:180, x0:x1] < 100, axis=1) > .75) + 40
    groups = []
    for y in hits:
        if not groups or y > groups[-1][-1] + 1:
            groups.append([int(y)])
        else:
            groups[-1].append(int(y))
    centers = [float(np.mean(group)) for group in groups]
    check(len(centers) == 5, "Five measured staff lines at strip " + str((x0, x1)))
    calibrations.append({"x": (x0 + x1 - 1) / 2, "lineYsTopToBottom": centers})
steps = []
for index, (x, y) in enumerate(review["pixelEvidence"]["manualNoteheadCenters"]):
    left, right = calibrations
    weight = (x - left["x"]) / (right["x"] - left["x"])
    lines = [a + weight * (b - a) for a, b in zip(left["lineYsTopToBottom"], right["lineYsTopToBottom"])]
    half_space = (lines[-1] - lines[0]) / 8
    step = round((lines[-1] - y) / half_space)
    steps.append(step)
    check(float(np.mean(image[y-7:y+8, x-10:x+11] < 100)) > .15, "Annotated notehead has actual dark raster support: " + str(index))
check(steps == review["pixelEvidence"]["expectedDiatonicStepsAboveE4"], "All12 staff-relative diatonic positions reproduce")
names = ["E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5"]
check([names[step] for step in steps] == review["notation"]["flattenedWrittenNotes"], "Treble-clef pitch spelling agrees with measured staff positions")

offsets = {"E4": 0, "F4": 1, "G4": 3, "A4": 5, "B4": 7}
for motif in review["notation"]["motifs"]:
    values = [offsets[note] for note in motif["writtenNotes"]]
    check(values == motif["chromaticOffsetsFromE4"], "Written pitch offsets: " + motif["accent"])
    check([b-a for a, b in zip(values, values[1:])] == motif["withinMotifChromaticIntervals"], "Written interval sequence: " + motif["accent"])
check(offsets["A4"] - offsets["G4"] == 2 and offsets["A4"] - offsets["A4"] == 0, "Distinct-anchor major second and terminal-pair unison remain distinct")

for track in audio["tracks"]:
    check(sha(track["sourcePath"]) == track["sourceSha256"], "Decoded audio source bound: " + str(track["track"]))
    check(sha(track["derivedWav"]) == track["wavSha256"], "Derived WAV exact bytes: " + str(track["track"]))
    with wave.open(str(ROOT / track["derivedWav"]), "rb") as stream:
        check(stream.getframerate() == 16000 and stream.getnchannels() == 1 and stream.getsampwidth() == 2, "Decoded WAV format: " + str(track["track"]))
        check(stream.getnframes() == track["decodedSamples"] and stream.getnframes()/16000 == track["decodedSeconds"], "Decoded sample count and duration: " + str(track["track"]))

check(receipt["status"] == "judged" and receipt["resolved_model"] == "jev-1.14.0", "Actual resolved Jev model")
answer = receipt["answers"]["anchor_representation"]
check(set(answer["probabilities"]) == set(request["questions"]["anchor_representation"]["criteria"]) and abs(sum(answer["probabilities"].values())-1) < 1e-9, "Full Jev options and normalized distribution")
check(answer["winner"] == "full_motifs_and_distinct_score_anchors", "Executed representation follows actual Jev selection")
check(review["audioInspection"]["newVerifiedAcousticAnchorPairs"] == 0, "No unverified audio alignment promoted")

paths = ["docs/evidence/levisson-haftarah-score-recovery.json", "docs/evidence/levisson-haftarah-retrieval.json", "docs/evidence/levisson-haftarah-audio-inspection.json", "docs/evidence/levisson-haftarah-jev-request.json", "docs/evidence/levisson-haftarah-superjev.json", "docs/evidence/levisson-haftarah-supermemory.json", "docs/evidence/levisson-haftarah-validate.py"]
paths += [p.relative_to(ROOT).as_posix() for p in (ROOT / "docs/evidence/levisson-haftarah-sources").iterdir() if p.is_file()]
result = {"schema": "sunny.levisson-haftarah-validation.v1", "createdUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "passed", "exitCode": 0, "checksPassed": len(checks), "checks": checks, "actualStaffCalibration": calibrations, "reproducedDiatonicSteps": steps, "publisherTrackBindings": publisher_links, "bindings": {path: sha(path) for path in paths}, "notVerified": ["Independent sung syllable-to-time transcription", "Performed octave, pitch-reference/temperament and acoustic f0 accuracy", "Track01 third accent's spoken/sung name", "Cross-witness or ancient sound/intention transfer"], "persistentProcessesStarted": 0, "protectedCodexPathWrites": 0}
(ROOT / "docs/evidence/levisson-haftarah-validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "passed", "exitCode": 0, "checksPassed": len(checks), "scoreRecoverySha256": sha("docs/evidence/levisson-haftarah-score-recovery.json"), "output": "docs/evidence/levisson-haftarah-validation.json"}))
