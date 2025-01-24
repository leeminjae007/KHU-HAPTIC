import scipy.io
from scipy.signal import butter, filtfilt, find_peaks

# Cargar los datos
mat_data = scipy.io.loadmat('elctrography_Dog_01.mat') #Firulais
#mat_data = scipy.io.loadmat('elctrography_Rabbit_04_part_1.mat') #bugs bunny
#mat_data = scipy.io.loadmat('elctrography_Mouse_06.mat') #jerry
signal = mat_data['Data'][:, 0]
fs = mat_data['Fs'][0, 0]
print(fs)

# Preprocesamiento de la señal
lowcut = 5.0
highcut = 15.0
nyquist = 0.5 * fs
low = lowcut / nyquist
high = highcut / nyquist
b, a = butter(1, [low, high], 'bandpass')
filtered_signal = filtfilt(b, a, signal)

# Detección de los picos R
peaks, _ = find_peaks(filtered_signal, distance=0.2*fs, height=0.01)

# Cálculo de la frecuencia cardíaca
rr_intervals = peaks[1:] - peaks[:-1]
if rr_intervals.size > 0:
    heart_rate = fs * 60 / rr_intervals.mean()
    print("Frecuencia cardíaca: %.2f bpm" % heart_rate)
else:
    print("No se encontraron picos R en la señal.")
