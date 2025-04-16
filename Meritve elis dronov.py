import serial
import time
import pyvisa
import numpy as np
import csv
import os
import matplotlib.pyplot as plt

# Ciljna mapa za shranjevanje rezultatov
TARGET_DIRECTORY = r"C:\Users\zmrzl\OneDrive - Univerza v Ljubljani\Magisterij\Meritve propelerjev 2"

def perform_measurement(file_name, vrt, oscilloscope):
    # Pridobivanje nastavitev FFT iz osciloskopa
    freq_start = float(oscilloscope.query(':MATH1:FFT:FREQ:STAR?'))
    freq_end = float(oscilloscope.query(':MATH1:FFT:FREQ:END?'))
    frequencies = np.linspace(freq_start, freq_end, 1000)
    vert_scale = float(oscilloscope.query(':MATH1:FFT:SCAL?'))
    vert_offset = float(oscilloscope.query(':MATH1:FFT:OFFS?'))
    time_scale = float(oscilloscope.query(':TIM:MAIN:SCAL?'))

    def capture_fft():
        oscilloscope.write(':WAV:SOUR MATH1')
        oscilloscope.write(':WAV:MODE NORM')
        oscilloscope.write(':WAV:FORM BYTE')
        data = oscilloscope.query_binary_values(':WAV:DATA?', datatype='B')
        return np.array(data)

    def parse_angle(line):
        try:
            return int(float(line[0:5]) * 10.0 + 0.5)
        except (ValueError, IndexError):
            return None

    angles = []
    vpp_values = []
    fft_data = []

    time.sleep(1)  # Kratka pavza za inicializacijo
    vrt.write(str.encode('5D'))  # Zagon vrtenja

    try:
        current_angle = 0
        true_angle = 0

        while current_angle < 3600:
            line = vrt.readline().decode('ascii', errors='ignore').strip()
            angle = parse_angle(line)
            if angle is not None:
                current_angle = angle
                new_true_angle = current_angle // 10

                if new_true_angle != true_angle:
                    true_angle = new_true_angle
                    Vpp = oscilloscope.query(':MEAS:ITEM? VPP')
                    fft = capture_fft()
                    angles.append(true_angle)
                    vpp_values.append(float(Vpp.strip()))
                    fft_data.append(fft)

        vrt.write(str.encode('S'))   # Ustavitev vrtenja
        vrt.write(str.encode('9L'))  # Resetiranje
        time.sleep(7)

    finally:
        vrt.close()

    if not os.path.exists(TARGET_DIRECTORY):
        os.makedirs(TARGET_DIRECTORY)

    # Shranjevanje kotov in Vpp v CSV
    full_file_path = os.path.join(TARGET_DIRECTORY, f"{os.path.splitext(file_name)[0]}.csv")
    with open(full_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Kot (\u00b0)', 'Vpp [V]'])
        for angle, vpp in zip(angles, vpp_values):
            writer.writerow([angle, vpp])

    # Shranjevanje FFT podatkov v CSV
    fft_file_name = f"{os.path.splitext(file_name)[0]}_FFT.csv"
    fft_full_file_path = os.path.join(TARGET_DIRECTORY, fft_file_name)
    fft_data_array = np.array(fft_data)

    with open(fft_full_file_path, mode='w', newline='') as fft_file:
        writer = csv.writer(fft_file)
        writer.writerow(["Zacetna frekvenca [Hz]:", "Končna frekvenca [Hz]:", "Število točk:", "Vertikalna skala:", "Vertikalni zamik:", "Časovna skala:"])
        writer.writerow([freq_start, freq_end, len(frequencies), vert_scale, vert_offset, time_scale])
        writer.writerow(['Kot (°)', 'FFT vrednosti'])
        for angle, fft_values in zip(angles, fft_data_array):
            writer.writerow([angle] + fft_values.tolist())

    # Prikaz waterfall grafa
    plt.figure(figsize=(10, 8))
    plt.imshow(
        fft_data_array,
        aspect='auto',
        cmap='jet',
        origin='upper',
        extent=[freq_start, freq_end, 360, 0]
    )
    plt.colorbar(label='Amplituda')
    plt.xlabel('Frekvenca [Hz]')
    plt.ylabel('Kot [°]')
    plt.title('Waterfall graf FFT meritev')
    plt.show()

def main():
    vrt = serial.Serial('COM3', 115200, timeout=1.0)
    vrt.setRTS(False)
    vrt.setDTR(False)

    rm = pyvisa.ResourceManager()
    try:
        oscilloscope = rm.open_resource('TCPIP0::169.254.112.67::INSTR')
        idn = oscilloscope.query('*IDN?')
        print(f"Povezava vzpostavljena. Naprava: {idn}")
    except pyvisa.VisaIOError as e:
        print(f"Napaka pri povezavi: {e}")
        return

    try:
        while True:
            file_name = input("Ime nove meritve: ")
            print("Zacetek meritve...")
            perform_measurement(file_name, vrt, oscilloscope)
            repeat = input("Nova meritev? (y/n): ").strip().lower()
            if repeat != 'y':
                break
    finally:
        vrt.close()
        oscilloscope.close()

if __name__ == "__main__":
    main()
