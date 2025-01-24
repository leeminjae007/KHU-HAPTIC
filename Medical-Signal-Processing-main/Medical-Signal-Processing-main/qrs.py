import scipy.io
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks
import os
#04 part2
#obtener la ruta actual
current_dir = os.getcwd()
#especificar ruta 
folder_path = os.path.join(current_dir, 'physiozoo-mammalian-nsr-databases-1.0.0', 'matlab_format', 'rabbit')

# Especificar la ruta completa al archivo
filename = os.path.join(folder_path, 'Rabbit_04_part_2', 'elctrography_Rabbit_04_part_2.mat')
filename_base = os.path.basename(filename)

# Cargar los datos
mat_data = scipy.io.loadmat(filename)
signal = mat_data['Data'][:, 0]
fs = mat_data['Fs'][0, 0]


# Preprocesamiento de la señal
def bandpass_filter(signal, fs, lowcut, highcut):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(1, [low, high], 'bandpass')
    return filtfilt(b, a, signal)

filtered_signal = bandpass_filter(signal, fs, 5.0, 30.0)

# Detección de los picos R
def detect_r_peaks(signal, fs):
    peaks, _ = find_peaks(signal, distance=0.2 * fs, height=0.01)
    return peaks

peaks = detect_r_peaks(filtered_signal, fs)

# Cálculo de los intervalos RR
rr_intervals = np.diff(peaks)
mean_rr = np.mean(rr_intervals)

# Marcado de los segmentos QRS
qrs_start = []
qrs_end = []


def mark_qrs_segments(signal, peaks, mean_rr):
    # Agregar el primer complejo QRS
    first_q_peak = np.argmin(signal[:peaks[0]])  # Encontrar el pico Q en la señal antes del primer complejo R
    s_peak = np.argmax(signal[first_q_peak:peaks[0]]) + first_q_peak  # Encontrar el pico S en la señal entre el pico Q y el primer complejo R
    qrs_start_i = first_q_peak - int(0.35 * mean_rr)
    qrs_end_i = s_peak + int(0.3 * mean_rr)
    qrs_start.append(qrs_start_i)
    qrs_end.append(qrs_end_i)
    for i in range(len(peaks) - 1):
        r_peak = peaks[i]
        next_r_peak = peaks[i+1]
        q_peak = np.argmin(signal[r_peak:next_r_peak]) + r_peak
        s_peak = np.argmax(signal[q_peak:next_r_peak]) + q_peak
        
        # Marcado del segmento QRS
        qrs_start_i = q_peak - int(0.35 * mean_rr)
        qrs_end_i = s_peak + int(0.3 * mean_rr)
        qrs_start.append(qrs_start_i)
        qrs_end.append(qrs_end_i)
        
    return qrs_start, qrs_end

qrs_start, qrs_end = mark_qrs_segments(filtered_signal, peaks, mean_rr)

# Almacenamiento de los intervalos QRS en un archivo
filename_qrs = 'qrs/' + 'qrs_' + filename_base[:-4] + '.txt'
with open(filename_qrs, 'w') as f:
    for i in range(len(qrs_start)):
        f.write('{} {}\n'.format(qrs_start[i], qrs_end[i]))

# Visualización de los segmentos QRS marcados
def plot_qrs_segments(signal, qrs_start, qrs_end, fs):
    fig, ax = plt.subplots(figsize=(18.5,10.5))
    ax.plot(signal)
    
    # Colores para el segmento QRS
    color = 'red'
    label = 'QRS'
    
    label_added = False
    for i in range(len(qrs_start)):
        if qrs_start[i] > 0 and qrs_end[i] < len(signal):
            ax.axvspan(qrs_start[i], qrs_end[i], alpha=0.2, color=color)
            if not label_added:
                ax.plot([], label=label, color=color)
                label_added = True
                
    ax.set_title('Marcado del segmento QRS en la señal')
    ax.set_xlabel('Muestras')
    ax.set_ylabel('Amplitud')
    ax.set_xlim([0, 2*fs])
    ax.legend(loc='upper right')
    plt.show()

plot_qrs_segments(filtered_signal, qrs_start, qrs_end, fs)
