import os
import subprocess
import moviepy.editor as mp
from PIL import Image
from datetime import datetime
from vosk import Model, KaldiRecognizer
import wave
import json

# ディレクトリを作成する関数
def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# 音声をWAV形式のモノラルPCMに変換する関数
def convert_to_mono_pcm(input_audio_path, output_audio_path):
    command = [
        'ffmpeg',
        '-i', input_audio_path,
        '-ac', '1',
        '-ar', '16000',
        '-f', 'wav',
        output_audio_path
    ]
    subprocess.run(command, check=True)

# 音声をテキストに変換する関数
def transcribe_audio(audio_path, model_path):
    if not os.path.exists(model_path):
        print(f"モデルパス {model_path} が存在しません。")
        exit(1)

    wf = wave.open(audio_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 44100]:
        print("オーディオファイルはWAV形式のモノラルPCMである必要があります。")
        exit(1)

    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())

    text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get('text', '')

    result = json.loads(rec.FinalResult())
    text += result.get('text', '')

    return text

# 動画ファイルが保存されているディレクトリのパス
video_dir = "/Users/ryomuranaka/CreateMarkdown/video"  # 動画が保存されているディレクトリのパスに変更してください

# ディレクトリ内の.mp4ファイルを検索
video_file = None
for file in os.listdir(video_dir):
    if file.endswith(".mp4"):
        video_file = os.path.join(video_dir, file)
        break

if not video_file:
    print("ディレクトリ内に.mp4ファイルが見つかりません")
else:
    video = mp.VideoFileClip(video_file)

# 現在の日時を取得
current_time = datetime.now().strftime("%Y%m%d%H%M%S")

# 画像を保存するディレクトリ
frames_dir = f"frames_{current_time}"
create_dir(frames_dir)

# 2ごとに画像を切り取り保存する
frame_rate = 2  # フレームの間隔を3秒に設定
duration = int(video.duration)
frame_files = []
for t in range(0, duration, frame_rate):
    frame = video.get_frame(t)
    img = Image.fromarray(frame)
    frame_file = os.path.join(frames_dir, f"frame_{t}_{current_time}.png")
    try:
        img.save(frame_file)
        frame_files.append(frame_file)
    except Exception as e:
        print(f"フレーム {t} の保存中にエラーが発生しました: {e}")

# # 音声を抽出して保存する
# original_audio_path = f"audio_{current_time}.wav"
# video.audio.write_audiofile(original_audio_path)

# # 音声をWAV形式のモノラルPCMに変換する
# mono_pcm_audio_path = f"audio_mono_{current_time}.wav"
# convert_to_mono_pcm(original_audio_path, mono_pcm_audio_path)

# # 音声をテキストに変換する
# model_path = "/Users/ryomuranaka/CreateMarkdown/vosk-model-en-us-0.42-gigaspeech"  # ここにVosk日本語モデルのパスを指定
# text = transcribe_audio(mono_pcm_audio_path, model_path)

# # Markdownファイルに出力する
# md_file = f"output_{current_time}.md"
# with open(md_file, "w", encoding="utf-8") as file:
#     file.write("# 動画から抽出されたデータ\n\n")
#     file.write("## 音声のテキスト\n\n")
#     file.write(text + "\n\n")
#     file.write("## 抽出されたフレーム\n\n")
#     for frame_file in frame_files:
#         file.write(f"![frame]({frame_file})\n\n")

# print("プロジェクトが完了しました。")
print(f"画像は {frames_dir} に保存されました。")
# print(f"音声のテキストは {md_file} に保存されました。")
