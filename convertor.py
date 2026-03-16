import librosa
import numpy as np
import soundfile as sf
import argparse

def bilateral_convert(input_path, output_path, mode='beat', toggle_freq=1.0):

    print("Loading audio...")
    y, sr = librosa.load(input_path, sr=None, mono=True)
    n = len(y)

    print("Processing mode:", mode)

    if mode == 'beat':
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()

        if beat_times and beat_times[-1] < n/sr:
            beat_times.append(n/sr)

        times = beat_times

    else:
        half_period = 1.0 / (2 * toggle_freq)
        times = np.arange(0, n/sr + half_period, half_period).tolist()

        if times[-1] < n/sr:
            times.append(n/sr)

    out = np.zeros((n, 2), dtype=y.dtype)
    left = True

    for i in range(len(times)-1):

        start_idx = int(times[i] * sr)
        end_idx = int(times[i+1] * sr)

        if left:
            out[start_idx:end_idx, 0] = y[start_idx:end_idx]
        else:
            out[start_idx:end_idx, 1] = y[start_idx:end_idx]

        left = not left

    print("Saving output...")
    sf.write(output_path, out, sr)
    print("Done! Saved to:", output_path)


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

if __name__ == "__main__":

    input_path = input("Enter input file path: ")
    output_path = input("Enter output file path: ")
    mode = input("Mode (beat/fixed): ").strip().lower()

    freq = 2.0
    if mode == "fixed":
        freq = float(input("Enter frequency (Hz): "))

    bilateral_convert(input_path, output_path, mode, freq)