"""Decode pinned modern recordings; compute exposed, non-linguistic controls."""
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
DECODER = Path(os.environ.get("SUNNY_MATCHED_AUDIO_DECODER", str(Path(os.environ["TEMP"]) / "sunny-miniaudio-analysis")))
sys.path.insert(0, str(DECODER))
import miniaudio
import numpy as np
import scipy
from scipy.signal import correlate, find_peaks, spectrogram
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def wav(path, samples, sample_rate, channels):
    with wave.open(str(path), "wb") as output:
        output.setnchannels(channels)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(samples.tobytes())


def periodicity(x, sample_rate=16000):
    # This reproduces the frozen exploratory procedure; no target labels enter.
    records = []
    width, hop = 960, 160
    for start in range(0, len(x) - width + 1, hop):
        raw = x[start:start+width].astype(np.float64) / 32768
        rms = float(np.sqrt(np.mean(raw*raw)))
        rms_dbfs = float(20*np.log10(max(rms, 1e-12)))
        row = {"time_s": round((start+width/2)/sample_rate, 6), "rms_dbfs": round(rms_dbfs, 6),
               "candidate_hz": None, "nacf": None, "status": "below_energy_gate"}
        if rms_dbfs > -40:
            centered = raw - np.mean(raw)
            products = correlate(centered, centered, mode="full", method="fft")[width-1:]
            energy = np.concatenate(([0.0], np.cumsum(centered**2)))
            lags = np.arange(26, 268)
            norms = np.sqrt(energy[width-lags] * (energy[width]-energy[lags]))
            values = products[lags] / np.maximum(norms, 1e-30)
            peaks, _ = find_peaks(values)
            if len(peaks):
                index = int(peaks[np.argmax(values[peaks])])
                peak = float(values[index])
                row.update(nacf=round(peak, 8), status="periodicity_rejected")
                if peak >= .8:
                    y0, y1, y2 = values[index-1:index+2]
                    denominator = y0 - 2*y1 + y2
                    adjustment = float(.5*(y0-y2)/denominator) if abs(denominator)>1e-12 else 0
                    lag = float(lags[index]) + adjustment
                    row.update(candidate_hz=round(sample_rate/lag, 6), status="candidate")
            else:
                row["status"] = "no_local_peak"
        records.append(row)
    return records


