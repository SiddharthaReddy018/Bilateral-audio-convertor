import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import simpleaudio as sa
import librosa

file = input("Enter stereo audio file path: ")

data, sr = sf.read(file)

if len(data.shape) < 2:
    print("Need stereo file.")
    exit()

left = data[:,0]
right = data[:,1]

# Beat detection
y_mono = (left + right) / 2
tempo, beats = librosa.beat.beat_track(y=y_mono, sr=sr)
beat_times = librosa.frames_to_time(beats, sr=sr)

print("Detected BPM:", tempo)

# play audio
audio = (data * 32767).astype(np.int16)
play_obj = sa.play_buffer(audio, 2, 2, sr)

plt.figure(figsize=(12,6))

t = np.arange(len(left))/sr

plt.subplot(2,1,1)
plt.title("Left Channel")
plt.plot(t, left, linewidth=0.5)

for bt in beat_times:
    plt.axvline(bt, color="red", alpha=0.3)

plt.subplot(2,1,2)
plt.title("Right Channel")
plt.plot(t, right, linewidth=0.5)

for bt in beat_times:
    plt.axvline(bt, color="red", alpha=0.3)

plt.tight_layout()
plt.show()

play_obj.wait_done()