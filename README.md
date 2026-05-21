# BPM Changer App

フォルダ内の音声ファイルを指定BPMへ一括変換するGUIツールです。

## 機能

- フォルダのドラッグ＆ドロップ
- `.mp3` / `.wav` ファイルの一括処理
- `librosa` によるBPM検出
- 指定BPMに合わせた再生速度変更
- 任意でメトロノーム音を追加
- 変換後ファイルを `bpm_changed` フォルダへ出力

## 使い方

1. アプリを起動します。

```bash
python bpm_changer_app.py
```

2. 音声ファイルが入ったフォルダを画面へドラッグ＆ドロップします。
3. 目標BPMを入力します。
4. メトロノーム音を追加するか選択します。
5. 処理が完了すると、ドロップしたフォルダ内に `bpm_changed` フォルダが作成されます。

## 出力

出力ファイルは以下の形式で保存されます。

```text
bpm_changed/元ファイル名_指定BPMbpm.拡張子
```

例：

```text
bpm_changed/sample_128bpm.mp3
```

## 対応ファイル

- `.mp3`
- `.wav`

## 必要なライブラリ

```bash
pip install librosa pydub tkinterdnd2
```

## 処理内容

1. 音声ファイルを読み込みます。
2. `librosa.beat.beat_track()` でBPMを検出します。
3. 指定BPMとの比率を計算します。
4. `AudioSegment.speedup()` で再生速度を変更します。
5. メトロノーム追加を選択した場合は、`WhiteNoise` で生成したクリック音を重ねます。
6. 変換後ファイルを出力します。

## メトロノーム音

メトロノーム音は、`pydub.generators.WhiteNoise` で生成します。

外部のクリック音ファイルは使用しません。

## 備考

- 元ファイルは上書きされません。
- 処理対象は、ドロップしたフォルダ直下の `.mp3` / `.wav` ファイルです。
- BPMを検出できないファイルは処理されません。