def process(source, column, axes):
    identifier = source["id"]
    condition = "without melody" if identifier.endswith("06") else "with Sefardi melody"
    path = ROOT / source["path"]
    assert sha(path) == source["sha256"]
    info = miniaudio.mp3_get_file_info(str(path))
    native = miniaudio.mp3_read_file_s16(str(path))
    native_array = np.asarray(native.samples, dtype=np.int16)
    native_wav = HERE / "derived" / (identifier + ".native-s16.wav")
    wav(native_wav, native_array, native.sample_rate, native.nchannels)
    decoded = miniaudio.decode_file(str(path), output_format=miniaudio.SampleFormat.SIGNED16,
                                   nchannels=1, sample_rate=16000, dither=miniaudio.DitherMode.NONE)
    values = np.asarray(decoded.samples, dtype=np.int16)
    analysis_wav = HERE / "derived" / (identifier + ".mono16k-s16.wav")
    wav(analysis_wav, values, 16000, 1)
    opening = values[:15*16000]
    opening_wav = HERE / "derived" / (identifier + ".opening15s.wav")
    wav(opening_wav, opening, 16000, 1)
    normalized = native_array.astype(np.float64) / 32768
    rms = float(np.sqrt(np.mean(normalized**2)))
    rms_frames = []
    for start in range(0, len(opening)-160+1, 80):
        frame = opening[start:start+160].astype(np.float64)/32768
        value = max(float(np.sqrt(np.mean(frame**2))), 1e-12)
        rms_frames.append({"start_s": start/16000, "center_s": (start+80)/16000, "rms_dbfs": float(20*np.log10(value))})
    # 10ms windows separated by 5ms: 9 consecutive windows cover 50ms.
    activity = None
    for index in range(len(rms_frames)-8):
        if all(frame["rms_dbfs"] > -40 for frame in rms_frames[index:index+9]):
            activity = rms_frames[index]["start_s"]
            break
    candidates = periodicity(opening)
    candidate_values = np.array([row["candidate_hz"] for row in candidates if row["candidate_hz"] is not None])
    csv_path = HERE / "derived" / (identifier + ".opening-periodicity.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["time_s", "rms_dbfs", "candidate_hz", "nacf", "status"])
        writer.writeheader()
        writer.writerows(candidates)
    rms_path = HERE / "derived" / (identifier + ".opening-rms.csv")
    with rms_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=["start_s", "center_s", "rms_dbfs"])
        writer.writeheader()
        writer.writerows(rms_frames)
    signal = opening.astype(np.float64)/32768
    time = np.arange(len(signal))/16000
    axes[0, column].plot(time[::4], signal[::4], linewidth=.35)
    axes[0, column].set(title=identifier+" — "+condition, ylabel="Digital amplitude", ylim=(-1,1))
    axes[1, column].plot([r["center_s"] for r in rms_frames], [r["rms_dbfs"] for r in rms_frames], linewidth=.7)
    axes[1, column].axhline(-40, color="red", linewidth=.6, linestyle="--")
    if activity is not None:
        axes[1, column].axvline(activity, color="green", linewidth=.8)
    axes[1, column].set(ylabel="RMS (dBFS)", ylim=(-100,0))
    frequencies, times, power = spectrogram(signal, fs=16000, window="hann", nperseg=400,
                                           noverlap=320, nfft=1024, detrend=False, scaling="density", mode="psd")
    axes[2, column].pcolormesh(times, frequencies, 10*np.log10(np.maximum(power,1e-16)),
                              shading="auto", vmin=-110, vmax=-35, cmap="magma")
    axes[2, column].set(ylabel="Frequency (Hz)", ylim=(0,5000))
    valid = [row for row in candidates if row["candidate_hz"] is not None]
    axes[3, column].scatter([r["time_s"] for r in valid], [r["candidate_hz"] for r in valid], s=2)
    axes[3, column].set(ylabel="Periodicity candidate (Hz)", xlabel="Seconds from decoded-file origin", ylim=(50,650))
    for row in range(4):
        axes[row, column].set_xlim(0,15)
        axes[row, column].grid(alpha=.18)
    derived = [native_wav, analysis_wav, opening_wav, csv_path, rms_path]
    return {
        "id": identifier, "reader": "Alex Foreman", "condition": condition,
        "source": source["path"], "source_sha256": source["sha256"],
        "mp3_info": {"sample_rate": info.sample_rate, "channels": info.nchannels,
                      "num_frames": info.num_frames, "duration_s": info.duration},
        "native_decode": {"sample_rate": native.sample_rate, "channels": native.nchannels,
                          "interleaved_samples": len(native_array), "frames": native.num_frames,
                          "duration_s": native.num_frames/native.sample_rate, "sample_format": "signed16 PCM"},
        "native_statistics": {"peak_absolute_digital_fraction": float(np.max(np.abs(normalized))),
                              "rms_digital_fraction": rms, "rms_dbfs": float(20*np.log10(max(rms,1e-12))),
                              "full_scale_code_samples": int(np.sum((native_array==-32768)|(native_array==32767))),
                              "exact_zero_code_samples": int(np.sum(native_array==0)),
                              "limit": "Digital values only; full-scale codes are not proof of clipping and zeros do not establish phonetic silence."},
        "analysis_decode": {"sample_rate":16000, "channels":1, "sample_format":"signed16 PCM", "frames":len(values), "duration_s":len(values)/16000,
                            "resampling": "miniaudio decode_file conversion from native source; no dither; no additional denoising/normalization"},
        "opening_0_15s": {"actual_duration_s":len(opening)/16000, "activity_mark_s":activity,
                          "activity_mark_is_linguistic_boundary":False, "periodicity_frames":len(candidates),
                          "accepted_periodicity_candidates":len(candidate_values),
                          "candidate_median_hz": float(np.median(candidate_values)) if len(candidate_values) else None,
                          "candidate_10_90_percentile_hz": np.percentile(candidate_values,[10,90]).tolist() if len(candidate_values) else None,
                          "limit":"Exposed opening time window, with octave/subharmonic ambiguity. No token or melodic comparison is inferred from these pooled values."},
        "derived": [{"path": p.relative_to(ROOT).as_posix(), "bytes":p.stat().st_size, "sha256":sha(p)} for p in derived],
    }


