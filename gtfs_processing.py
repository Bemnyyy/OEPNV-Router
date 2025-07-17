import pandas as pd
import networkx as nx
from utils import get_valid_service_ids

# Lädt alle gtfs daten
def load_gtfs_data(gtfs_folder='gtfs'):
    gtfs = {}
    try:
        gtfs['stops'] = pd.read_csv(f'{gtfs_folder}/stops.txt')
        gtfs['routes'] = pd.read_csv(f'{gtfs_folder}/routes.txt')
        gtfs['trips'] = pd.read_csv(f'{gtfs_folder}/trips.txt')
        gtfs['stop_times'] = pd.read_csv(f'{gtfs_folder}/stop_times.txt', low_memory=False)
        gtfs['calendar'] = pd.read_csv(f'{gtfs_folder}/calendar.txt', encoding='utf-8-sig')
        gtfs['calendar_dates'] = pd.read_csv(f'{gtfs_folder}/calendar_dates.txt')
        # Für check in calendar, ob die tage dem inhalt der gtfs entsprechen
        for day in ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']:
            gtfs['calendar'][day] = gtfs['calendar'][day].astype(int)
        gtfs['calendar']['start_date'] = pd.to_datetime(gtfs['calendar']['start_date'], format='%Y%m%d').dt.date
        gtfs['calendar']['end_date'] = pd.to_datetime(gtfs['calendar']['end_date'], format='%Y%m%d').dt.date
    except FileNotFoundError as e:
        print(f'Fehler beim Laden der GTFS-Daten: {e}')
        gtfs = {}
    return gtfs

# Hintergrund für folgende Funktion:
''' Im GTFS-Standard werden ggf. Abfahrts- und Ankunftszeiten als 24:01:00 oder 25:15:00 angegeben
Dies wird durch die Funktion behoben, denn Python akzeptiert max. nur 23:59:59'''
def parse_time_with_correction(time_series):
    """
    Korrigiert GTFS-Zeiten wie '24:01:00' zu '00:01:00' und parst sie zu time-Objekten.
    """
    corrected_times = []
    for t in time_series:
        if isinstance(t, str):
            # Korrigiere Zeiten >= 24:00:00
            if t.startswith('24:'):
                corrected = '00' + t[2:]
            elif t.startswith('25:'):
                corrected = '01' + t[2:]
            elif t.startswith('26:'):
                corrected = '02' + t[2:]
            elif t.startswith('27:'):
                corrected = '03' + t[2:]
            else:
                corrected = t
            corrected_times.append(corrected)
        else:
            corrected_times.append(t)
    # Schleife über alle Einträge in der Eingabeliste
    # Falls Eintrag ein string ist:
    '''     - "24:" wird zu "00:..."
            - "25:" wird zu "01:..."
            usw...
    alle anderen zeiten bleiben gleich
    '''

    # Parse mit Fehlerbehandlung
    try:
        parsed = pd.to_datetime(corrected_times, format='%H:%M:%S', errors='coerce') # Wandelt die Strings in datetime-Objekte um
        return [pd.NaT if pd.isna(x) else x.time() for x in parsed]
    except Exception as e:  # Fehlerbehandlung
        print(f"Fehler beim Zeitparsing: {e}")
        return [None] * len(corrected_times)


