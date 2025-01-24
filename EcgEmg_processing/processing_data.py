import os
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 기본 설정
base_dir = r"Z:/EEG/haptic/DSI_가야금/HAPTIC DATA/20250123"
target_suffix = "5 (1)"
filtered_file_paths = []

# 파일 필터링
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.endswith(".csv") and target_suffix in file:
            file_path = os.path.join(root, file)
            filtered_file_paths.append(file_path)

print("필터링된 파일 목록:")

for file_path in filtered_file_paths:
    print(file_path)

# 저장 폴더 생성
output_dir = r"D:\Users\MJL\Desktop\Plots"
os.makedirs(output_dir, exist_ok=True)

# 데이터 처리 및 플롯 저장
for idx, path in enumerate(filtered_file_paths, start=1):  # 순서 추가
    print(f"Processing file {idx}: {path}")
    
    # 데이터 읽기
    data = pd.read_csv(path, encoding='cp949')
    
    # 일부 데이터 추출
    data_part1 = data.loc[10000:10900]
    
    # EMG 데이터 추출
    emg_x1_right = data.iloc[:, 4].values.flatten()
    emg_x2_left = data.iloc[:, 5].values.flatten()
    emg_900_right = data_part1.iloc[:, 4].values.flatten()
    emg_900_left = data_part1.iloc[:, 5].values.flatten()
    
    # 마지막 열에서 0이 아닌 값의 인덱스 추출
    nonzero_indices = data.index[data.iloc[:, -1] != 0].tolist()
    nonzero_indices_part1 = [idx for idx in data_part1.index if idx in nonzero_indices]
    
    # NeuroKit2로 EMG 신호 처리
    emg_signals = pd.DataFrame({
        "emg_right": emg_x1_right,
        "emg_left": emg_x2_left,
        "emg_NeuroKit_right": nk.emg_clean(emg_x1_right, sampling_rate=250),
        "emg_NeuroKit_left": nk.emg_clean(emg_x2_left, sampling_rate=250)
    })
    
    emg_signals_900 = pd.DataFrame({
        "emg_part_900_right": emg_900_right,
        "emg_part_900_left": emg_900_left,
        "emg_NeuroKit_right": nk.emg_clean(emg_900_right, sampling_rate=250),
        "emg_NeuroKit_left": nk.emg_clean(emg_900_left, sampling_rate=250)
    })
    
    # 전체 신호 플롯
    fig, axes = plt.subplots(nrows=len(emg_signals.columns), ncols=1, figsize=(16, 10))
    for i, column in enumerate(emg_signals.columns):
        axes[i].plot(emg_signals[column])
        axes[i].set_title(column)
        # 빨간 점 추가
        if "right" in column or "left" in column:
            valid_indices = [idx for idx in nonzero_indices if idx < len(emg_signals[column])]
            axes[i].scatter(valid_indices, emg_signals[column].iloc[valid_indices], color='red', label='Non-zero points')
            axes[i].legend()
    plt.suptitle(f"Full Signal - {os.path.basename(path)}", fontsize=12)
    full_output_path = os.path.join(output_dir, f"{idx:02d}_full_signal_{os.path.basename(path).replace('.csv', '.png')}")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(full_output_path)
    print(f"Full signal plot saved to {full_output_path}")
    plt.close(fig)
    
    # 특정 구간 신호 플롯
    fig, axes = plt.subplots(nrows=len(emg_signals_900.columns), ncols=1, figsize=(16, 10))
    for i, column in enumerate(emg_signals_900.columns):
        axes[i].plot(emg_signals_900[column])
        axes[i].set_title(column)
        # 빨간 점 추가
        if "right" in column or "left" in column:
            valid_indices_part1 = [idx for idx in nonzero_indices_part1 if idx < len(emg_signals_900[column])]
            axes[i].scatter(valid_indices_part1, emg_signals_900[column].iloc[valid_indices_part1], color='red', label='Non-zero points')
            axes[i].legend()
    plt.suptitle(f"10000~10900 Signal - {os.path.basename(path)}", fontsize=12)
    segment_output_path = os.path.join(output_dir, f"{idx:02d}_segment_signal_{os.path.basename(path).replace('.csv', '.png')}")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(segment_output_path)
    print(f"Segment signal plot saved to {segment_output_path}")
    plt.close(fig)


    # DDD