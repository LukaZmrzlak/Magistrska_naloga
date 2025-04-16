import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import time

# Nastavi velikost pisave na grafih
plt.rcParams.update({'font.size': 21})

def load_fft_data(file_path):
    # Branje FFT podatkov iz CSV datoteke
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    freq_start, freq_end, num_points = map(float, rows[1][:3])

    angles = []
    fft_data = []

    for row in rows[3:]:
        angles.append(float(row[0]))
        fft_amplitudes = list(map(float, row[1:]))
        fft_data.append(fft_amplitudes)

    return freq_start, freq_end, np.array(angles), np.array(fft_data)

def plot_waterfall(freq_start, freq_end, angles, fft_data, save_path, base_name):
    # Izris waterfall grafa FFT podatkov
    plt.figure(figsize=(10, 8))
    plt.imshow(
        fft_data,
        aspect='auto',
        cmap='inferno',
        origin='upper',
        extent=[freq_start, freq_end, 360, 0],
        vmin=0,
        vmax=250
    )
    plt.colorbar(label='Amplituda')
    plt.xlabel('Frekvenca [Hz]')
    plt.ylabel('Kot [°]')
    plt.title(f'{base_name}')
    plt.savefig(save_path, bbox_inches='tight')
    plt.show(block=False)
    plt.close()
    print(f"Waterfall graf shranjen: {save_path}")

def main():
    # Poišči trenutno mapo in seznam CSV datotek
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.csv')]
    if not csv_files:
        print("V mapi ni CSV datotek.")
        return

    print("Dostopne CSV datoteke:")
    for i, file_name in enumerate(csv_files, start=1):
        print(f"{i}: {file_name}")

    while True:
        try:
            file_input = input("Vnesi številke datotek za prikaz, ločene z vejicami, ali 'all' za vse: ").strip().lower()
            if file_input == "all":
                selected_files = csv_files
                break
            else:
                file_indices = [int(index.strip()) - 1 for index in file_input.split(',')]
                if all(0 <= index < len(csv_files) for index in file_indices):
                    selected_files = [csv_files[index] for index in file_indices]
                    break
                else:
                    print("Napačna izbira. Poskusi znova.")
        except ValueError:
            print("Napaka vnosa. Uporabi številke, ločene z vejicami, ali 'all'.")

    for selected_file in selected_files:
        file_path = os.path.join(script_dir, selected_file)
        freq_start, freq_end, angles, fft_data = load_fft_data(file_path)
        base_name, _ = os.path.splitext(selected_file)
        title_name = base_name.replace("_FFT", "").strip()
        save_path = os.path.join(script_dir, f"{base_name}_waterfall_graf.svg")
        plot_waterfall(freq_start, freq_end, angles, fft_data, save_path, title_name)

if __name__ == "__main__":
    main()
