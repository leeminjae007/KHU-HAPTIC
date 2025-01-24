import pandas as pd
import neurokit2 as nk
import matplotlib.pyplot as plt

path = r"D:\mildseven\EcgEmg_processing\2_2_test_all.csv"

data = pd.read_csv(path)
data_part1 = data.loc[40000:41000]
data_part2 = data.loc[40000:43000]

print(data.shape)
print(data.columns)


ecg = data.iloc[:, 5].values.flatten()
ecg_1000 = data_part1.iloc[:,5].values.flatten()
ecg_3000 = data_part2.iloc[:,5].values.flatten()

ecg_signals = pd.DataFrame({
    "ECG_Raw": ecg,
    # "ECG_NeuroKit": nk.ecg_clean(ecg, sampling_rate=250, method="neurokit"),
    # "ECG_BioSPPy": nk.ecg_clean(ecg, sampling_rate=250, method="biosppy"),
    # "ECG_PanTompkins": nk.ecg_clean(ecg, sampling_rate=250, method="pantompkins1985"),
    # "ECG_Hamilton": nk.ecg_clean(ecg, sampling_rate=250, method="hamilton2002"),
    # "ECG_Elgendi": nk.ecg_clean(ecg, sampling_rate=250, method="elgendi2010"),
    # "ECG_EngZeeMod": nk.ecg_clean(ecg, sampling_rate=250, method="engzeemod2012"),
    # "ECG_VG": nk.ecg_clean(ecg, sampling_rate=250, method="vg"),
    # "ECG_TC": nk.ecg_clean(ecg, sampling_rate=250, method="templateconvolution")
})

ecg_signals_1000 = pd.DataFrame({"ECG_part_1000": ecg_1000})
ecg_signals_3000 = pd.DataFrame({"ECG_part_3000": ecg_3000})

emg = data.iloc[:, 4].values.flatten()
emg_1000 = data_part1.iloc[:,4].values.flatten()
emg_3000 = data_part2.iloc[:,4].values.flatten()
emg_signals_1000 = pd.DataFrame({"EMG_part_1000": emg_1000})
emg_signals_3000 = pd.DataFrame({"EMG_part_3000": emg_3000})

emg_signals = pd.DataFrame({"EMG_Raw": emg})
# , "EMG_Cleaned":nk.emg_clean(emg, sampling_rate=1000)

# ecg_signals.plot(subplots=True, figsize=(16,2.5))
# ecg_signals_1000.plot(subplots=True, figsize=(16,2.5))
# ecg_signals_3000.plot(subplots=True, figsize=(16,2.5))
emg_signals.plot(subplots=True, figsize=(16,2.5))
emg_signals_1000.plot(subplots=True, figsize=(16,2.5))
emg_signals_3000.plot(subplots=True, figsize=(16,2.5))
plt.show()