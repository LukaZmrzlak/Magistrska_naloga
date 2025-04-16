import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import FuncFormatter

# Nastavi velikost pisave za grafe
plt.rcParams.update({'font.size': 21})

def load_s2p(file_path):
    # Branje S-parametrov iz .s2p datoteke
    frequencies = []
    s11_amp = []
    s21_amp = []
    s12_amp = []
    s22_amp = []

    with open(file_path, 'r') as file:
        data_started = False
        for line in file:
            line = line.strip()
            if line.startswith("# GHZ S DB R 50"):
                data_started = True
                continue
            if data_started and line:
                columns = line.split()
                frequencies.append(float(columns[0]))
                s11_amp.append(float(columns[1]))
                s21_amp.append(float(columns[3]))
                s12_amp.append(float(columns[5]))
                s22_amp.append(float(columns[7]))

    return (
        np.array(frequencies),
        np.array(s11_amp),
        np.array(s21_amp),
        np.array(s12_amp),
        np.array(s22_amp),
    )

def comma_formatter(x, pos):
    return f"{x:.1f}".replace(".", ",")

def plot_multiple_s2p(data_list, save_path):
    # Izris grafa S-parametrov
    plt.figure(figsize=(12, 8))

    for frequencies, s11, s21, s12, s22, base_name in data_list:
        plt.plot(frequencies, s11, label="S11")
        plt.plot(frequencies, s21, label="S21")
        plt.plot(frequencies, s12, label="S12")
        plt.plot(frequencies, s22, label="S22")

    plt.xlabel('Frekvenca [GHz]')
    plt.ylabel('Amplituda [dB]')
    plt.title(f'{base_name}')
    plt.legend()
    plt.minorticks_on()
    plt.grid(visible=True, which='major')
    plt.grid(visible=True, which='minor', linestyle=':', linewidth=0.5)
    plt.tight_layout()
    plt.xlim(8, 12)
    plt.ylim(-40, 1)
    plt.gca().xaxis.set_major_formatter(FuncFormatter(comma_formatter))
    plt.savefig(save_path)
    plt.show()

def main():
    # Poišči trenutno mapo in naloži .s2p datoteke
    script_dir = os.path.dirname(os.path.abspath(__file__))
    s2p_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.s2p')]
    if not s2p_files:
        print("V mapi ni .s2p datotek.")
        return

    print("Dostopne .s2p datoteke:")
    for i, file_name in enumerate(s2p_files, start=1):
        print(f"{i}: {file_name}")

    selected_indices = []
    while True:
        try:
            selection = input("Vnesi številke datotek za prikaz, ločene z vejicami (npr. 1,3,5): ")
            selected_indices = [
                int(idx.strip()) - 1 for idx in selection.split(",") if idx.strip().isdigit()
            ]
            if all(0 <= idx < len(s2p_files) for idx in selected_indices):
                break
            else:
                print("Ena ali več izbranih številk ni v dosegu. Poskusi znova.")
        except ValueError:
            print("Neveljaven vnos. Vnesi številke, ločene z vejicami.")

    data_list = []
    for idx in selected_indices:
        file_path = os.path.join(script_dir, s2p_files[idx])
        frequencies, s11, s21, s12, s22 = load_s2p(file_path)
        base_name, _ = os.path.splitext(s2p_files[idx])
        data_list.append((frequencies, s11, s21, s12, s22, base_name))

    base_names = "_".join([os.path.splitext(s2p_files[idx])[0] for idx in selected_indices])
    save_path = os.path.join(script_dir, f"{base_names}_s_parameter_graf.svg")
    plot_multiple_s2p(data_list, save_path)

if __name__ == "__main__":
    main()