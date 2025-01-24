from scipy.signal import butter, filtfilt, find_peaks
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy

# Obtener la ruta actual
current_dir = os.getcwd()

# Especificar la ruta de la carpeta de datos
folder_path = os.path.join(current_dir, 'physiozoo-mammalian-nsr-databases-1.0.0', 'matlab_format', 'rabbit')

# Especificar la ruta completa al archivo
filename = os.path.join(folder_path, 'Rabbit_04_part_2', 'elctrography_Rabbit_04_part_2.mat')


# Cargar los datos
mat_data = scipy.io.loadmat(filename)
signal = mat_data['Data'][:, 0]
fs = mat_data['Fs'][0, 0]


# Filtro paso banda
def bandpass_filter(signal, fs, lowcut, highcut):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(1, [low, high], 'bandpass')
    return filtfilt(b, a, signal)


# Derivada
def derivative(signal):
    diff = np.diff(signal)
    return np.concatenate(([diff[0]], diff))


# Cuadrado
def square(signal):
    return signal**2


# Media móvil
def moving_average(signal, window_size):
    return np.convolve(signal, np.ones(window_size)/window_size, mode='same')


# Filtrado de la señal
filtered_signal = bandpass_filter(signal, fs, 5.0, 30.0)

# Aplicación del algoritmo de Pan-Tompkins
def pan_tompkins(signal, fs):
    # Filtro paso bajo
    lowcut = 5.0 / (fs / 2)
    highcut = 30 / (fs / 2)
    b, a = butter(1, [lowcut, highcut], 'bandpass')
    filtered_signal = filtfilt(b, a, signal)

    # Derivada
    d_signal = derivative(filtered_signal)

    # Cuadrado
    squared_signal = square(d_signal)

    # Media móvil
    window_size = int(0.5 * fs)
    ma_signal = moving_average(squared_signal, window_size)

    # Normalización
    ma_signal = (ma_signal - np.mean(ma_signal)) / np.std(ma_signal)

    # Detección de los picos R
    threshold = 0.01
    peaks, _ = find_peaks(ma_signal, distance=0.2 * fs, height=threshold)
    return peaks

peaks = pan_tompkins(filtered_signal, fs)

# Cálculo de los intervalos RR
rr_intervals = np.diff(peaks)
mean_rr = np.mean(rr_intervals)


# Marcado de los segmentos QRS
qrs_start = []
qrs_end = []

# Marcado de los segmentos QRS
def mark_qrs_segments(signal, peaks, mean_rr, fs):
    qrs_start = []
    qrs_end = []
    # Agregar el primer complejo QRS
    first_q_peak = np.argmin(signal[:peaks[0]])  # Encontrar el pico Q en la señal antes del primer complejo R
    s_peak = np.argmax(signal[first_q_peak:peaks[0]]) + first_q_peak  # Encontrar el pico S en la señal entre el pico Q y el primer complejo R
    qrs_start_i = first_q_peak - int(0.35 * mean_rr)
    qrs_end_i = s_peak + int(0.3 * mean_rr)
    qrs_start.append(qrs_start_i)
    qrs_end.append(qrs_end_i)
    # Agregar una línea vertical en el gráfico para marcar el inicio y el fin del primer segmento QRS
    plt.axvline(x=qrs_start_i, color='g', linewidth=2)
    plt.axvline(x=qrs_end_i, color='g', linewidth=2)
    for i in range(len(peaks) - 1):
        r_peak = peaks[i]
        next_r_peak = peaks[i+1]
        q_peak = np.argmin(signal[r_peak:next_r_peak]) + r_peak
        s_peak = np.argmax(signal[q_peak:next_r_peak]) + q_peak
        qrs_start_i = q_peak - int(0.35 * mean_rr)
        qrs_end_i = s_peak + int(0.3 * mean_rr)
        qrs_start.append(qrs_start_i)
        qrs_end.append(qrs_end_i)
        # Agregar una línea vertical en el gráfico para marcar el inicio y el fin de cada segmento
        plt.axvline(x=qrs_start_i, color='g', linewidth=2)
        plt.axvline(x=qrs_end_i, color='g', linewidth=2)
        
    plt.plot(signal, 'k', linewidth=1)
    plt.plot(peaks, signal[peaks], 'r.', markersize=10)
    plt.title('QRS segments')
    plt.xlim([peaks[0]-fs, peaks[-1]+fs])
    plt.xlabel('Time (s)')
    
    # Aumentar el tamaño de la figura
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    plt.xlim([0, 2*fs])
    plt.show()
    filename_base = os.path.basename(filename)
    # Almacenamiento de los intervalos QRS en un archivo
    filename_qrs = 'qrs_pan/' + 'qrs_pan_' + filename_base[:-4] + '.txt'
    with open(filename_qrs, 'w') as f:
        for i in range(len(qrs_start)):
            f.write('{} {}\n'.format(qrs_start[i], qrs_end[i]))



mark_qrs_segments(filtered_signal, peaks, mean_rr, fs)

