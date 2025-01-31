import os
import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 기본 경로
root_dir = r"Z:\\EEG\\haptic\\DSI_가야금\\HAPTIC DATA"

def processing(path, name):
    data_path = os.path.join(path, name)
    dir_split = path.split("\\")
    
    if len(dir_split) < 2 or len(name) < 11:
        print(f"Skipping {name}: insufficient directory depth or filename length.")
        return
    
    base_name = dir_split[-2][2:] + "_" + dir_split[-1] + "_" + name[10]
    
    try:
        data = pd.read_csv(data_path)
    except Exception as e:
        print(f"Error reading file {data_path}: {e}")
        return
    
    if data.shape[1] < 7:
        print(f"Skipping {name}: insufficient columns in data.")
        return
    
    if "(1)" in data_path:
        emg_name = "emg_" + base_name
        try:
            emg_signals = {
                "Raw Left": data.iloc[:, 4].values.flatten(),
                "Cleaned Left": nk.emg_clean(data.iloc[:, 4].values.flatten(), sampling_rate=1000),
                "Raw Right": data.iloc[:, 6].values.flatten(),
                "Cleaned Right": nk.emg_clean(data.iloc[:, 6].values.flatten(), sampling_rate=1000)
            }
            processed_data = pd.DataFrame(emg_signals)
            processed_data.to_csv(os.path.join(path, f"{emg_name}.csv"), index=False)
        except Exception as e:
            print(f"Error processing EMG data in {name}: {e}")
            return
        
        zoom_start, zoom_end = 10000, 10900
        colors = {"Raw Left": 'blue', "Cleaned Left": 'red', "Raw Right": 'green', "Cleaned Right": 'orange'}
        
        fig, axes = plt.subplots(nrows=8, ncols=1, figsize=(16, 12), sharex=False)
        
        for i, (key, signal) in enumerate(emg_signals.items()):
            axes[i].plot(signal, label=key, color=colors[key])
            axes[i].set_title(key)
            axes[i].legend()
            axes[i].grid()
            axes[i + 4].plot(signal, label=f"Zoomed {key}", color=colors[key])
            axes[i + 4].set_title(f"Zoomed {key}")
            axes[i + 4].legend()
            axes[i + 4].grid()
            axes[i + 4].set_xlim(zoom_start, zoom_end)
        
        plt.xlabel("Time (samples)")
        plt.tight_layout()
        plt.savefig(os.path.join(path, f"{emg_name}.png"))
    
    else:
        ecg_name = "ecg_" + base_name
        try:
            ecg = data.iloc[:, 5].values.flatten()
            ecg_clean = nk.ecg_clean(ecg, sampling_rate=250, method="neurokit")
            ecg_signals = {"ECG Raw": ecg, "ECG_NeuroKit": ecg_clean}
            processed_ecg = pd.DataFrame(ecg_signals)
            processed_ecg.to_csv(os.path.join(path, f"{ecg_name}.csv"), index=False)
        except Exception as e:
            print(f"Error processing ECG data in {name}: {e}")
            return
        
        fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(16, 6), sharex=False)
        colors = {"ECG Raw": 'blue', "ECG_NeuroKit": 'red'}
        
        for i, (key, signal) in enumerate(ecg_signals.items()):
            axes[i].plot(signal, label=key, color=colors[key])
            axes[i].set_title(key)
            axes[i].legend()
            axes[i].grid()
            axes[i + 2].plot(signal, label=f"Zoomed {key}", color=colors[key])
            axes[i + 2].set_title(f"Zoomed {key}")
            axes[i + 2].legend()
            axes[i + 2].grid()
            axes[i + 2].set_xlim(10000, 10900)
        
        plt.xlabel("Time (samples)")
        plt.tight_layout()
        plt.savefig(os.path.join(path, f"{ecg_name}.png"))


for (root, dirs, files) in os.walk(root_dir):
    print("# root : " + root)
    for file_name in files:
        processing(root, file_name)





# "ECG_BioSPPy": nk.ecg_clean(ecg, sampling_rate=250, method="biosppy"),
# "ECG_PanTompkins": nk.ecg_clean(ecg, sampling_rate=250, method="pantompkins1985"),
# "ECG_Hamilton": nk.ecg_clean(ecg, sampling_rate=250, method="hamilton2002"),
# "ECG_Elgendi": nk.ecg_clean(ecg, sampling_rate=250, method="elgendi2010"),
# "ECG_EngZeeMod": nk.ecg_clean(ecg, sampling_rate=250, method="engzeemod2012"),
# "ECG_VG": nk.ecg_clean(ecg, sampling_rate=250, method="vg"),
# "ECG_TC": nk.ecg_clean(ecg, sampling_rate=250, method="templateconvolution")
