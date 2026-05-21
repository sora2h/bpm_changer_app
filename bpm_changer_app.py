import math
from pydub.generators import WhiteNoise
import os
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

from tkinterdnd2 import DND_FILES, TkinterDnD
import librosa
from pydub import AudioSegment
from pydub.generators import Sine

def create_metronome_track(bpm, duration_ms):
    interval_ms = 60000 / bpm
    hi_hat_noise = WhiteNoise().to_audio_segment(duration=100)
    click = hi_hat_noise.fade_out(duration=80).apply_gain(-15) 
    
    silence_duration = interval_ms - len(click)
    if silence_duration < 0:
        silence_duration = 0

    silence = AudioSegment.silent(duration=silence_duration)
    one_beat = click + silence
    
    num_beats = math.ceil(duration_ms / interval_ms)
    
    metronome_track = one_beat * num_beats
    
    return metronome_track[:duration_ms]

def change_audio_bpm(input_path, output_path, target_bpm, add_metronome):
    try:
        y, sr = librosa.load(input_path, sr=None)

        original_bpm, _ = librosa.beat.beat_track(y=y, sr=sr)
        original_bpm = float(original_bpm)

        if original_bpm == 0:
            print(f"BPMが検出できませんでした: {os.path.basename(input_path)}")
            return False

        speed_ratio = target_bpm / original_bpm
        print(f"ファイル: {os.path.basename(input_path)}, 元BPM: {original_bpm:.2f}, 変更率: {speed_ratio:.2f}")

        audio = AudioSegment.from_file(input_path)
        changed_audio = audio.speedup(playback_speed=speed_ratio)
        
        if add_metronome:
            metronome = create_metronome_track(target_bpm, len(changed_audio))
            final_audio = changed_audio.overlay(metronome)
        else:
            final_audio = changed_audio
        
        file_format = input_path.split('.')[-1]
        final_audio.export(output_path, format=file_format)
        
        return True
    except Exception as e:
        print(f"エラーが発生しました ({os.path.basename(input_path)}): {e}")
        return False

class BpmChangerApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("BPM一括変更ツール")
        self.geometry("400x200")

        self.label = tk.Label(
            self,
            text="ここにフォルダをドラッグ＆ドロップしてください",
            font=("Helvetica", 12),
            bg="lightgrey",
            padx=20,
            pady=20
        )
        self.label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        folder_path = event.data.strip('{}')
        if not os.path.isdir(folder_path):
            messagebox.showerror("エラー", "フォルダをドロップしてください。")
            return

        target_bpm_str = simpledialog.askstring("BPM指定", "目標のBPMを入力してください (例: 128)")
        if not target_bpm_str or not target_bpm_str.isdigit():
            messagebox.showwarning("キャンセル", "BPMが正しく入力されなかったため、処理を中断しました。")
            return
        
        target_bpm = int(target_bpm_str)

        add_metronome = messagebox.askyesno(
            "メトロノーム追加",
            f"BPM {target_bpm} のメトロノーム音を追加しますか？"
        )
        
        self.label.config(text=f"処理を開始します... (BPM: {target_bpm})")
        process_thread = threading.Thread(
            target=self.process_files,
            args=(folder_path, target_bpm, add_metronome)
        )
        process_thread.start()

    def process_files(self, folder_path, target_bpm, add_metronome):
        output_folder = os.path.join(folder_path, "bpm_changed")
        os.makedirs(output_folder, exist_ok=True)

        files_to_process = [
            f for f in os.listdir(folder_path)
            if f.lower().endswith(('.mp3', '.wav'))
        ]
        
        total_files = len(files_to_process)
        success_count = 0

        for i, filename in enumerate(files_to_process):
            self.label.config(text=f"処理中 ({i+1}/{total_files}): {filename}")
            
            input_path = os.path.join(folder_path, filename)
            
            base_name, ext = os.path.splitext(filename)
            output_filename = f"{base_name}_{target_bpm}bpm{ext}"
            output_path = os.path.join(output_folder, output_filename)
            
            if change_audio_bpm(input_path, output_path, target_bpm, add_metronome):
                success_count += 1
        
        self.label.config(text="ここにフォルダをドラッグ＆ドロップしてください")
        messagebox.showinfo(
            "完了",
            f"処理が完了しました。\n\n"
            f"対象ファイル数: {total_files}\n"
            f"成功: {success_count}\n"
            f"出力先: {output_folder}"
        )

if __name__ == "__main__":
    app = BpmChangerApp()
    app.mainloop()