import os
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

#기본 경로
root_dir = r"Z:\EEG\haptic\DSI_가야금\HAPTIC DATA"

def procssing(path, name):
    data_path = os.path.join(path, name)
    dir_split = path.split("\\")
    if "(1)" in data_path:
        data = pd.read_csv(data_path)
        emg_left = data.iloc[:, 4].values.flatten()
        emg_right = data.iloc[:, 6].values.flatten()
        # EMG 신호 필터링
        clean_left = nk.emg_clean(emg_left, sampling_rate=1000)
        clean_right = nk.emg_clean(emg_right, sampling_rate=1000)
        # 확대할 구간 설정 (10000 ~ 10900)
        zoom_start, zoom_end = 10000, 10900

        # 8개의 그래프를 위에서 아래로 정렬
        fig, axes = plt.subplots(nrows=8, ncols=1, figsize=(16, 12), sharex=False)

        # Raw Left
        axes[0].plot(emg_left, label="Raw Left", color='blue')
        axes[0].set_title("Raw EMG Left")
        axes[0].legend()
        axes[0].grid()

        # Clean Left
        axes[1].plot(clean_left, label="Cleaned Left", color='red')
        axes[1].set_title("Cleaned EMG Left")
        axes[1].legend()
        axes[1].grid()

        # Raw Left (확대)
        axes[2].plot(emg_left, label="Zoomed Raw Left", color='blue')
        axes[2].set_title("Zoomed Cleaned EMG Left")
        axes[2].legend()
        axes[2].grid()
        axes[2].set_xlim(zoom_start, zoom_end)

        # Clean Left (확대)
        axes[3].plot(clean_left, label="Zoomed Cleaned Left", color='red')
        axes[3].set_title("Zoomed Raw EMG Left")
        axes[3].legend()
        axes[3].grid()
        axes[3].set_xlim(zoom_start, zoom_end)

        # Raw Right
        axes[4].plot(emg_right, label="Raw Right", color='green')
        axes[4].set_title("Raw EMG Right")
        axes[4].legend()
        axes[4].grid()

        # Clean Right
        axes[5].plot(clean_right, label="Cleaned Right", color='orange')
        axes[5].set_title("Cleaned EMG Right")
        axes[5].legend()
        axes[5].grid()

        # Raw Right (확대)
        axes[6].plot(clean_right, label="Zoomed Raw Right", color='green')
        axes[6].set_title("Zoomed Raw EMG Right")
        axes[6].legend()
        axes[6].grid()
        axes[6].set_xlim(zoom_start, zoom_end)

        # Clean Right (확대)
        axes[7].plot(clean_right, label="Zoomed Cleaned Right", color='orange')
        axes[7].set_title("Zoomed Cleaned EMG Right")
        axes[7].legend()
        axes[7].grid()
        axes[7].set_xlim(zoom_start, zoom_end)

        # X축 레이블 추가
        plt.xlabel("Time (samples)")

        # 레이아웃 자동 조정
        plt.tight_layout()
        plt.show()
        # emg_name = dir_split[-2]+"_"+dir_split[-1][0:2] + "_" + name[10] + "emg"
        # emg.to_csv(os.path.join(data_path, emg_name), index = False)
    # else:
    #     data = pd.read_csv(data_path)
    #     ecg = data.iloc[:, 5].values.flatten()
    #     ecg_signals = pd.DataFrame({
    #         "ECG_Raw": ecg,
    #         # "ECG_NeuroKit": nk.ecg_clean(ecg, sampling_rate=250, method="neurokit"),
    #         # "ECG_BioSPPy": nk.ecg_clean(ecg, sampling_rate=250, method="biosppy"),
    #         # "ECG_PanTompkins": nk.ecg_clean(ecg, sampling_rate=250, method="pantompkins1985"),
    #         # "ECG_Hamilton": nk.ecg_clean(ecg, sampling_rate=250, method="hamilton2002"),
    #         # "ECG_Elgendi": nk.ecg_clean(ecg, sampling_rate=250, method="elgendi2010"),
    #         # "ECG_EngZeeMod": nk.ecg_clean(ecg, sampling_rate=250, method="engzeemod2012"),
    #         # "ECG_VG": nk.ecg_clean(ecg, sampling_rate=250, method="vg"),
    #         # "ECG_TC": nk.ecg_clean(ecg, sampling_rate=250, method="templateconvolution")
    #     })
    #     ecg_signals.plot(subplots=True, figsize=(16,2.5))
    #     ecg_signals.plot(subplots=True, figsize=(16,2.5), xlim = (10000,10900))
    #     ecg_name = data_path
    #     ecg.to_csv(os.path.join(data_path, ecg_name), index = False)


for (root, dirs, files) in os.walk(root_dir):
    print("# root : " + root)
    for file_name in files:
        procssing(root,file_name)
            