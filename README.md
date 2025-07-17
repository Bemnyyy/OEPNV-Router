# ÖPNV-Router Karlsruhe

Interaktiver Routenplaner für den öffentlichen Nahverkehr in und um Karlsruhe. Nutzt GTFS-Daten, um optimale Verbindungen zwischen Adressen oder Haltestellen zu berechnen.

## Features

- **Intuitive GUI** mit Start- und Zielauswahl  
- **Schnelles Backend** mit Multithreading (keine "hängenbleibende" Oberfläche)  
- **Flexible Eingabe**: Adresse oder Haltestellenname  
- **Automatische Umstiegslogik**  
- **Kartenansicht der Route (Folium)**  
- **Plattformübergreifend:** Windows, macOS, Linux

## Quickstart

**Schritt 1:** Repository klonen

**Schritt 2:** GTFS-Daten herunterladen  
Die aktuellen GTFS-Daten des KVV **dürfen nicht** im Repository liegen, sondern müssen manuell geladen werden:  
[Zu den GTFS-Daten von KVV](https://www.kvv.de/fahrplan/fahrplaene/open-data.html)  

**Schritt 3:** GTFS-Daten entpacken  
Lege alle `.txt`-Dateien in einen Unterordner `gtfs/` (z.B. `gtfs/stops.txt`, `gtfs/routes.txt`, ...).

**Schritt 4:** Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Schritt 5:** Anwendung starten

```bash
python main.py
```

## Ordnerstruktur

| Datei/Ordner              | Beschreibung                                                      |
|---------------------------|-------------------------------------------------------------------|
| `main.py`                 | Startpunkt & Haupt-GUI der Anwendung                              |
| `gtfs_processing.py`      | Laden und Verarbeiten der GTFS-Daten                              |
| `routing.py`              | Routenplanung und Umstiegslogik                                   |
| `auto_choose.py`          | Richtungslogik & automatische Haltestellenauswahl                 |
| `parent_station_utils.py` | Utilities für Umsteigestationen                                   |
| `utils.py`                | Hilfsfunktionen (Geocoding, Parsing, Adressdaten etc.)            |
| `visualize_route.py`      | Interaktive Kartenvisualisierung der Route                        |
| `karlsruhe_addresses.csv` | Adressdatensatz für Geokodierung                                  |
| `requirements.txt`        | Abhängigkeiten                                                    |

> **Hinweis:**  
> GTFS-Daten müssen aus lizenzrechtlichen und Speichergründen extern geladen werden.

## Externe Daten

- **GTFS-Daten für Karlsruhe:**  
  [https://www.kvv.de/fahrplan/fahrplaene/open-data.html](https://www.kvv.de/fahrplan/fahrplaene/open-data.html)

  Nach dem Download:
  - Entpacke alles in den Ordner `gtfs/` innerhalb dieses Repositories

## Voraussetzungen

- Python 3.8 oder neuer
- Notwendige Pakete siehe `requirements.txt`

## Bedienungsanleitung

1. Starte das Programm mit `python main.py`
2. Trage Start und Ziel (Haltestelle oder Adresse) ein
3. Klicke auf **Route suchen**
4. Die optimale Verbindung erscheint im Ergebnisfeld
5. Mit **Karte anzeigen** wird die Route im Browser visualisiert

## Hinweise

- Erstsuche kann ein paar Sekunden dauern (Daten werden geladen und geparst)
- Adressdaten in `karlsruhe_addresses.csv` können erweitert werden

## Lizenz

MIT-Lizenz.  
Die verwendeten GTFS-Daten unterliegen den Nutzungsbedingungen des KVV.

*Viel Spaß beim Erkunden des Karlsruher Nahverkehrs!*

[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/a0bf6848-ee7a-4966-bc70-d3fcd0771bc0/main.py
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/1b07f70e-3b0e-4403-b548-2be79a70689c/parent_station_utils.py
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/5787a14c-a025-493d-b558-0d7fc96be274/routing.py
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/09f95b05-f6a7-46a5-8a41-0b15dd18c1fe/utils.py
[5] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/03053968-101f-4c71-b540-ff1235ff5fae/visualize_route.py
[6] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/d45f9d3b-d16f-45f0-8f4f-b850271cd2d3/gtfs_processing.py
[7] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/58544092/ba474e71-7626-4e6b-8503-ffc1152607eb/auto_choose.py