# Netzwerk aufbau (wichtigste Funktion), dient dazu das im hintergrund stehende ÖPNV-Netzwerk aufzubauen
def build_transit_graph(gtfs, routing_time=None):
    """
    Baut den Transit-Graphen aus GTFS-Daten.
    """
    # Prüfe, ob GTFS-Daten vollständig geladen wurden
    required_keys = ['stops', 'routes', 'trips', 'stop_times']
    for key in required_keys:
        if key not in gtfs or gtfs[key].empty:
            print(f"Fehler: GTFS-Daten unvollständig. '{key}' fehlt oder ist leer.")
            return nx.DiGraph()
    
    G = nx.DiGraph()
    
    # Knoten hinzufügen (alle Haltestellen) -> Haltestelle wird als Knoten MIT Name hinzugefügt
    for _, stop in gtfs["stops"].iterrows():
        G.add_node(stop["stop_id"], name=stop["stop_name"])
    
    # Gültige Stops definieren -> Alle gültigen Haltestellen IDs werden in einer Menge gespeichert
    valid_stops = set(gtfs["stops"]["stop_id"])
    
    # Filtere Trips nach gültigen service_ids für das Routing-Datum
    # Es werden nur Fahrten (Trips) und Stopzeiten berücksichtigt die am gewünschten Tag verkehren
    # get_valid_service_ids muss hierfür korrekt implementiert sein -> könnten sonst zu viel oder zu wenig Fahrten übrig bleiben
    if routing_time is not None:
        valid_services = get_valid_service_ids(gtfs['calendar'], routing_time.date())
        gtfs['trips'] = gtfs['trips'][gtfs['trips']['service_id'].isin(valid_services)]
        #stop_times direkt mitfiltern wegen Speicher
        gtfs['stop_times'] = gtfs['stop_times'][gtfs['stop_times']['trip_id'].isin(gtfs['trips']['trip_id'])]

    # Merge stop_times mit trips und routes -> Die Stopzeiten werden mit den Fahrten und Routen zusammengeführt, sodass alle nötigen Infos in einer Tabelle stehen
    merged = gtfs["stop_times"].merge(gtfs["trips"], on="trip_id")
    merged = merged.merge(gtfs["routes"], on="route_id")
    
    # Trips filtern: Start und Ende müssen im Karlsruher Netz sein
    trip_start_end = merged.groupby("trip_id")["stop_id"].agg(["first", "last"])
    valid_trips = trip_start_end[
        (trip_start_end["first"].isin(valid_stops)) & 
        (trip_start_end["last"].isin(valid_stops))
    ].index
    # Mögliche Fehlerquelle: Wenn ein Trip außerhalb des Netzes startet/endet, wird er ausgeschlossen -> eig. gewollt, kann aber zu Lücken führen

    #valid_trip_ids = gtfs['trips'][gtfs['trips']['service_id'].isin(valid_services)]['trip_id']

    merged = merged[merged["trip_id"].isin(valid_trips)]
    # Es verbleiben nur die Zeilen mit gültigen Trips

    # Zeitkonvertierung mit Behandlung von 24:xx:xx Zeiten 
    print("Konvertiere Ankunftszeiten...")
    merged["arrival_time"] = parse_time_with_correction(merged["arrival_time"])
    print("Konvertiere Abfahrtszeiten...")
    merged["departure_time"] = parse_time_with_correction(merged["departure_time"])
    
    # Entferne Zeilen mit ungültigen Zeiten
    merged = merged.dropna(subset=['arrival_time', 'departure_time'])
    
    # Kanten zwischen aufeinanderfolgenden Stopps eines Trips
    for trip_id, group in merged.groupby("trip_id"):
        group['stop_sequence'] = pd.to_numeric(group['stop_sequence'], errors='coerce')
        group = group.dropna(subset=['stop_sequence'])
        group = group.sort_values("stop_sequence")
        
        for i in range(1, len(group)):
            prev = group.iloc[i-1]
            curr = group.iloc[i]
            
            if prev.stop_id in valid_stops and curr.stop_id in valid_stops:
                
                route_name = curr.get('route_long_name') or curr.get('route_short_name') or "Unbekannt"                
                #if pd.isna(route_name) or not route_name:
                #    route_name = "Linienrichtung nicht gefunden, bitte Aushangfahrplan beachten"               
                
                direction = curr.get('stop_headsign') or curr.get('trip_headsign') or "Unbekannt"
                if pd.isna(direction) or not direction:
                    direction = "Fahrtrichtungsdaten konnten nicht geladen werden, bitte informieren Sie sich an den Aushangfahrplänen an den Haltestellen"

                G.add_edge(
                    prev.stop_id,
                    curr.stop_id,
                    departure_time=prev.departure_time,
                    arrival_time=curr.arrival_time,
                    route_name=route_name,
                    direction=direction,
                    trip_id=trip_id
                )
    # ==> Für jede Fahrt (Trip) werden die Stopps nach Reihenfolge sortiert
    # Zwischen jedem aufeinanderfolgenden Stopp wird eine Kante im Graphen angelegt -> mit relevanten Fahrplandaten als Attributen
    # Attribute werden in der klammer definiert G.add_edge(...)

    # Kurze Ausgabe um zu erkennen wie viele Knoten und Kanten erstellt worden sind
    # Dies sollten theoretisch >1000 sein
    print(f"Transit-Graph erstellt: {G.number_of_nodes()} Knoten, {G.number_of_edges()} Kanten")
    return G    #Gibt dann schlussendlich den Graphen zurück