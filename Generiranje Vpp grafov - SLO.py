import numpy as np
import matplotlib.pyplot as plt
import csv
import os

# Nastavi velikost pisave za grafe
plt.rcParams.update({'font.size': 21})

def load_data(file_path):
    # Branje CSV datoteke in razdelitev na kote in Vpp vrednosti
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    Vpp = []
    angle = []

    for row in rows[1:]:
        angle.append(float(row[0]))
        Vpp.append(float(row[1]))

    return np.array(Vpp), np.array(angle)

def plot_multiple_Vpp(data_list, save_path):
    # Izris primerjalnega grafa za izbrane datoteke
    plt.figure(figsize=(10, 8))

    for angle, Vpp, base_name in data_list:
        plt.plot(angle, Vpp, label=base_name)

    plt.xlabel('Kot [°]')
    plt.ylabel('Vpp [V]')
    plt.ylim(0, 25)
    plt.xlim(0, 360)
    plt.minorticks_on()
    plt.grid(visible=True, which='major')
    plt.grid(visible=True, which='minor', linestyle=':', linewidth=0.5)
    plt.legend(loc=2, prop={'size': 21})
    plt.savefig(save_path, bbox_inches='tight')
    plt.show()

def main():
    # Dobi trenutno mapo skripte in poišči CSV datoteke
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_files = [f for f in os.listdir(script_dir) if f.lower().endswith('.csv')]
    if not csv_files:
        print("V mapi ni CSV datotek.")
        return

    print("Dostopne CSV datoteke:")
    for i, file_name in enumerate(csv_files, start=1):
        print(f"{i}: {file_name}")

    # Uporabnik izbere datoteke za prikaz
    selected_indices = []
    while True:
        try:
            selection = input("Vnesi številke datotek za prikaz, ločene z vejicami (npr. 1,3,5): ")
            selected_indices = [
                int(idx.strip()) - 1 for idx in selection.split(",") if idx.strip().isdigit()
            ]
            if all(0 <= idx < len(csv_files) for idx in selected_indices):
                break
            else:
                print("Ena ali več izbranih številk ni v dosegu. Poskusi znova.")
        except ValueError:
            print("Neveljaven vnos. Vnesi številke, ločene z vejicami.")

    # Naloži podatke za vsako izbrano datoteko
    data_list = []
    for idx in selected_indices:
        file_path = os.path.join(script_dir, csv_files[idx])
        Vpp, angle = load_data(file_path)
        base_name, _ = os.path.splitext(csv_files[idx])
        data_list.append((angle, Vpp, base_name))

    # Ustvari pot za shranjevanje grafa
    base_names = "_".join([os.path.splitext(csv_files[idx])[0] for idx in selected_indices])
    save_path = os.path.join(script_dir, f"{base_names}_primerjalni_graf.svg")

    # Prikaz in shranjevanje grafa
    plot_multiple_Vpp(data_list, save_path)

if __name__ == "__main__":
    main()
