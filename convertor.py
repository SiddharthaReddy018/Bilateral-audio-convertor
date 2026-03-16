import librosa
import numpy as np
import soundfile as sf
import argparse

# def bilateral_convert(input_path, output_path, mode='beat', toggle_freq=1.0):

#     print("Loading audio...")
#     y, sr = librosa.load(input_path, sr=None, mono=True)
#     n = len(y)

#     print("Processing mode:", mode)

#     if mode == 'beat':
#         tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
#         beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

#         if beat_times and beat_times[-1] < n/sr:
#             beat_times.append(n/sr)

#         times = beat_times

#     else:
#         half_period = 1.0 / (2 * toggle_freq)
#         times = np.arange(0, n/sr + half_period, half_period).tolist()

#         if times[-1] < n/sr:
#             times.append(n/sr)

#     out = np.zeros((n, 2), dtype=y.dtype)
#     left = True

#     for i in range(len(times)-1):

#         start_idx = int(times[i] * sr)
#         end_idx = int(times[i+1] * sr)

#         if left:
#             out[start_idx:end_idx, 0] = y[start_idx:end_idx]
#         else:
#             out[start_idx:end_idx, 1] = y[start_idx:end_idx]

#         left = not left

#     print("Saving output...")
#     sf.write(output_path, out, sr)
#     print("Done! Saved to:", output_path)


# if __name__ == "__main__":

#     parser = argparse.ArgumentParser(description="Bilateral Audio Converter")

#     parser.add_argument("-i", "--input", required=True,
#                         help="Path to input audio file")

#     parser.add_argument("-o", "--output", required=True,
#                         help="Path to output audio file")

#     parser.add_argument("-m", "--mode", choices=["beat", "fixed"],
#                         default="beat",
#                         help="Mode: beat or fixed")

#     parser.add_argument("-f", "--freq", type=float, default=2.0,
#                         help="Toggle frequency (Hz) for fixed mode")

#     args = parser.parse_args()

#     bilateral_convert(
#         args.input,
#         args.output,
#         mode=args.mode,
#         toggle_freq=args.freq
#     )

#version-2
# def bilateral_convert(input_path, output_path, mode='beat', toggle_freq=2.0):
#     print("Loading audio...")
#     y, sr = librosa.load(input_path, sr=None, mono=True)
#     n = len(y)
#     print("Processing mode:", mode)

#     if mode == 'beat':
#         tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
#         print(f"Detected tempo: {float(tempo):.1f} BPM")
#         beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

#         if not beat_times:
#             print("Warning: No beats detected, falling back to fixed mode.")
#             mode = 'fixed'  # fall through
#         else:
#             times = [0.0] + beat_times          # ← fix: don't drop pre-beat audio
#             if times[-1] < n / sr:
#                 times.append(n / sr)

#     if mode == 'fixed':
#         half_period = 1.0 / (2 * toggle_freq)
#         times = np.arange(0, n / sr, half_period).tolist()
#         times.append(n / sr)                    # always cap at audio end

#     out = np.zeros((n, 2), dtype=y.dtype)
#     left = True
#     for i in range(len(times) - 1):
#         start_idx = int(times[i] * sr)
#         end_idx = min(int(times[i + 1] * sr), n)  # clamp to avoid OOB
#         if left:
#             out[start_idx:end_idx, 0] = y[start_idx:end_idx]
#         else:
#             out[start_idx:end_idx, 1] = y[start_idx:end_idx]
#         left = not left

#     print("Saving output...")
#     sf.write(output_path, out, sr)
#     print("Done! Saved to:", output_path)

    
def bilateral_convert(input_path, output_path, mode="beat", toggle_freq=2.0, fade_ms=15):

    print("Loading audio...")
    y, sr = librosa.load(input_path, sr=None, mono=True)
    n = len(y)

    print("Processing mode:", mode)

    # ----------- SEGMENT TIMES -----------
    if mode == "beat":
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        print(f"Detected tempo: {float(tempo):.1f} BPM")

        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        if len(beat_times) == 0:
            print("No beats detected → switching to fixed mode")
            mode = "fixed"
        else:
            times = np.concatenate(([0], beat_times, [n/sr]))

    if mode == "fixed":
        half_period = 1.0 / (2 * toggle_freq)
        times = np.arange(0, n/sr, half_period)
        times = np.append(times, n/sr)

    # ----------- OUTPUT BUFFER -----------
    out = np.zeros((n, 2), dtype=np.float32)

    fade_len = int(sr * fade_ms / 1000)
    fade = np.linspace(0, 1, fade_len)

    left_side = True

    for i in range(len(times) - 1):

        start = int(times[i] * sr)
        end = int(times[i + 1] * sr)
        end = min(end, n)

        segment = y[start:end].copy()

        # APPLY FADE IN/OUT
        if len(segment) > fade_len * 2:
            segment[:fade_len] *= fade
            segment[-fade_len:] *= fade[::-1]

        if left_side:
            out[start:end, 0] = segment
        else:
            out[start:end, 1] = segment

        left_side = not left_side

    print("Saving output...")
    sf.write(output_path, out, sr)
    print("Done! Saved to:", output_path)

if __name__ == "__main__":

    input_path = input("Enter input file path: ").strip()
    output_path = input("Enter output file path: ").strip()
    mode = input("Mode (beat/fixed): ").strip().lower()

    freq = 2.0
    if mode == "fixed":
        freq = float(input("Enter frequency (Hz): "))

    bilateral_convert(input_path, output_path, mode, freq)