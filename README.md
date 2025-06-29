ÖPNV-Router Karlsruhe
Routenplaner für den öffentlichen Nahverkehr in Karlsruhe
Dieses Python-Projekt ermöglicht es, Verbindungen im Karlsruher ÖPNV-Netz (Tram, Bus, Bahn) auf Basis von GTFS-Daten zu berechnen.

Features
Routing zwischen beliebigen Haltestellen oder Adressen

Unterstützung für Bus, Bahn, Tram (wahlweise)

Richtungsabhängige Haltestellenerkennung für zweigleisige Systeme

Umstiegsoptimierung und Zeitfenster-Suche

Fuzzy-Matching für Haltestellennamen

Übersichtliche Routenausgabe

Projektstruktur
Datei/Ordner	Beschreibung
main.py	Hauptprogramm, Einstiegspunkt
routing.py	Routing-Algorithmen (mit und ohne Umstieg)
auto_choose.py	Richtungsabhängige Haltestellenwahl
utils.py	Hilfsfunktionen: Matching, Geokodierung, Ausgabe
parent_station_utils.py	Funktionen für parent_station-Logik
gtfs_processing.py	Laden und Vorverarbeiten der GTFS-Daten
karlsruhe_addresses.csv	Adressdatenbank für Adresssuche (optional)
graph.pkl	Serialisierter Transit-Graph (wird beim ersten Start erzeugt)
Hinweis:
Die eigentlichen GTFS-Daten (Ordner gtfs/ mit stops.txt, routes.txt, trips.txt, stop_times.txt, calendar.txt, calendar_dates.txt etc.) sind aus Platzgründen nicht im Repository enthalten.

Installation
Repository klonen

bash
git clone https://github.com/DEIN-NAME/DEIN-REPO.git
cd DEIN-REPO
Abhängigkeiten installieren

bash
pip install -r requirements.txt
Benötigte Pakete (Beispiel):

pandas

numpy

networkx

rapidfuzz

GTFS-Daten herunterladen

Lade die GTFS-Daten für Karlsruhe (z.B. von kvv.de) herunter.

Entpacke alle Dateien (stops.txt, routes.txt, trips.txt, stop_times.txt, calendar.txt, calendar_dates.txt etc.) in einen Ordner gtfs/ im Projektverzeichnis.

(Optional) Adressdatenbank

Die Datei karlsruhe_addresses.csv kann für Adresssuche genutzt werden.
Format: Spalten full_address, latitude, longitude

Nutzung
Das Programm wird über die Konsole gestartet:

bash
python main.py
Du wirst nach folgenden Angaben gefragt:

Modus: 1 (Nur Bahn) oder 2 (Bus und Bahn)

Start (Adresse oder Haltestelle)

Ziel (Adresse oder Haltestelle)

Startzeit (HH:MM oder HH:MM:SS, optional)

Das System gibt die gefundene Route mit allen Umstiegen und Zeiten aus.

Hinweise
GTFS-Daten müssen lokal im Ordner gtfs/ liegen.

Beim ersten Start wird der Transit-Graph aus den GTFS-Daten gebaut und als graph.pkl gespeichert (Beschleunigung für Folgestarts).

Für Adresssuche muss karlsruhe_addresses.csv vorhanden sein – ansonsten sind nur Haltestellen als Start/Ziel möglich.

Bei Problemen mit der Haltestellenerkennung prüfe Schreibweise und nutze ggf. alternative Namen (z.B. "Marktplatz (Kaiserstraße U)", "KA Marktplatz (Kaiserstraße U)", "Hauptbahnhof", "Hbf").

Lizenz
Dieses Projekt steht unter der MIT-Lizenz.

Fragen oder Probleme?
Erstelle ein Issue im GitHub-Repository oder kontaktiere den Entwickler.

Hinweis:
Die GTFS-Daten dürfen aus lizenzrechtlichen und Speicherplatzgründen nicht im Repository bereitgestellt werden. Bitte lade sie selbstständig von der offiziellen KVV-Website herunter.