if __name__ == "__main__":
    acquisition = json.loads((HERE/"acquisition.json").read_text(encoding="utf-8"))
    assert acquisition["method_sha256"] == sha(HERE/"method-frozen.json")
    (HERE/"derived").mkdir(exist_ok=True)
    fig, axes = plt.subplots(4,2, figsize=(16,12), sharex="col")
    sources = [r for r in acquisition["sources"] if r["id"].startswith("OBP.") and r["status"]=="acquired"]
    assert len(sources)==2
    results = [process(source, column, axes) for column, source in enumerate(sources)]
    fig.suptitle("Modern Tiberian performance control: fixed opening 0–15 s; no syllable alignment", fontsize=14)
    fig.tight_layout(rect=(0,0,1,.97))
    plot_path = HERE/"derived"/"opening-comparison.png"
    fig.savefig(plot_path,dpi=140)
    plt.close(fig)
    tokens = [{"id":f"Gen1.1-w{index}-alef", "documentary_role":role, "audio_intervals":{source["id"]:None for source in sources},
               "glottal_realization":"indeterminate", "reason":"No actual listening or independently validated token alignment in this run."}
              for index,role in [(1,"No corresponding [ʔ] marker in displayed first profile"),(2,"No corresponding [ʔ] marker in displayed first profile"),(3,"Initial [ʔ] explicitly marked")]]
    packet={"schema":"sunny.matched-audio.measurements.v1", "created_utc":datetime.now(timezone.utc).isoformat(),
            "method_sha256":sha(HERE/"method-frozen.json"), "acquisition_sha256":sha(HERE/"acquisition.json"),
            "decoder":{"module_path":str(Path(miniaudio.__file__).resolve()), "python_binding_version":miniaudio.__version__,
                       "native_library_version":miniaudio.lib_version(), "existing_environment_reused":True,
                       "module_sha256":sha(miniaudio.__file__), "native_extension_sha256":sha(DECODER/"_miniaudio.pyd"),
                       "new_packages_installed":0},
            "analysis_runtime":{"python":sys.version, "numpy":np.__version__, "scipy":scipy.__version__, "matplotlib":matplotlib.__version__},
            "tracks":results, "token_alignment":tokens, "verified_aligned_tokens":0,
            "plot":{"path":plot_path.relative_to(ROOT).as_posix(),"sha256":sha(plot_path)},
            "exposure":"Prior documentary source roles and retained Jev direction were known; opening analysis is exposed and not a blind prediction.",
            "not_established":["Any Alef token's phonetic realization", "Duration of a source-aligned glottal event", "Pitch of a particular source syllable",
                               "Equal phonetic behavior between the two conditions", "Ancient waveform, inventor intention, native Western prescription or absolute Hz per glyph"],
            "new_model_requests":0,"persistent_processes_started":0,"protected_configuration_writes":0}
    write_json(HERE/"measurements.json", packet)
    print(json.dumps({"status":"decoded_and_measured", "tracks":[{k:r[k] for k in ["id","native_decode","native_statistics","opening_0_15s"]} for r in results],
                      "verified_aligned_tokens":0,"new_packages_installed":0}))
