import os
import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(current_dir, "sadge_nations.txt")
history_dir = os.path.join(current_dir, "history")
old_nations_dir = os.path.join(current_dir, "old_nations")

matze_file = os.path.join(current_dir, "sadge_nations_matze.txt")
sven_file = os.path.join(current_dir, "sadge_nations_sven.txt")

if not os.path.exists(history_dir):
    os.makedirs(history_dir)
if not os.path.exists(old_nations_dir):
    os.makedirs(old_nations_dir)

header_line = ""
history_mode = False
current_history_version = 0

def replace_umlauts_in_str(s):
    if not s:
        return s
    s = s.replace("ä", "ae").replace("Ä", "Ae")
    s = s.replace("ö", "oe").replace("Ö", "Oe")
    s = s.replace("ü", "ue").replace("Ü", "Ue")
    return s

def replace_umlauts_in_all():
    for n in nations_data:
        n["clong"] = replace_umlauts_in_str(n["clong"])
        n["rgb"] = replace_umlauts_in_str(n["rgb"])
        n["leader_trait"] = replace_umlauts_in_str(n["leader_trait"])
        n["leader_name"] = replace_umlauts_in_str(n["leader_name"])
        n["owned_states"] = replace_umlauts_in_str(n["owned_states"])
        n["state_cores"] = replace_umlauts_in_str(n["state_cores"])
        n["stability"] = replace_umlauts_in_str(n["stability"])
        n["war_support"] = replace_umlauts_in_str(n["war_support"])
        n["factories"] = replace_umlauts_in_str(n["factories"])
        n["population"] = replace_umlauts_in_str(n["population"])

        n["traits"] = [replace_umlauts_in_str(t) for t in n["traits"]]

    update_listbox()
    messagebox.showinfo("Erfolg", "Umlaute wurden ersetzt.")

