import csv
import json

groups_filename = 'groups.json'


def print_element(element):
    """Funkce pro formátovaný tisk detailů prvku."""
    for key, value in element.items():
        print(f"{key}: {value}")


# Načtení dat
def load_elements(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            elements = [row for row in reader]
            return elements
    except FileNotFoundError:
        print(f"Soubor {file_path} nebyl nalezen.")
        return []


def load_groups(filename):
    with open(filename, mode='r', encoding='utf-8') as file:
        return json.load(file)


# Zobrazení prvku podle kritéria
def find_element(elements, key, value):
    try:
        # Mapování uživatelských klíčů na názvy v CSV
        key_map = {
            "proton_number": "NumberofProtons",
            "symbol": "Symbol",
            "group": "Group",
            "period": "Period"
        }
        key = key_map.get(key, key)  # Převod klíče, pokud existuje v mapě

        # Pokud hledáme číselnou hodnotu, převádíme vstup na int
        if key in ["NumberofProtons", "Group", "Period"]:
            value = int(value)

        # Porovnání hodnot
        return [el for el in elements if str(el.get(key, '')).strip().lower() == str(value).strip().lower()]
    except Exception as e:
        print(f"Chyba při hledání: {e}")
        return []


# Výpočet průměrné relativní atomové hmotnosti
def calculate_average_atomic_mass(elements, key, value):
    try:
        # Mapování klíčů
        key_map = {"group": "Group", "period": "Period"}
        key = key_map.get(key, key)

        # Přeskakujeme prázdné hodnoty a filtrujeme
        valid_elements = [
            el for el in elements
            if key in el and el[key].strip() and el.get("AtomicMass", '').strip()
        ]

        filtered_elements = [
            el for el in valid_elements if str(el[key]).strip() == str(value).strip()
        ]

        if not filtered_elements:
            print(f"Žádné prvky neodpovídají zadaným kritériím ({key} = {value}).")
            return None

        # Výpočet průměrné hmotnosti
        atomic_masses = [float(el["AtomicMass"]) for el in filtered_elements if el["AtomicMass"].strip()]
        if not atomic_masses:
            print("Žádné platné atomové hmotnosti k výpočtu.")
            return None

        return sum(atomic_masses) / len(atomic_masses)
    except Exception as e:
        print(f"Došlo k chybě: {e}")
        return None


# Generování HTML tabulky s názvy a CSS styly
def generate_html_table(elements, filename="generated/periodic_table.html"):
    # Načtení skupin z JSON
    with open(groups_filename, 'r', encoding='utf-8') as file:
        groups = json.load(file)

    # Přiřazení skupin prvkům
    element_classes = {}
    group_colors = {}
    css_rules = []
    for group in groups:
        group_name = group['cs']
        color = f"hsl({len(group['elements']) * 30}, 70%, 80%)"  # Dynamická barva
        group_colors[group_name] = color
        css_rules.append(f".{group_name.replace(' ', '_')} {{ background-color: {color}; }}")
        for element in group['elements']:
            element_classes[element] = group_name.replace(' ', '_')

    # Kontrola přítomnosti 'atomic_number' u každého prvku
    lanthanoids = [e for e in elements if 'atomic_number' in e and 57 <= e['atomic_number'] <= 71]
    actinoids = [e for e in elements if 'atomic_number' in e and 89 <= e['atomic_number'] <= 103]
    main_elements = [e for e in elements if 'atomic_number' in e and e not in lanthanoids and e not in actinoids]

    # Vytvoření mřížky pro periodickou tabulku
    table = [["" for _ in range(18)] for _ in range(7)]

    for element in main_elements:
        try:
            group = int(element['group'])
            period = int(element['period'])
            element_class = element_classes.get(element['symbol'], "unknown")
            if element['atomic_number'] == 57 or element['atomic_number'] == 89:
                # Prázdné místo pro lanthanoidy/aktinoidy
                table[period - 1][group - 1] = "<div class='empty'></div>"
            else:
                # Tady je ten kód, který dává HTML pro každý prvek
                table[period - 1][group - 1] = (
                    f"<div class='element {element_class}' onclick=\"showPopup("
                    f"'{element['symbol']}', "
                    f"'{element['name']}', "
                    f"{element['atomic_number']}, "
                    f"'{element['group']}', "
                    f"'{element['period']}', "
                    f"{element['atomic_weight']}, "
                    f"'{element['state']}')\">"
                    f"<div class='atomic-number'>{element['atomic_number']}</div>"
                    f"<div class='symbol'>{element['symbol']}</div>"
                    f"<div class='name'>{element['name']}</div>"
                    f"<div class='atomic-weight'>{element['atomic_weight']}</div>"
                    f"</div>"
                )
        except ValueError:
            continue

    # Generování HTML
    with open(filename, 'w', encoding='utf-8') as htmlfile:
        htmlfile.write("<!DOCTYPE html><html><head><style>")
        htmlfile.write("""
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f9f9f9;
        }
        .periodic-table {
            display: grid;
            grid-template-columns: repeat(18, 1fr); /* All columns have the same width */
            gap: 2px;
            max-width: 95vw;
            margin: auto;
        }
        .lanthanoids, .actinoids {
            display: grid;
            grid-template-columns: repeat(15, 1fr);
            gap: 2px;
            margin: 10px auto;
            max-width: 95vw;
        }
        .lanthanoids {
            margin-bottom: 20px; /* Add margin to separate lanthanoids and actinoids */
        }
        .element {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: transform 0.2s ease-in-out;
        }
        .element:hover {
            transform: scale(1.05);
        }
        .empty {
            border: 1px solid transparent;
            background-color: #f0f0f0;
        }
        .atomic-number {
            font-size: 0.7em;
            color: #666;
        }
        .symbol {
            font-size: 1.2em;
            font-weight: bold;
        }
        .name {
            font-size: 0.8em;
            color: #333;
        }
        .atomic-weight {
            font-size: 0.7em;
            color: #999;
        }
        .overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: none;
            z-index: 1000;
        }
        .popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            display: none;
            z-index: 1001;
        }
        .popup .close {
            position: absolute;
            top: 10px;
            right: 10px;
            cursor: pointer;
            font-size: 1.2em;
        }
        """ + "\n".join(css_rules) + """
        </style></head><body>
        <div class='overlay' id='overlay' onclick='hidePopup()'></div>
        <div class='popup' id='popup'>
            <span class='close' onclick='hidePopup()'>×</span>
            <div id='popup-content'></div>
        </div>
        <div class='periodic-table'>
        """)
        # Generování hlavní tabulky
        for row in table:
            for cell in row:
                if cell:
                    htmlfile.write(cell)
                else:
                    htmlfile.write("<div class='element' style='background-color: #f0f0f0;'></div>")

        htmlfile.write("""<script>
        function showPopup(symbol, name, atomicNumber, group, period, atomicWeight, state) {
            const popup = document.getElementById('popup');
            const overlay = document.getElementById('overlay');
            const content = document.getElementById('popup-content');
            content.innerHTML = `
                <h2>${name} (${symbol})</h2>
                <p><strong>Atomic Number:</strong> ${atomicNumber}</p>
                <p><strong>Group:</strong> ${group}</p>
                <p><strong>Period:</strong> ${period}</p>
                <p><strong>Atomic Weight:</strong> ${atomicWeight}</p>
                <p><strong>State:</strong> ${state}</p>
            `;
            popup.style.display = 'block';
            overlay.style.display = 'block';
        }
        function hidePopup() {
            const popup = document.getElementById('popup');
            const overlay = document.getElementById('overlay');
            popup.style.display = 'none';
            overlay.style.display = 'none';
        }
        </script>
        </body></html>
        """)

    print(f"Periodická tabulka s lanthanoidy a aktinoidy byla vygenerována a uložena jako {filename}.")


# Export do Markdown
# Funkce na vytvoření Markdown souboru
def generate_markdown(csv_file, json_file, group=None, period=None, output_file="elements.md"):
    # Načtení CSV souboru
    with open(csv_file, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        elements = list(reader)

    # Načtení JSON souboru
    with open(json_file, encoding='utf-8') as f:
        groups = json.load(f)

    # Filtrování prvků podle skupiny nebo periody
    filtered_elements = []

    if group:
        # Najdi skupinu v JSON podle názvu nebo překladu
        selected_group = next((g for g in groups if g["en"] == group or g["cs"] == group), None)
        if selected_group:
            group_elements = selected_group["elements"]
            filtered_elements = [e for e in elements if e["Symbol"] in group_elements]

    if period:
        filtered_elements = [e for e in elements if e["Period"] == str(period)]

    if group and period:
        filtered_elements = [e for e in filtered_elements if e["Period"] == str(period)]

    # Pokud nejsou nalezené prvky, vrať upozornění
    if not filtered_elements:
        print("No elements found for the specified group or period.")
        return

    # Vytvoření Markdown obsahu
    markdown_content = "# Elements Overview\n\n"

    if group:
        markdown_content += f"## Group: {group}\n"
        if selected_group:
            markdown_content += f"{selected_group['description']}\n\n"

    if period:
        markdown_content += f"## Period: {period}\n\n"

    markdown_content += "| Atomic Number | Element | Symbol | Atomic Mass | Period | Group | Type |\n"
    markdown_content += "|---------------|---------|--------|-------------|--------|-------|------|\n"

    for element in filtered_elements:
        markdown_content += (
            f"| {element['AtomicNumber']} | {element['Element']} | {element['Symbol']} | "
            f"{element['AtomicMass']} | {element['Period']} | {element['Group']} | {element['Type']} |\n"
        )

    # Uložení do souboru
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file '{output_file}' has been created.")


# Příklad použití
generate_markdown("elements.csv", "groups.json", group="Alkalické kovy", period=2)


# Hlavní menu aplikace
def main():
    elements = load_elements("elements.csv")
    groups = load_groups("groups.json")

    while True:
        print("\nMenu:")
        print("1. Vyhledat prvek podle kritéria")
        print("2. Vypočítat průměrnou relativní atomovou hmotnost")
        print("3. Generovat HTML tabulku")
        print("4. Exportovat do Markdown")
        print("5. Ukončit")

        choice = input("Vyberte možnost: ")
        if choice == '1':
            key = input("Zadejte kritérium (např. symbol, proton_number, group): ")
            value = input("Zadejte hodnotu: ")
            results = find_element(elements, key, value)
            if results:
                for result in results:
                    print("\nNalezený prvek:")
                    print_element(result)
            else:
                print("Žádný prvek neodpovídá zadaným kritériím.")
        elif choice == '2':
            key = input("Zadejte kritérium (např. group, period): ")
            value = input("Zadejte hodnotu: ")
            avg_mass = calculate_average_atomic_mass(elements, key, value)
            print(f"Průměrná relativní atomová hmotnost: {avg_mass}" if avg_mass else "Nelze vypočítat průměr.")
        elif choice == '3':
            generate_html_table(elements)
            print("HTML tabulka byla vygenerována.")
        elif choice == '4':
            generate_markdown("elements.csv", "groups.json")
            print("Export do Markdown byl úspěšný.")
        elif choice == '5':
            print("Ukončuji aplikaci.")
            break
        else:
            print("Neplatná volba. Zkuste to znovu.")


if __name__ == "__main__":
    main()
