"""Fresh source-byte, re-decode, WAV-header and independent statistic verification."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
import sys
import wave

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DECODER = Path(os.environ.get("SUNNY_MATCHED_AUDIO_DECODER", str(Path(os.environ["TEMP"])/"sunny-miniaudio-analysis")))
sys.path.insert(0, str(DECODER))
import miniaudio
import numpy as np

checks = []


def check(value, name):
    assert value, name
    checks.append({"name":name, "status":"passed"})


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE/name).read_text(encoding="utf-8-sig"))


def read_wav(path):
    with wave.open(str(path), "rb") as source:
        header = (source.getnchannels(), source.getframerate(), source.getsampwidth(), source.getnframes())
        samples = np.frombuffer(source.readframes(source.getnframes()), dtype="<i2")
    return header, samples


if __name__ == "__main__":
    acquisition, packet, method = read("acquisition.json"), read("measurements.json"), read("method-frozen.json")
    check(sha(HERE/"method-frozen.json")==acquisition["method_sha256"]==packet["method_sha256"], "Frozen method byte binding")
    check(sha(HERE/"acquisition.json")==packet["acquisition_sha256"], "Acquisition byte binding")
    method_time=datetime.fromisoformat(method["frozen_utc"].replace("Z","+00:00"))
    for source in acquisition["sources"]:
        check(method_time < datetime.fromisoformat(source["start_utc"]), "Method predates GET attempt: "+source["id"])
    for track in packet["tracks"]:
        identifier=track["id"]
        source=ROOT/track["source"]
        check(sha(source)==track["source_sha256"], "Exact publisher MP3 hash: "+identifier)
        rec=next(r for r in acquisition["sources"] if r["id"]==identifier)
        check(rec["http_status"]==200 and rec["requested_url"].startswith("https://doi.org/") and rec["final_url"].startswith("https://cdn.openbookpublishers.com/"), "Actual successful DOI-to-publisher retrieval: "+identifier)
        check(source.stat().st_size==rec["bytes"]==int(rec["headers"]["Content-Length"]), "Publisher Content-Length matches source bytes: "+identifier)
        for derived in track["derived"]:
            check(sha(ROOT/derived["path"])==derived["sha256"], "Exact derived hash: "+Path(derived["path"]).name)
        native_entry=next(r for r in track["derived"] if r["path"].endswith(".native-s16.wav"))
        analysis_entry=next(r for r in track["derived"] if r["path"].endswith(".mono16k-s16.wav"))
        opening_entry=next(r for r in track["derived"] if r["path"].endswith(".opening15s.wav"))
        native_header, native = read_wav(ROOT/native_entry["path"])
        analysis_header, analysis = read_wav(ROOT/analysis_entry["path"])
        opening_header, opening = read_wav(ROOT/opening_entry["path"])
        check(native_header==(2,44100,2,track["native_decode"]["frames"]), "Native WAV header/sample count: "+identifier)
        check(analysis_header==(1,16000,2,track["analysis_decode"]["frames"]), "Analysis WAV header/sample count: "+identifier)
        check(opening_header==(1,16000,2,240000) and np.array_equal(opening,analysis[:240000]), "Opening is exact first15s of derived waveform: "+identifier)
        check(abs(native_header[3]/native_header[1]-analysis_header[3]/analysis_header[1]) <= 1/16000, "Resampling duration differs by at most one analysis sample: "+identifier)
        fresh_native=miniaudio.mp3_read_file_s16(str(source))
        check(fresh_native.samples.tobytes()==native.tobytes(), "Fresh native re-decode equals retained PCM: "+identifier)
        fresh_analysis=miniaudio.decode_file(str(source), output_format=miniaudio.SampleFormat.SIGNED16, nchannels=1, sample_rate=16000, dither=miniaudio.DitherMode.NONE)
        check(fresh_analysis.samples.tobytes()==analysis.tobytes(), "Fresh mono16k re-decode equals retained PCM: "+identifier)
        squares=np.sum(native.astype(np.float64)**2)
        independent_rms=float(np.sqrt(squares/len(native))/32768)
        check(abs(independent_rms-track["native_statistics"]["rms_digital_fraction"])<1e-12, "Independent WAV RMS: "+identifier)
        check(int(np.count_nonzero((native==-32768)|(native==32767)))==track["native_statistics"]["full_scale_code_samples"], "Independent WAV full-scale code count: "+identifier)
        # Vectorized energy windows independently reproduce the recorded activity mark.
        windows=np.lib.stride_tricks.sliding_window_view(opening.astype(np.float64)/32768,160)[::80]
        above=np.sqrt(np.mean(windows**2,axis=1)) > .01
        onsets=np.flatnonzero(np.convolve(above.astype(int),np.ones(9,dtype=int),mode="valid")==9)
        activity=float(onsets[0]*.005) if len(onsets) else None
        check(activity==track["opening_0_15s"]["activity_mark_s"], "Independent energy-window activity mark: "+identifier)
        csv_entry=next(r for r in track["derived"] if r["path"].endswith(".opening-periodicity.csv"))
        with (ROOT/csv_entry["path"]).open(newline="",encoding="utf-8") as stream:
            rows=list(csv.DictReader(stream))
        accepted=[float(r["candidate_hz"]) for r in rows if r["status"]=="candidate"]
        check(len(rows)==1495 and len(accepted)==track["opening_0_15s"]["accepted_periodicity_candidates"], "CSV candidate accounting: "+identifier)
        check(float(np.median(accepted))==track["opening_0_15s"]["candidate_median_hz"], "CSV candidate median: "+identifier)
        # Compare FFT-derived correlation against direct dot products on20 fixed frames.
        direct_checks=0
        for index in range(0,len(rows),75):
            row=rows[index]
            if not row["nacf"]:
                continue
            frame=opening[index*160:index*160+960].astype(np.float64)/32768
            frame-=np.mean(frame)
            values=[]
            for lag in range(26,268):
                left,right=frame[:-lag],frame[lag:]
                values.append(float(np.dot(left,right)/max(np.linalg.norm(left)*np.linalg.norm(right),1e-30)))
            peaks=[i for i in range(1,len(values)-1) if values[i]>values[i-1] and values[i]>values[i+1]]
            strongest=max(values[i] for i in peaks)
            check(abs(strongest-float(row["nacf"]))<1e-7, "Direct dot-product periodicity check: "+identifier+" frame"+str(index))
            direct_checks+=1
        check(direct_checks>0, "Direct periodicity frames checked: "+identifier)
    check(len(packet["token_alignment"])==3 and packet["verified_aligned_tokens"]==0, "Three exposed token roles, zero asserted alignment")
    check(all(all(interval is None for interval in token["audio_intervals"].values()) and token["glottal_realization"]=="indeterminate" for token in packet["token_alignment"]), "Unknown alignment and glottal outcomes preserved")
    check(packet["new_model_requests"]==packet["persistent_processes_started"]==packet["protected_configuration_writes"]==0, "No new model requests, services or protected configuration writes declared")
    check(packet["decoder"]["new_packages_installed"]==0, "Existing decoder reused")
    artifacts=[p for p in HERE.rglob("*") if p.is_file() and p.name not in {"validation.json"} and "__pycache__" not in p.parts]
    artifacts.append(ROOT/"docs/research/MATCHED_AUDIO_CONTROL.md")
    result={"schema":"sunny.matched-audio.validation.v1", "created_utc":datetime.now(timezone.utc).isoformat(),
            "status":"passed","exit_code":0,"checks_passed":len(checks),"checks":checks,
            "bindings":{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(artifacts)},
            "scope":"Fresh local source/re-decode, digital statistic and provenance checks. No listening or source-token timing validated.",
            "not_verified":["Three Alef token timings/realizations", "Inter-performance token correspondence", "Ancient sound or global reconstruction"],
            "persistent_processes_started":0,"protected_configuration_writes":0}
    (HERE/"validation.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"passed","checks_passed":len(checks),"verified_aligned_tokens":0,"output":str(HERE/"validation.json")}))
