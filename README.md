# ÖPNV-Router Karlsruhe

Ein Python-basiertes Routingsystem für den öffentlichen Nahverkehr in Karlsruhe.  
**Berechnet optimale Verbindungen zwischen Haltestellen oder Adressen auf Basis von GTFS-Daten.**

---

## Inhaltsverzeichnis

- [Features](#features)
- [Projektstruktur](#projektstruktur)
- [Installation](#installation)
- [GTFS-Daten](#gtfs-daten)
- [Nutzung](#nutzung)
- [Beispiel](#beispiel)
- [Hinweise & Troubleshooting](#hinweise--troubleshooting)
- [Lizenz](#lizenz)

---

## Features

- Routing zwischen beliebigen Haltestellen
- Unterstützung für Bus, Bahn, Tram (wahlweise)
- Richtungsabhängige Haltestellenerkennung für zweigleisige Systeme
- Umstiegsoptimierung und Zeitfenster-Suche
- Fuzzy-Matching für Haltestellennamen
- Übersichtliche Routenausgabe

---

## Projektstruktur

| Datei/Ordner                | Beschreibung                                         |
|-----------------------------|-----------------------------------------------------|
| `main.py`                   | Hauptprogramm, Einstiegspunkt                       |
| `routing.py`                | Routing-Algorithmen (mit und ohne Umstieg)          |
| `auto_choose.py`            | Richtungsabhängige Haltestellenwahl                 |
| `utils.py`                  | Hilfsfunktionen: Matching, Geokodierung, Ausgabe    |
| `parent_station_utils.py`   | Funktionen für parent_station-Logik                 |
| `gtfs_processing.py`        | Laden und Vorverarbeiten der GTFS-Daten             |
| `karlsruhe_addresses.csv`   | Adressdatenbank für Adresssuche (optional)          |
| `graph.pkl`                 | Serialisierter Transit-Graph (wird beim ersten Start erzeugt) |

---

## Installation

1. **Repository klonen**

    ```
    git clone https://github.com/DEIN-NAME/DEIN-REPO.git
    cd DEIN-REPO
    ```

2. **Abhängigkeiten installieren**

    ```
    pip install -r requirements.txt
    ```
    _Benötigte Pakete (Beispiel):_
    - pandas
    - numpy
    - networkx
    - rapidfuzz

3. **GTFS-Daten bereitstellen**  
    Die GTFS-Daten sind aus Speicherplatz **nicht im Repository enthalten**.  
    - Lade die GTFS-Daten für Karlsruhe (https://www.kvv.de/fahrplan/fahrplaene/open-data.html) herunter.
    - Entpacke alle Dateien (`stops.txt`, `routes.txt`, `trips.txt`, `stop_times.txt`, `calendar.txt`, `calendar_dates.txt` etc.) in einen Ordner `gtfs/` im Projektverzeichnis.

4. **(Optional) Adressdatenbank**  
    Die Datei `karlsruhe_addresses.csv` kann für Adresssuche genutzt werden.  
    Format: Spalten `full_address`, `latitude`, `longitude`

---

## GTFS-Daten

> **Wichtig:**  
> Die GTFS-Daten (Ordner `gtfs/`) werden aus Platzgründen **nicht** mitgeliefert.  
> Bitte lade sie selbstständig von der offiziellen KVV-Seite herunter und lege sie im Projektordner ab.

---

## Nutzung

Das Programm wird über die Konsole gestartet:


Du wirst nach folgenden Angaben gefragt:
- Modus: `1` (Nur Bahn) oder `2` (Bus und Bahn)
- Start (Adresse oder Haltestelle)
- Ziel (Adresse oder Haltestelle)
- Startzeit (HH:MM oder HH:MM:SS, optional)

Das System gibt die gefundene Route mit allen Umstiegen und Zeiten aus.

---

## Beispiel

==================================================

Willkommen beim ÖPNV-Router Karlsruhe

==================================================

Geben Sie 1 (Nur Bahn) oder 2 (Bus und Bahn) ein: 2
Lade Adressdatensatz...
Adressdatensatz geladen.
Start (Adresse oder Haltestelle): Kirchfeld
Ziel (Adresse oder Haltestelle): Yorckstraße
Bitte Startzeit angeben (HH:MM) oder (HH:MM:SS): 17:30
Verwendete Startzeit: 17:30:00
Lade GTFS-Daten...
GTFS-Daten geladen.
Baue oder lade Transit-Graph...
Transit-Graph geladen.
Gefundene Route:
=== ROUTE ===

Richtung S1 Bad Herrenalb
17:45 Neureut Kirchfeld → 17:45 Neureut Adolf-Ehrmann-Bad

Richtung S1 Bad Herrenalb
17:46 Neureut Adolf-Ehrmann-Bad → 17:47 Neureut Bärenweg

...

=== GESAMT: 9 Haltestellen, Fahrtzeit: 13min, Ankunft um 17:58 ===

---

## Hinweise & Troubleshooting

- **GTFS-Daten** müssen lokal im Ordner `gtfs/` liegen.
- Beim ersten Start wird der Transit-Graph aus den GTFS-Daten gebaut und als `graph.pkl` gespeichert (Beschleunigung für Folgestarts).
- Für Adresssuche muss `karlsruhe_addresses.csv` vorhanden sein – ansonsten sind nur Haltestellen als Start/Ziel möglich.
- Bei Problemen mit der Haltestellenerkennung prüfe Schreibweise und nutze ggf. alternative Namen (z.B. `"Marktplatz (Kaiserstraße U)"`, `"KA Marktplatz (Kaiserstraße U)"`, `"Hauptbahnhof"`, `"Hbf"`).
- Für Fehlerberichte oder Featurewünsche bitte ein GitHub-Issue eröffnen.

---

## Lizenz

MIT License

---

**Viel Spaß beim Routing!**
