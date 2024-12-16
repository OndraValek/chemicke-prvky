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
def generate_html_table_with_colors(elements, filename="periodic_table_colored.html"):
    """Generování periodické tabulky s barvami skupin."""
    # Barevné schéma podle skupin
    group_colors = {
        "1": "#f7d7a8",  # Alkalické kovy
        "2": "#c6e5b3",  # Alkalické zeminy
        "3-12": "#ffc971",  # Přechodné kovy
        "13": "#ffeb99",  # Borová skupina
        "14": "#a7c7e7",  # Uhlíková skupina
        "15": "#d5a6bd",  # Dusíková skupina
        "16": "#b6d7a8",  # Chalkogeny
        "17": "#e06666",  # Halogeny
        "18": "#a4c2f4",  # Vzácné plyny
        "lanthanoids": "#d9d2e9",  # Lanthanoidy
        "actinoids": "#f4cccc",  # Aktinoidy
    }

    # Mřížka pro hlavní tabulku
    table = [["" for _ in range(18)] for _ in range(7)]

    lanthanoids = []
    actinoids = []

    for element in elements:
        try:
            group = element.get("Group", "")
            period = element.get("Period", "")
            atomic_number = element.get("AtomicNumber", "")
            symbol = element.get("Symbol", "")
            name = element.get("Element", "")
            atomic_mass = element.get("AtomicMass", "")

            # Zvláštní zacházení pro lanthanoidy a aktinoidy
            if 57 <= int(atomic_number) <= 71:
                lanthanoids.append(element)
                continue
            elif 89 <= int(atomic_number) <= 103:
                actinoids.append(element)
                continue

            # Umístění do tabulky
            if group and period:
                row = int(period) - 1
                col = int(group) - 1

                # Barva pro skupinu
                color = group_colors.get(group, "#ffffff")
                if 3 <= int(group) <= 12:
                    color = group_colors["3-12"]

                # HTML element
                table[row][col] = (
                    f"<div class='element' style='background-color: {color};'>"
                    f"<div class='atomic-number'>{atomic_number}</div>"
                    f"<div class='symbol'>{symbol}</div>"
                    f"<div class='name'>{name}</div>"
                    f"<div class='atomic-mass'>{atomic_mass}</div>"
                    f"</div>"
                )
        except ValueError:
            continue

    # Generování HTML
    with open(filename, "w", encoding="utf-8") as htmlfile:
        htmlfile.write("<!DOCTYPE html><html><head><style>")
        htmlfile.write("""
        body {
            font-family: Arial, sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 0;
        }
        .periodic-table {
            display: grid;
            grid-template-columns: repeat(18, 50px);
            gap: 2px;
            justify-content: center;
            margin: 20px auto;
        }
        .element {
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 5px;
            text-align: center;
            font-size: 0.8em;
        }
        .atomic-number {
            font-size: 0.6em;
            color: #555;
        }
        .symbol {
            font-size: 1.2em;
            font-weight: bold;
        }
        .name {
            font-size: 0.8em;
            color: #333;
        }
        .atomic-mass {
            font-size: 0.7em;
            color: #777;
        }
        .lanthanoids, .actinoids {
            display: grid;
            grid-template-columns: repeat(15, 50px);
            gap: 2px;
            justify-content: center;
            margin: 10px auto;
        }
        </style></head><body>
        <div class='periodic-table'>
        """)

        # Vkládání hlavní tabulky
        for row in table:
            for cell in row:
                if cell:
                    htmlfile.write(cell)
                else:
                    htmlfile.write("<div class='element' style='background-color: #f0f0f0;'></div>")

        # Lanthanoidy
        htmlfile.write("</div><h3>Lanthanoids</h3><div class='lanthanoids'>")
        for element in lanthanoids:
            color = group_colors["lanthanoids"]
            htmlfile.write(
                f"<div class='element' style='background-color: {color};'>"
                f"<div class='atomic-number'>{element['AtomicNumber']}</div>"
                f"<div class='symbol'>{element['Symbol']}</div>"
                f"<div class='name'>{element['Element']}</div>"
                f"<div class='atomic-mass'>{element['AtomicMass']}</div>"
                f"</div>"
            )

        # Aktinoidy
        htmlfile.write("</div><h3>Actinoids</h3><div class='actinoids'>")
        for element in actinoids:
            color = group_colors["actinoids"]
            htmlfile.write(
                f"<div class='element' style='background-color: {color};'>"
                f"<div class='atomic-number'>{element['AtomicNumber']}</div>"
                f"<div class='symbol'>{element['Symbol']}</div>"
                f"<div class='name'>{element['Element']}</div>"
                f"<div class='atomic-mass'>{element['AtomicMass']}</div>"
                f"</div>"
            )

        htmlfile.write("</div></body></html>")

    print(f"Periodická tabulka s barvami byla vygenerována a uložena jako {filename}.")


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
            generate_html_table_with_colors(elements)
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