def load_data_from_file(path):
    nations = []
    global header_line
    if not os.path.exists(path):
        print(f"Datei '{path}' nicht gefunden: {path}")
        return nations

    with open(path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if lines:
            header_line = lines[0].rstrip("\n")
        header_skipped = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if not header_skipped:
                header_skipped = True
                continue
            
            parts = line.split("\t")
            if len(parts) < 17:
                parts += [""] * (17 - len(parts))

            nation_data = {
                "id": parts[0],
                "tag": parts[1],
                "clong": parts[2],
                "rgb": parts[3],
                "leader_trait": parts[4],
                "leader_name": parts[5],
                "traits": parts[6:11],
                "owned_states": parts[11],
                "state_cores": parts[12],
                "stability": parts[13],
                "war_support": parts[14],
                "factories": parts[15],
                "population": parts[16]
            }
            nations.append(nation_data)
    return nations

def load_data(filepath):
    return load_data_from_file(filepath)

def update_listbox():
    listbox.delete(*listbox.get_children())
    for nation in nations_data:
        values = (
            nation["id"], nation["tag"], nation["clong"], nation["rgb"],
            nation["leader_trait"], nation["leader_name"]
        ) + tuple(nation["traits"]) + (
            nation["owned_states"], nation["state_cores"],
            nation["stability"], nation["war_support"], nation["factories"], nation["population"]
        )
        listbox.insert("", "end", values=values)

def delete_selected():
    selected_items = listbox.selection()
    if not selected_items:
        return
    indices = [listbox.index(i) for i in selected_items]
    indices.sort(reverse=True)
    for idx in indices:
        nations_data.pop(idx)
    update_listbox()
    create_current_snapshot()

def nation_selected(event):
    selected_items = listbox.selection()
    count = len(selected_items)

    if count > 1:
        button_save.config(state="disabled")
        button_land.config(state="disabled")
    else:
        button_save.config(state="normal")
        button_land.config(state="normal")

    if count != 1:
        if count == 0:
            entry_land.delete(0, tk.END)
            entry_leader.delete(0, tk.END)
            entry_trait_name.delete(0, tk.END)
            entry_rgb.delete(0, tk.END)
            entry_trait_strings.delete(0, tk.END)
            entry_owned_states.delete(0, tk.END)
            entry_core_states.delete(0, tk.END)
            entry_stability.delete(0, tk.END)
            entry_war_support.delete(0, tk.END)
            entry_factories.delete(0, tk.END)
            entry_population.delete(0, tk.END)
        return

    item_index = listbox.index(selected_items[0])
    nation = nations_data[item_index]

    entry_land.delete(0, tk.END)
    entry_land.insert(0, nation["clong"])

    entry_leader.delete(0, tk.END)
    entry_leader.insert(0, nation["leader_name"])

    entry_trait_name.delete(0, tk.END)
    entry_trait_name.insert(0, nation["leader_trait"])

    rgb_parts = nation["rgb"].split()
    rgb_code = ",".join(rgb_parts) if rgb_parts else nation["rgb"]
    entry_rgb.delete(0, tk.END)
    entry_rgb.insert(0, rgb_code)

    trait_list = [t for t in nation["traits"] if t.strip()]
    entry_trait_strings.delete(0, tk.END)
    if trait_list:
        entry_trait_strings.insert(0, ",".join(trait_list))
    else:
        entry_trait_strings.delete(0, tk.END)

    entry_owned_states.delete(0, tk.END)
    if nation["owned_states"].strip():
        entry_owned_states.insert(0, nation["owned_states"])

    entry_core_states.delete(0, tk.END)
    if nation["state_cores"].strip():
        entry_core_states.insert(0, nation["state_cores"])

    entry_stability.delete(0, tk.END)
    if nation["stability"].strip():
        entry_stability.insert(0, nation["stability"])

    entry_war_support.delete(0, tk.END)
    if nation["war_support"].strip():
        entry_war_support.insert(0, nation["war_support"])

    entry_factories.delete(0, tk.END)
    if nation["factories"].strip():
        entry_factories.insert(0, nation["factories"])

    entry_population.delete(0, tk.END)
    if nation["population"].strip():
        entry_population.insert(0, nation["population"])

def create_current_snapshot():
    version = find_next_current_version()
    snapshot_path = os.path.join(history_dir, f"sadge_nations_current{version}.txt")
    with open(snapshot_path, "w", encoding="utf-8") as file:
        file.write(header_line + "\n")
        for n in nations_data:
            line = [
                n["id"], n["tag"], n["clong"], n["rgb"], n["leader_trait"], n["leader_name"]
            ] + n["traits"] + [
                n["owned_states"], n["state_cores"],
                n["stability"], n["war_support"], n["factories"], n["population"]
            ]
            file.write("\t".join(line) + "\n")

def find_max_current_version():
    pattern = re.compile(r"^sadge_nations_current(\d+)\.txt$")
    existing_numbers = []
    for f in os.listdir(history_dir):
        match = pattern.match(f)
        if match:
            num = int(match.group(1))
            existing_numbers.append(num)
    max_num = max(existing_numbers) if existing_numbers else 0
    return max_num

def find_next_current_version():
    return find_max_current_version() + 1

def load_current_version(version):
    path = os.path.join(history_dir, f"sadge_nations_current{version}.txt")
    if not os.path.exists(path):
        return False
    global nations_data, current_history_version, history_mode
    nations_data = load_data_from_file(path)
    current_history_version = version
    history_mode = True
    update_listbox()
    return True

def toggle_history():
    global history_mode, current_history_version
    if not history_mode:
        max_ver = find_max_current_version()
        if max_ver == 0:
            return
        if load_current_version(max_ver):
            button_history.config(text="Zurück")
    else:
        if current_history_version > 1:
            new_version = current_history_version - 1
            if load_current_version(new_version):
                if new_version == 1:
                    pass

def history_reset():
    if not messagebox.askyesno("Bestätigen", "Sind Sie sicher, dass Sie die History löschen möchten?"):
        return

    max_ver = find_max_current_version()
    if max_ver == 0:
        return
    highest_file = os.path.join(history_dir, f"sadge_nations_current{max_ver}.txt")

    pattern = re.compile(r"^sadge_nations_current(\d+)\.txt$")
    for f in os.listdir(history_dir):
        match = pattern.match(f)
        if match:
            num = int(match.group(1))
            if num != max_ver:
                os.remove(os.path.join(history_dir, f))

    if max_ver != 1:
        new_path = os.path.join(history_dir, "sadge_nations_current1.txt")
        os.rename(highest_file, new_path)
        max_ver = 1

    load_current_version(1)
    button_history.config(text="History Laden")
    global history_mode
    history_mode = False

def get_file_timestamp(filepath):
    ctime = os.path.getctime(filepath)
    dt = datetime.fromtimestamp(ctime)
    return dt.strftime("%Y.%m.%d - %H-%M-%S")

def find_next_updated_filename():
    pattern = re.compile(r"^sadge_nations_updated(\d+)\.txt$")
    existing_numbers = []
    for f in os.listdir(current_dir):
        match = pattern.match(f)
        if match:
            num = int(match.group(1))
            existing_numbers.append(num)
    max_num = max(existing_numbers) if existing_numbers else 0
    return os.path.join(current_dir, f"sadge_nations_updated{max_num+1}.txt")

def find_next_merged_filename():
    pattern = re.compile(r"^sadge_nations_merged(\d+)\.txt$")
    existing_numbers = []
    for f in os.listdir(current_dir):
        match = pattern.match(f)
        if match:
            num = int(match.group(1))
            existing_numbers.append(num)
    max_num = max(existing_numbers) if existing_numbers else 0
    return os.path.join(current_dir, f"sadge_nations_merged{max_num+1}.txt")

def merge_feature():
    if not os.path.exists(matze_file) or not os.path.exists(sven_file):
        messagebox.showerror("Fehler", "Die Dateien sadge_nations_matze.txt und sadge_nations_sven.txt müssen existieren!")
        return

    matze_data = load_data_from_file(matze_file)
    sven_data = load_data_from_file(sven_file)

    merged_dict = {}
    for n in matze_data:
        c = n["clong"]
        if c not in merged_dict:
            merged_dict[c] = n

    for n in sven_data:
        c = n["clong"]
        if c not in merged_dict:
            merged_dict[c] = n

    merged_list = list(merged_dict.values())
    merged_list.sort(key=lambda x: x["clong"])
    new_id_num = 1
    for n in merged_list:
        n["id"] = str(new_id_num)
        new_id_str = str(new_id_num)
        if len(new_id_str) == 1:
            new_id_str = "0" + new_id_str
        n["tag"] = "S" + new_id_str
        new_id_num += 1

    merged_path = find_next_merged_filename()
    with open(merged_path, "w", encoding="utf-8") as file:
        file.write(header_line + "\n")
        for n in merged_list:
            line = [
                n["id"],
                n["tag"],
                n["clong"],
                n["rgb"],
                n["leader_trait"],
                n["leader_name"]
            ] + n["traits"] + [
                n["owned_states"], n["state_cores"],
                n["stability"], n["war_support"],
                n["factories"], n["population"]
            ]
            file.write("\t".join(line) + "\n")

    messagebox.showinfo("Erfolg", f"Merge abgeschlossen! Die Datei {os.path.basename(merged_path)} wurde erstellt.\nInhalt: {len(merged_list)} Nationen.")

def save_data():
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(header_line + "\n")
        for n in nations_data:
            line = [
                n["id"],
                n["tag"],
                n["clong"],
                n["rgb"],
                n["leader_trait"],
                n["leader_name"]
            ] + n["traits"] + [
                n["owned_states"], n["state_cores"],
                n["stability"], n["war_support"],
                n["factories"], n["population"]
            ]
            file.write("\t".join(line) + "\n")

def create_updated_file():
    new_filepath = find_next_updated_filename()
    with open(new_filepath, "w", encoding="utf-8") as file:
        file.write(header_line + "\n")
        for n in nations_data:
            line = [
                n["id"], n["tag"], n["clong"], n["rgb"],
                n["leader_trait"], n["leader_name"]
            ] + n["traits"] + [
                n["owned_states"], n["state_cores"],
                n["stability"], n["war_support"],
                n["factories"], n["population"]
            ]
            file.write("\t".join(line) + "\n")
    messagebox.showinfo("Erfolg", f"Updated-Datei {os.path.basename(new_filepath)} wurde erstellt.")

def datei_speichern_action():
    create_updated_file()

def update_clong():
    # Hole den aktuell ausgewählten Eintrag
    selected_items = listbox.selection()

    if not selected_items:
        messagebox.showwarning("Warnung", "Bitte wählen Sie ein Land aus, das aktualisiert werden soll.")
        return
    
    # Hole den Index des ausgewählten Eintrags
    item_index = listbox.index(selected_items[0])
    
    # Hole die neuen Werte aus den Textfeldern
    new_land = entry_land.get().strip()
    new_leader = entry_leader.get().strip()
    new_trait = entry_trait_name.get().strip()
    new_rgb = entry_rgb.get().strip()
    new_trait_string = entry_trait_strings.get().strip()
    new_stability = entry_stability.get().strip()
    new_war_support = entry_war_support.get().strip()
    new_factories = entry_factories.get().strip()
    new_population = entry_population.get().strip()

    # Verarbeiten der Trait-Strings
    traits_list = [t.strip() for t in new_trait_string.split(",") if t.strip()]
    while len(traits_list) < 5:
        traits_list.append("")
    if len(traits_list) > 5:
        traits_list = traits_list[:5]

    new_owned_states = entry_owned_states.get().strip()
    new_state_cores = entry_core_states.get().strip()

    if not new_land:
        messagebox.showwarning("Warnung", "Das Land-Feld darf nicht leer sein.")
        return
    
    # Aktualisiere alle Felder der ausgewählten Nation
    nations_data[item_index]["clong"] = new_land
    nations_data[item_index]["leader_name"] = new_leader
    nations_data[item_index]["leader_trait"] = new_trait
    nations_data[item_index]["rgb"] = " ".join(new_rgb.split(",")) if new_rgb else ""
    nations_data[item_index]["traits"] = traits_list
    nations_data[item_index]["owned_states"] = new_owned_states
    nations_data[item_index]["state_cores"] = new_state_cores
    nations_data[item_index]["stability"] = new_stability
    nations_data[item_index]["war_support"] = new_war_support
    nations_data[item_index]["factories"] = new_factories
    nations_data[item_index]["population"] = new_population

    # Aktualisiere die Listbox, um die Änderung anzuzeigen
    update_listbox()


def get_unique_filename(base_path):
    counter = 1
    new_name = base_path
    while os.path.exists(new_name):  # Überprüfen, ob die Datei existiert
        # Wenn die Datei existiert, füge eine fortlaufende Zahl an den Namen an
        new_name = f"{base_path[:-4]}_{counter}.txt"  # Entferne ".txt" und füge den Zähler hinzu
        counter += 1
    return new_name
    
def konsolidieren():
    pattern = re.compile(r"^sadge_nations_updated(\d+)\.txt$")
    updated_files = []
    
    # Suche nach allen "updated"-Dateien im aktuellen Verzeichnis
    for f in os.listdir(current_dir):
        match = pattern.match(f)
        if match:
            num = int(match.group(1))
            updated_files.append((num, f))
    
    updated_files.sort(key=lambda x: x[0])  # Sortiere nach Versionsnummer

    if not updated_files:
        messagebox.showinfo("Info", "Keine updated Dateien vorhanden zum Konsolidieren.")
        return

    # Die neueste Datei ermitteln (mit der höchsten Nummer)
    max_num, max_file = updated_files[-1]
    print(f"max_num: {max_num}, max_file: {max_file}")  # Log-Ausgabe für max_num und max_file
    newest_path = os.path.join(current_dir, max_file)
    
    # Lade die neueste "updated"-Datei
    global nations_data
    nations_data = load_data_from_file(newest_path)
    
    if not nations_data:
        messagebox.showerror("Fehler", "Neueste updated Datei ist leer oder fehlerhaft.")
        return

    # Speichere die konsolidierten Nationen-Daten in "sadge_nations.txt"
    save_data()

    # Verschiebe alle alten "updated"-Dateien in den Ordner "old_nations"
    for num, fname in updated_files:
        print(f"Vergleiche num: {num} mit max_num: {max_num}")  # Log-Ausgabe für num und max_num
        if num != max_num:  # Überspringe die neueste Datei
            old_path = os.path.join(current_dir, fname)
            ts = get_file_timestamp(old_path)  # Hole den Timestamp der Datei
            new_name = f"{ts}_snc.txt"
            new_name = get_unique_filename(os.path.join(old_nations_dir, new_name))
            new_path = os.path.join(old_nations_dir, new_name)
            try:
                os.rename(old_path, new_path)  # Datei umbenennen und verschieben
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Verschieben der Datei: {e}")
        if num == max_num:
            sadge_path = "sadge_nations.txt" 
            if os.path.exists(sadge_path):
                        os.remove(sadge_path)
            os.rename(fname,"sadge_nations.txt")

def restart_script():
    os.execl(sys.executable, sys.executable, *sys.argv)

def open_mass_fill_window():
    mass_fill_window = tk.Toplevel(root)
    mass_fill_window.title("Mass Fill")
    mass_fill_window.geometry("600x600")  # Fenstergröße um 100% vergrößern
    
    # Hintergrundfarbe des Fensters anpassen
    mass_fill_window.configure(bg="#2c2c2c")
    
    tk.Label(mass_fill_window, text="Wählen Sie die Spalten aus, die Sie füllen möchten:", bg="#2c2c2c", fg="white").pack(pady=10)
    
    # Checkboxen für jede Spalte mit angepasstem Hintergrund
    columns_to_fill = [
        "ID", "TAG", "CLONG", "RGB", "Leader Trait", "Leader Name",
        "Trait1", "Trait2", "Trait3", "Trait4", "Trait5",
        "OwnedStates", "StateCores", "stability", "war_support", "factories", "population"
    ]
    
    selected_columns = []
    var_dict = {}
    
    for col in columns_to_fill:
        var_dict[col] = tk.BooleanVar()
        checkbox = tk.Checkbutton(mass_fill_window, text=col, variable=var_dict[col], bg="#2c2c2c", fg="white", selectcolor="#555", highlightthickness=2, relief="solid")
        checkbox.pack(anchor="w", padx=20)  # Etwas Abstand zu den Rändern hinzufügen

    # Textfeld für den Wert
    tk.Label(mass_fill_window, text="Wert für die ausgewählten Spalten:", bg="#2c2c2c", fg="white").pack(pady=10)
    entry_value = tk.Entry(mass_fill_window, width=30)
    entry_value.pack(pady=5)

    # Funktion, die ausgeführt wird, wenn der Benutzer den Wert bestätigt
    def apply_mass_fill():
        value = entry_value.get().strip()
        if not value:
            messagebox.showwarning("Warnung", "Bitte einen Wert eingeben.")
            return
        
        # Durch alle Nationen gehen und die ausgewählten Spalten füllen
        for nation in nations_data:
            for col, var in var_dict.items():
                if var.get():
                    if col == "ID":
                        nation["id"] = value
                    elif col == "TAG":
                        nation["tag"] = value
                    elif col == "CLONG":
                        nation["clong"] = value
                    elif col == "RGB":
                        nation["rgb"] = value
                    elif col == "Leader Trait":
                        nation["leader_trait"] = value
                    elif col == "Leader Name":
                        nation["leader_name"] = value
                    elif col == "Trait1":
                        nation["traits"][0] = value
                    elif col == "Trait2":
                        nation["traits"][1] = value
                    elif col == "Trait3":
                        nation["traits"][2] = value
                    elif col == "Trait4":
                        nation["traits"][3] = value
                    elif col == "Trait5":
                        nation["traits"][4] = value
                    elif col == "OwnedStates":
                        nation["owned_states"] = value
                    elif col == "StateCores":
                        nation["state_cores"] = value
                    elif col == "stability":
                        nation["stability"] = value
                    elif col == "war_support":
                        nation["war_support"] = value
                    elif col == "factories":
                        nation["factories"] = value
                    elif col == "population":
                        nation["population"] = value

        update_listbox()
        mass_fill_window.destroy()
        create_current_snapshot()
        messagebox.showinfo("Erfolg", "Die ausgewählten Spalten wurden erfolgreich gefüllt.")
    
    # Button zum Bestätigen
    button_apply = tk.Button(mass_fill_window, text="Anwenden", command=apply_mass_fill, bg="#444", fg="white")
    button_apply.pack(pady=20)


def save_or_update_entry():
    land = entry_land.get().strip()
    leader = entry_leader.get().strip()
    trait = entry_trait_name.get().strip()
    rgb_input = entry_rgb.get().strip()
    trait_string = entry_trait_strings.get().strip()
    stability = entry_stability.get().strip()
    war_support = entry_war_support.get().strip()
    factories = entry_factories.get().strip()
    population = entry_population.get().strip()

    traits_list = [t.strip() for t in trait_string.split(",") if t.strip()]
    while len(traits_list) < 5:
        traits_list.append("")
    if len(traits_list) > 5:
        traits_list = traits_list[:5]

    owned_states = entry_owned_states.get().strip()
    state_cores = entry_core_states.get().strip()

    existing_nation = None
    for n in nations_data:
        if n["clong"] == land:
            existing_nation = n
            break

    if existing_nation:
        existing_nation["clong"] = land
        existing_nation["leader_name"] = leader
        existing_nation["leader_trait"] = trait
        existing_nation["rgb"] = " ".join(rgb_input.split(",")) if rgb_input else ""
        existing_nation["traits"] = traits_list
        existing_nation["owned_states"] = owned_states
        existing_nation["state_cores"] = state_cores
        existing_nation["stability"] = stability
        existing_nation["war_support"] = war_support
        existing_nation["factories"] = factories
        existing_nation["population"] = population
    else:
        max_id_num = 0
        for n in nations_data:
            try:
                nid = int(n["id"])
                if nid > max_id_num:
                    max_id_num = nid
            except ValueError:
                pass
        new_id_num = max_id_num + 1
        new_id_str = str(new_id_num)
        if len(new_id_str) == 1:
            new_id_str = "0" + new_id_str
        tag = "S" + new_id_str

        nation_data = {
            "id": str(new_id_num),
            "tag": tag,
            "clong": land,
            "rgb": " ".join(rgb_input.split(",")) if rgb_input else "",
            "leader_trait": trait,
            "leader_name": leader,
            "traits": traits_list,
            "owned_states": owned_states,
            "state_cores": state_cores,
            "stability": stability,
            "war_support": war_support,
            "factories": factories,
            "population": population
        }
        nations_data.append(nation_data)

    update_listbox()
    create_current_snapshot()

nations_data = load_data(filepath)

root = tk.Tk()
root.title("Sadge Nations Editor")
root.geometry("1000x900")
root.configure(bg="#2c2c2c")

frame_list = tk.Frame(root, bg="#2c2c2c")
frame_list.place(x=10, y=10, width=780, height=580)
frame_list.grid_rowconfigure(0, weight=1)
frame_list.grid_columnconfigure(0, weight=1)

columns = (
    "ID", "TAG", "CLONG", "RGB", "Leader Trait", "Leader Name",
    "Trait1", "Trait2", "Trait3", "Trait4", "Trait5",
    "OwnedStates", "StateCores", "stability", "war_support", "factories", "population"
)

listbox = ttk.Treeview(frame_list, columns=columns, show="headings", selectmode="extended")
listbox.column("ID", width=40)
listbox.column("TAG", width=40)
listbox.column("CLONG", width=100)
listbox.column("RGB", width=60)
listbox.column("Leader Trait", width=100)
listbox.column("Leader Name", width=100)
listbox.column("Trait1", width=60)
listbox.column("Trait2", width=60)
listbox.column("Trait3", width=60)
listbox.column("Trait4", width=60)
listbox.column("Trait5", width=60)
listbox.column("OwnedStates", width=80)
listbox.column("StateCores", width=80)
listbox.column("stability", width=60)
listbox.column("war_support", width=60)
listbox.column("factories", width=80)
listbox.column("population", width=80)

for col in columns:
    listbox.heading(col, text=col)

scrollbar_y = ttk.Scrollbar(frame_list, orient="vertical", command=listbox.yview)
scrollbar_x = ttk.Scrollbar(frame_list, orient="horizontal", command=listbox.xview)
listbox.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

listbox.grid(row=0, column=0, sticky="nsew")
scrollbar_y.grid(row=0, column=1, sticky="ns")
scrollbar_x.grid(row=1, column=0, sticky="ew")

frame_buttons = tk.Frame(root, bg="#2c2c2c")
frame_buttons.place(x=800, y=10, width=180, height=580)

frame_combined_button = tk.Frame(frame_buttons, bg="#2c2c2c")
frame_combined_button.pack(fill="x", pady=10)
frame_combined_button.grid_columnconfigure(0, weight=7)
frame_combined_button.grid_columnconfigure(1, weight=3)

button_save = tk.Button(frame_combined_button, text="Neu", command=save_or_update_entry, bg="#444", fg="white", height=2)
button_save.grid(row=0, column=0, sticky="nsew")

button_land = tk.Button(frame_combined_button, text="Bearbeiten", command=update_clong, bg="#444", fg="white", height=2)
button_land.grid(row=0, column=1, sticky="nsew")

button_loeschen = tk.Button(frame_buttons, text="Löschen", command=delete_selected, bg="#444", fg="white")
button_loeschen.pack(fill="x", pady=10)

# Mass Fill Button hier
button_mass_fill = tk.Button(frame_buttons, text="Mass Fill", command=open_mass_fill_window, bg="#444", fg="white")
button_mass_fill.pack(fill="x", pady=10)

tk.Label(frame_buttons, text="", bg="#2c2c2c", height=2).pack()

button_speichern_datei = tk.Button(frame_buttons, text="Datei speichern", command=datei_speichern_action, bg="#444", fg="white")
button_speichern_datei.pack(fill="x", pady=10)

button_history = tk.Button(frame_buttons, text="History Laden", command=toggle_history, bg="#444", fg="white")
button_history.pack(fill="x", pady=10)

button_history_reset = tk.Button(frame_buttons, text="History Löschen", command=history_reset, bg="#444", fg="white")
button_history_reset.pack(fill="x", pady=10)

tk.Label(frame_buttons, text="", bg="#2c2c2c", height=2).pack()

button_konsolidieren = tk.Button(frame_buttons, text="Konsolidieren", command=konsolidieren, bg="#444", fg="white")
button_konsolidieren.pack(fill="x", pady=10)

button_mergen = tk.Button(frame_buttons, text="Mergen", command=merge_feature, bg="#444", fg="white")
button_mergen.pack(fill="x", pady=10)

button_umlaute = tk.Button(frame_buttons, text="Umlaute ersetzen", command=replace_umlauts_in_all, bg="#444", fg="white")
button_umlaute.pack(fill="x", pady=10)

button_reload = tk.Button(frame_buttons, text="SNC Reload", command=restart_script, bg="#444", fg="white")
button_reload.pack(fill="x", pady=10)

# Das Input-Formular bleibt gleich
frame_input = tk.Frame(root, bg="#2c2c2c")
frame_input.place(x=10, y=600, width=980, height=280)

label_land = tk.Label(frame_input, text="Land", bg="#2c2c2c", fg="white")
label_land.grid(row=0, column=0, padx=5, pady=(5,0))
label_leader = tk.Label(frame_input, text="Leader", bg="#2c2c2c", fg="white")
label_leader.grid(row=0, column=1, padx=5, pady=(5,0))
label_trait = tk.Label(frame_input, text="Trait", bg="#2c2c2c", fg="white")
label_trait.grid(row=0, column=2, padx=5, pady=(5,0))
label_rgb = tk.Label(frame_input, text="RGB", bg="#2c2c2c", fg="white")
label_rgb.grid(row=0, column=3, padx=5, pady=(5,0))

entry_land = tk.Entry(frame_input, width=30)
entry_land.grid(row=1, column=0, padx=5, pady=5)
entry_leader = tk.Entry(frame_input, width=30)
entry_leader.grid(row=1, column=1, padx=5, pady=5)
entry_trait_name = tk.Entry(frame_input, width=30)
entry_trait_name.grid(row=1, column=2, padx=5, pady=5)
entry_rgb = tk.Entry(frame_input, width=30)
entry_rgb.grid(row=1, column=3, padx=5, pady=5)

label_trait_strings = tk.Label(frame_input, text="Trait-Strings", bg="#2c2c2c", fg="white")
label_trait_strings.grid(row=2, column=0, padx=5, pady=(5,0), sticky="w")
entry_trait_strings = tk.Entry(frame_input, width=60)
entry_trait_strings.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

label_owned_states = tk.Label(frame_input, text="OwnedStates", bg="#2c2c2c", fg="white")
label_owned_states.grid(row=2, column=2, padx=5, pady=(5,0), sticky="w")
entry_owned_states = tk.Entry(frame_input, width=60)
entry_owned_states.grid(row=3, column=2, columnspan=2, padx=5, pady=5, sticky="w")

label_core_states = tk.Label(frame_input, text="CoreStates", bg="#2c2c2c", fg="white")
label_core_states.grid(row=2, column=4, padx=5, pady=(5,0), sticky="w")
entry_core_states = tk.Entry(frame_input, width=60)
entry_core_states.grid(row=3, column=4, columnspan=2, padx=5, pady=5, sticky="w")

label_stability = tk.Label(frame_input, text="Stability (-1 bis 1)", bg="#2c2c2c", fg="white")
label_stability.grid(row=4, column=0, padx=5, pady=(5,0), sticky="w")
entry_stability = tk.Entry(frame_input, width=20)
entry_stability.grid(row=5, column=0, padx=5, pady=5, sticky="w")

label_war_support = tk.Label(frame_input, text="War Support (0 bis 1)", bg="#2c2c2c", fg="white")
label_war_support.grid(row=4, column=1, padx=5, pady=(5,0), sticky="w")
entry_war_support = tk.Entry(frame_input, width=20)
entry_war_support.grid(row=5, column=1, padx=5, pady=5, sticky="w")

label_factories = tk.Label(frame_input, text="Factories (civi,mil)", bg="#2c2c2c", fg="white")
label_factories.grid(row=4, column=2, padx=5, pady=(5,0), sticky="w")
entry_factories = tk.Entry(frame_input, width=20)
entry_factories.grid(row=5, column=2, padx=5, pady=5, sticky="w")

label_population = tk.Label(frame_input, text="Population", bg="#2c2c2c", fg="white")
label_population.grid(row=4, column=3, padx=5, pady=(5,0), sticky="w")
entry_population = tk.Entry(frame_input, width=20)
entry_population.grid(row=5, column=3, padx=5, pady=5, sticky="w")

nations_data = load_data(filepath)
update_listbox()
create_current_snapshot()

listbox.bind("<<TreeviewSelect>>", nation_selected)

root.mainloop()
