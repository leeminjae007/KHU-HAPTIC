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
    """연속된 레이블의 시작과 끝 인덱스를 반환"""
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
    """EMG 및 ECG 데이터를 처리하고 시각화하여 저장"""
    
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
    # EMG 데이터 처리 (왼쪽: 5번째 컬럼, 오른쪽: 7번째 컬럼)
    # -----------------------------
    emg_left_raw = data.iloc[:, 4].values.flatten()
    emg_right_raw = data.iloc[:, 6].values.flatten()
    
    emg_left_clean = nk.emg_clean(emg_left_raw, sampling_rate=1000)
    emg_right_clean = nk.emg_clean(emg_right_raw, sampling_rate=1000)

    # 전처리된 EMG 데이터를 CSV로 저장
    emg_signals = {
        "Raw Left": emg_left_raw,
        "Cleaned Left": emg_left_clean,
        "Raw Right": emg_right_raw,
        "Cleaned Right": emg_right_clean
    }
    processed_emg = pd.DataFrame(emg_signals)
    emg_csv_path = os.path.join(os.path.dirname(filepath), f"emg_{base_name}.csv")
    processed_emg.to_csv(emg_csv_path, index=False)

    # 레이블 데이터 (마지막 컬럼) 추출
    labels = data.iloc[:, -1].values.flatten()
    segments = get_segments(labels)

    # 레이블에 따른 색상 지정
    marker_colors = {1: 'red', 2: 'blue', 3: 'green', 4: 'orange', 5: 'magenta'}

    zoom_start, zoom_end = 10000, 10900  # 줌 인 범위

    # EMG 시각화
    fig, axes = plt.subplots(4, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [2.5, 1]})
    
    emg_data = {
        "Raw Left": (emg_left_raw, 'black'),
        "Cleaned Left": (emg_left_clean, 'black'),
        "Raw Right": (emg_right_raw, 'black'),
        "Cleaned Right": (emg_right_clean, 'black')
    }
    
    for i, (sig_label, (signal, color)) in enumerate(emg_data.items()):
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

    # EMG 플롯에 마커 추가
    for i in range(4):
        y_val = np.mean(axes[i, 0].get_ylim())
        for start, end, label_val in segments:
            if label_val in marker_colors:
                axes[i, 0].scatter(np.arange(start, end), np.full(end-start, y_val),
                                   color=marker_colors[label_val], marker='o', s=30, zorder=10)

    plt.tight_layout()
    emg_png_path = os.path.join(os.path.dirname(filepath), f"emg_{base_name}.png")
    plt.savefig(emg_png_path)
    plt.close(fig)  # ✅ 개별 그래프 닫기

    # -----------------------------
    # ECG 데이터 처리 (6번째 컬럼)
    # -----------------------------
    ecg_raw = data.iloc[:, 5].values.flatten()
    ecg_clean = nk.ecg_clean(ecg_raw, sampling_rate=250, method="neurokit")

    # 전처리된 ECG 데이터를 CSV로 저장
    ecg_signals = {"ECG Raw": ecg_raw, "ECG Cleaned": ecg_clean}
    processed_ecg = pd.DataFrame(ecg_signals)
    ecg_csv_path = os.path.join(os.path.dirname(filepath), f"ecg_{base_name}.csv")
    processed_ecg.to_csv(ecg_csv_path, index=False)

    # ECG 시각화
    fig, axes = plt.subplots(2, 2, figsize=(16, 4), gridspec_kw={'width_ratios': [2.5, 1]})
    
    ecg_data = {
        "ECG Raw": (ecg_raw, 'black'),
        "ECG Cleaned": (ecg_clean, 'black')
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

    plt.tight_layout()
    ecg_png_path = os.path.join(os.path.dirname(filepath), f"ecg_{base_name}.png")
    plt.savefig(ecg_png_path)
    plt.close(fig)  # ✅ 개별 그래프 닫기


# 디렉토리 내 파일 처리
for root, dirs, files in os.walk(root_dir):
    print(f"# root : {root}")
    for file in files:
        if "(1)" not in file:
            continue
        filepath = os.path.join(root, file)
        process_file(filepath)
