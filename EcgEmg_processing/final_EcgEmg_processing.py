import os
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 기본 경로 설정
root_dir = r"Z:\EEG\haptic\DSI_가야금\HAPTIC DATA\\20250123"

def get_segments(labels):
    segments = []
    start = 0
    current_label = labels[0]
    for i in range(1, len(labels)):
        if labels[i] != current_label:
            segments.append((start, i, current_label))
            start = i
            current_label = labels[i]
    segments.append((start, len(labels), current_label))
    return segments

def process_file(filepath):
    # 파일명 기반 base_name 생성
    dir_split = filepath.split(os.sep)
    filename = os.path.basename(filepath)
    if len(dir_split) < 2 or len(filename) < 11:
        print(f"Skipping {filename}: 디렉토리 깊이 또는 파일명 길이가 부족합니다.")
        return
    base_name = dir_split[-3][2:] + "_" + dir_split[-2] + dir_split[-1][9:11]
    # CSV 파일 읽기
    try:
        data = pd.read_csv(filepath)
    except Exception as e:
        print(f"파일 읽기 오류: {filepath} - {e}")
        return

    if data.shape[1] < 7:
        print(f"컬럼 수 부족: {filepath}")
        return

    # -----------------------------
    # EMG 데이터 처리 (컬럼 5: 왼쪽, 컬럼 7: 오른쪽)
    # -----------------------------
    emg_left_raw = data.iloc[:, 4].values.flatten()
    emg_right_raw = data.iloc[:, 6].values.flatten()
    emg_left_clean = nk.emg_clean(emg_left_raw, sampling_rate=1000)
    emg_right_clean = nk.emg_clean(emg_right_raw, sampling_rate=1000)

    # 전처리된 EMG 데이터를 DataFrame으로 저장하고 CSV 파일로 내보내기
    emg_signals = {
        "Raw Left": emg_left_raw,
        "Cleaned Left": emg_left_clean,
        "Raw Right": emg_right_raw,
        "Cleaned Right": emg_right_clean
    }
    processed_emg = pd.DataFrame(emg_signals)
    emg_csv_path = os.path.join(os.path.dirname(filepath), f"emg_{base_name}.csv")
    processed_emg.to_csv(emg_csv_path, index=False)

    # 데이터셋의 마지막 컬럼(레이블) 추출 및 구간 설정
    labels = data.iloc[:, -1].values.flatten()
    segments = get_segments(labels)

    # marker 색상 딕셔너리 (레이블 1,2,3,4,5에 대해 각각 다른 색상)
    marker_colors = {1: 'red', 2: 'blue', 3: 'green', 4: 'orange', 5: 'purple'}

    zoom_start, zoom_end = 10000, 10900

    # EMG 플롯 (전체 신호와 Zoomed 신호를 각각 표시)
    fig, axes = plt.subplots(4, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [2.5, 1]})
    emg_data = {
        "Raw Left": (emg_left_raw, 'red'),
        "Cleaned Left": (emg_left_clean, 'blue'),
        "Raw Right": (emg_right_raw, 'green'),
        "Cleaned Right": (emg_right_clean, 'orange')
    }
    for i, (sig_label, (signal, color)) in enumerate(emg_data.items()):
        # 전체 신호 플롯
        axes[i, 0].plot(signal, color=color)
        axes[i, 0].set_title(sig_label)
        axes[i, 0].grid(True)
        # Zoomed 신호 플롯
        axes[i, 1].plot(signal, color=color)
        axes[i, 1].set_xlim(zoom_start, zoom_end)
        zoom_signal = signal[zoom_start:zoom_end]
        y_min, y_max = zoom_signal.min(), zoom_signal.max()
        margin = (y_max - y_min) * 0.1 if (y_max - y_min) != 0 else 1
        axes[i, 1].set_ylim(y_min - margin, y_max + margin)
        axes[i, 1].set_title(f"{sig_label} (Zoomed)")
        axes[i, 1].grid(True)

    # EMG 플롯에 marker 찍기 (전체 신호와 Zoomed 플롯 모두)
    for i in range(4):
        # 전체 신호 플롯 (axes[i, 0])
        y_min, y_max = axes[i, 0].get_ylim()
        y_val = (y_min + y_max) / 2
        for start, end, label_val in segments:
            if label_val in marker_colors:
                x_vals = np.arange(start, end)
                axes[i, 0].scatter(x_vals, np.full_like(x_vals, y_val),
                                   color=marker_colors[label_val], marker='o', s=10, zorder=10)
        # Zoomed 신호 플롯 (axes[i, 1])
        y_min, y_max = axes[i, 1].get_ylim()
        y_val = (y_min + y_max) / 2
        for start, end, label_val in segments:
            if label_val in marker_colors:
                x_vals = np.arange(start, end)
                axes[i, 1].scatter(x_vals, np.full_like(x_vals, y_val),
                                   color=marker_colors[label_val], marker='o', s=10, zorder=10)

    plt.tight_layout()
    emg_png_path = os.path.join(os.path.dirname(filepath), f"emg_{base_name}.png")
    plt.savefig(emg_png_path)

    # -----------------------------
    # ECG 데이터 처리 (컬럼 6)
    # -----------------------------
    ecg_raw = data.iloc[:, 5].values.flatten()
    ecg_clean = nk.ecg_clean(ecg_raw, sampling_rate=250, method="neurokit")

    # 전처리된 ECG 데이터를 DataFrame으로 저장하고 CSV 파일로 내보내기
    ecg_signals = {"ECG Raw": ecg_raw, "ECG Cleaned": ecg_clean}
    processed_ecg = pd.DataFrame(ecg_signals)
    ecg_csv_path = os.path.join(os.path.dirname(filepath), f"ecg_{base_name}.csv")
    processed_ecg.to_csv(ecg_csv_path, index=False)

    # ECG 플롯 (전체 신호와 Zoomed 신호를 각각 표시)
    fig, axes = plt.subplots(2, 2, figsize=(16, 4), gridspec_kw={'width_ratios': [2.5, 1]})
    ecg_data = {
        "ECG Raw": (ecg_raw, 'blue'),
        "ECG Cleaned": (ecg_clean, 'red')
    }
    for i, (sig_label, (signal, color)) in enumerate(ecg_data.items()):
        axes[i, 0].plot(signal, color=color)
        axes[i, 0].set_title(sig_label)
        axes[i, 0].grid(True)
        axes[i, 1].plot(signal, color=color)
        axes[i, 1].set_xlim(zoom_start, zoom_end)
        zoom_signal = signal[zoom_start:zoom_end]
        y_min, y_max = zoom_signal.min(), zoom_signal.max()
        margin = (y_max - y_min) * 0.1 if (y_max - y_min) != 0 else 1
        axes[i, 1].set_ylim(y_min - margin, y_max + margin)
        axes[i, 1].set_title(f"{sig_label} (Zoomed)")
        axes[i, 1].grid(True)

    # ECG 플롯에 marker 찍기 (전체 신호와 Zoomed 플롯 모두)
    for i in range(2):
        # 전체 신호 플롯 (axes[i, 0])
        y_min, y_max = axes[i, 0].get_ylim()
        y_val = (y_min + y_max) / 2
        for start, end, label_val in segments:
            if label_val in marker_colors:
                x_vals = np.arange(start, end)
                axes[i, 0].scatter(x_vals, np.full_like(x_vals, y_val),
                                   color=marker_colors[label_val], marker='o', s=10, zorder=10)
        # Zoomed 신호 플롯 (axes[i, 1])
        y_min, y_max = axes[i, 1].get_ylim()
        y_val = (y_min + y_max) / 2
        for start, end, label_val in segments:
            if label_val in marker_colors:
                x_vals = np.arange(start, end)
                axes[i, 1].scatter(x_vals, np.full_like(x_vals, y_val),
                                   color=marker_colors[label_val], marker='o', s=10, zorder=10)

    plt.tight_layout()
    ecg_png_path = os.path.join(os.path.dirname(filepath), f"ecg_{base_name}.png")
    plt.savefig(ecg_png_path)

# 디렉토리 순회하여 파일 처리 (파일명에 "(1)"이 포함된 경우에만)
for root, dirs, files in os.walk(root_dir):
    print("# root : " + root)
    for file in files:
        if "(1)" not in file:
            continue
        filepath = os.path.join(root, file)
        process_file(filepath)
