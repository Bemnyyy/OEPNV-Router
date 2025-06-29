import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rapidfuzz import process, fuzz

def is_stop_name(name, stops_df):
    """
    Prüft, ob ein gegebener Name in der stops DataFrame als Haltestelle existiert.
    Sucht sowohl nach exakten Übereinstimmungen als auch nach Teilstrings.
    """
    name_lower = name.lower()
    stop_names_lower = stops_df['stop_name'].str.lower()
    
    # 1. Exakte Übereinstimmung
    if name_lower in stop_names_lower.values:
        return True
    
    # 2. Teilstring-Suche (WICHTIG: regex=False für Klammern!)
    if stop_names_lower.str.contains(name_lower, na=False, regex=False).any():
        return True
    
    # 3. Fuzzy-Matching für häufige Varianten
    common_mappings = {
    'hauptbahnhof': ['hauptbahnhof', 'hbf'],
    'hbf': ['hauptbahnhof', 'hbf'],
    'marktplatz': ['marktplatz', 'marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u', 'marktplatz (pyramide)', 'marktplatz (pyramide) u'],
    'marktplatz (kaiserstraße u)': ['marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u'],
    'ka marktplatz (kaiserstraße u)': ['marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u'],
    }

    
    if name_lower in common_mappings:
        for variant in common_mappings[name_lower]:
            if stop_names_lower.str.contains(variant, na=False, regex=False).any():
                return True
    
    return False

def load_address_data(filename='karlsruhe_addresses.csv'):
    """
    Lädt den Adressdatensatz aus einer CSV-Datei.
    """
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"Adressdatei {filename} nicht gefunden.")
        return pd.DataFrame()

def find_address_coords(address, address_df):
    """
    Findet die Koordinaten für eine Adresse im Adressdatensatz.
    """
    if address_df.empty or 'full_address' not in address_df.columns:
        raise ValueError(f"Adressdatenbank ist leer oder hat keine 'address'-Spalte.")
    
    matches = address_df[address_df['full_address'].str.lower() == address.lower()]
    if not matches.empty:
        lat = matches.iloc[0]['latitude']
        lon = matches.iloc[0]['longitude']
        return lat, lon
    else:
        raise ValueError(f"Adresse '{address}' nicht in der Adressdatenbank gefunden.")

def haversine(lat1, lon1, lat2, lon2):
    # Radius der Erde in km
    R = 6371.0
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def geocode_address(address, stops_df, address_df):
    """
    Geokodiert Adresse und findet die nächste Haltestelle nach Entfernung.
    """
    if address_df.empty:
        raise ValueError("Keine Adressdatenbank verfügbar.")
    coords = find_address_coords(address, address_df)
    if not stops_df.empty and 'stop_lat' in stops_df.columns and 'stop_lon' in stops_df.columns:
        stops_df = stops_df.dropna(subset=['stop_lat', 'stop_lon'])
        stops_df['dist'] = stops_df.apply(
            lambda row: haversine(coords[0], coords[1], row['stop_lat'], row['stop_lon']), axis=1)
        nearest_stop = stops_df.loc[stops_df['dist'].idxmin()]['stop_id']
        return coords, nearest_stop
    else:
        return coords, None
'''
def choose_stop(name, stops_df, min_score=80):
    """
    Erweiterte Haltestellenauswahl mit Fuzzy-Matching (RapidFuzz).
    """
    name_lower = name.lower()
    stop_names = stops_df['stop_name'].astype(str)

    # 1. Exakte Übereinstimmung
    exact_matches = stops_df[stop_names.str.lower() == name_lower]
    if not exact_matches.empty:
        return exact_matches.iloc[0]['stop_id']

    # 2. Teilstring-Suche
    partial_matches = stops_df[stop_names.str.lower().str.contains(name_lower, na=False, regex=False)]
    if not partial_matches.empty:
        # Bevorzuge kürzere Namen (wahrscheinlich Haupthaltestelle)
        partial_matches = partial_matches.copy()
        partial_matches['name_length'] = partial_matches['stop_name'].str.len()
        best_match = partial_matches.loc[partial_matches['name_length'].idxmin()]
        print(f"Gefundene Haltestelle: '{best_match['stop_name']}' für Eingabe '{name}'")
        return best_match['stop_id']

    # 3. Fuzzy-Matching mit RapidFuzz
    choices = stop_names.tolist()
    result = process.extractOne(name, choices, scorer=fuzz.WRatio)
    if result and result[1] >= min_score:
        best_name = result[0]
        best_row = stops_df[stop_names == best_name]
        if not best_row.empty:
            print(f"Fuzzy-Match: '{best_name}' (Score: {result[1]}) für Eingabe '{name}'")
            return best_row.iloc[0]['stop_id']

    raise ValueError(f"Keine Haltestelle mit Namen ähnlich zu '{name}' gefunden.")
'''
'''
def choose_stop(name, stops_df, min_score=75):
    name_lower = name.lower()
    stop_names = stops_df['stop_name'].astype(str)
    # Exakte Übereinstimmung
    exact_matches = stops_df[stop_names.str.lower() == name_lower]
    if not exact_matches.empty:
        return exact_matches.iloc[0]['stop_id']
    # Mapping-Varianten
    common_mappings = {
    'hauptbahnhof': ['hauptbahnhof', 'hbf'],
    'hbf': ['hauptbahnhof', 'hbf'],
    'marktplatz': ['marktplatz', 'marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u', 'marktplatz (pyramide)', 'marktplatz (pyramide) u'],
    'marktplatz (kaiserstraße u)': ['marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u'],
    'ka marktplatz (kaiserstraße u)': ['marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u'],
    }
    if name_lower in common_mappings:
        for variant in common_mappings[name_lower]:
            partial_matches = stops_df[stop_names.str.lower().str.contains(variant, na=False, regex=False)]
            if not partial_matches.empty:
                return partial_matches.iloc[0]['stop_id']
    # Teilstring/Fuzzy
    partial_matches = stops_df[stop_names.str.lower().str.contains(name_lower, na=False, regex=False)]
    if not partial_matches.empty:
        return partial_matches.iloc[0]['stop_id']
    # Fuzzy
    from rapidfuzz import process, fuzz
    choices = stop_names.tolist()
    result = process.extractOne(name, choices, scorer=fuzz.WRatio)
    if result and result[1] >= min_score:
        best_name = result[0]
        best_row = stops_df[stop_names == best_name]
        if not best_row.empty:
            return best_row.iloc[0]['stop_id']
    raise ValueError(f"Keine Haltestelle mit Namen ähnlich zu '{name}' gefunden.")
'''

def choose_stop(name, stops_df, min_score=70):
    name_lower = name.lower().strip()
    stop_names = stops_df['stop_name'].astype(str)
    stop_names_lower = stop_names.str.lower().str.strip()

    # 1. Exakte Übereinstimmung
    exact_matches = stops_df[stop_names_lower == name_lower]
    if not exact_matches.empty:
        print(f"[MATCH] Exakt: {exact_matches.iloc[0]['stop_name']}")
        return exact_matches.iloc[0]['stop_id']

    # 2. Mapping-Varianten
    common_mappings = {
        'marktplatz': ['marktplatz', 'marktplatz (kaiserstraße)', 'marktplatz (kaiserstraße) u', 'ka marktplatz (kaiserstraße u)', 'marktplatz (pyramide)', 'ka marktplatz (pyramide) u'],
        'ettlinger tor': ['ettlinger tor', 'ka ettlinger tor/staatstheater (u)', 'ettlinger tor/staatstheater (u)'],
        'entenfang': ['entenfang', 'ka entenfang'],
        # weitere mappings...
    }
    if name_lower in common_mappings:
        for variant in common_mappings[name_lower]:
            partial_matches = stops_df[stop_names_lower.str.contains(variant, na=False, regex=False)]
            if not partial_matches.empty:
                print(f"[MATCH] Mapping: {partial_matches.iloc[0]['stop_name']}")
                return partial_matches.iloc[0]['stop_id']

    # 3. Teilstring-Suche
    partial_matches = stops_df[stop_names_lower.str.contains(name_lower, na=False, regex=False)]
    if not partial_matches.empty:
        print(f"[MATCH] Teilstring: {partial_matches.iloc[0]['stop_name']}")
        return partial_matches.iloc[0]['stop_id']

    # 4. Fuzzy-Matching
    from rapidfuzz import process, fuzz
    choices = stop_names.tolist()
    result = process.extractOne(name, choices, scorer=fuzz.WRatio)
    if result and result[1] >= min_score:
        best_name = result[0]
        best_row = stops_df[stop_names == best_name]
        if not best_row.empty:
            print(f"[MATCH] Fuzzy: '{best_name}' (Score: {result[1]}) für Eingabe '{name}'")
            return best_row.iloc[0]['stop_id']

    print(f"[WARN] Keine Haltestelle mit Namen ähnlich zu '{name}' gefunden.")
    raise ValueError(f"Keine Haltestelle mit Namen ähnlich zu '{name}' gefunden.")

    
def get_opposite_direction_stop_id(stop_id):
    """
    Findet die stop_id für die Gegenrichtung
    """
    if stop_id.endswith(":1:1"):
        return stop_id.replace(":1:1", ":2:2")
    elif stop_id.endswith(":2:2"):
        return stop_id.replace(":2:2", ":1:1")
    elif stop_id.endswith(":1:2"):
        return stop_id.replace(":1:2", ":2:1")
    elif stop_id.endswith(":2:1"):
        return stop_id.replace(":2:1", ":1:2")
    return stop_id

def get_all_direction_variants(stop_id):
    """
    Gibt alle möglichen Richtungsvarianten einer stop_id zurück
    """
    base_id = stop_id.rsplit(":", 2)[0]  # Entfernt die letzten beiden Teile
    variants = [
        f"{base_id}:1:1",
        f"{base_id}:1:2", 
        f"{base_id}:2:1",
        f"{base_id}:2:2"
    ]
    return variants

def print_clean_route(itinerary, stops_df, gtfs=None):
    """
    Saubere, übersichtliche Routenausgabe mit Linien- und Richtungsinformationen
    """
    if not itinerary:
        print("Keine Route gefunden.")
        return
    
    print("=== ROUTE ===")
    current_trip = None
    segment_count = 0
    
    for leg in itinerary:
        trip_id = leg.get('trip_id', '')
        route_name = leg.get('route_name', 'Unbekannt')
        direction = leg.get('direction', 'Unbekannt')
        
        # Verbesserte Linien- und Richtungsinformation
        line_info = get_enhanced_line_info(trip_id, direction, gtfs, route_name)
        
        # Umstieg erkannt
        if current_trip and current_trip != trip_id:
            print(f"  → UMSTIEG")
        
        current_trip = trip_id
        segment_count += 1
        
        from_name = stop_id_to_name(leg['from_stop'], stops_df)
        to_name = stop_id_to_name(leg['to_stop'], stops_df)
        
        print(f"{segment_count:2d}. {line_info}")
        print(f"    {leg['departure_time']} {from_name} → {format_time_with_day_hint(leg['departure_time'], leg['arrival_time'])} {to_name}")


    # Gesamtzeit berechnen
    start_time = itinerary[0]['departure_time']
    end_time = itinerary[-1]['arrival_time']
    total_time = calculate_travel_time(start_time, end_time)
    
    print(f"=== GESAMT: {len(itinerary)} Haltestellen, Fahrtzeit: {total_time}, Ankunft um {end_time} ===")

def get_enhanced_line_info(trip_id, direction, gtfs, route_name):
    """
    Extrahiert verbesserte Linien- und Richtungsinformationen
    """
    # Fallback-Werte bereinigen
    if route_name in ['nan', 'Unbekannt', None] or str(route_name) == 'nan':
        route_name = None
    if direction in ['nan', 'Unbekannt', None] or str(direction) == 'nan':
        direction = None
    
    # Versuche Informationen aus GTFS-Daten zu extrahieren
    if gtfs and trip_id:
        try:
            # Hole Trip-Informationen
            trip_info = gtfs['trips'][gtfs['trips']['trip_id'] == trip_id]
            if not trip_info.empty:
                trip_row = trip_info.iloc[0]
                
                # Hole Route-Informationen
                route_id = trip_row.get('route_id')
                if route_id:
                    route_info = gtfs['routes'][gtfs['routes']['route_id'] == route_id]
                    if not route_info.empty:
                        route_row = route_info.iloc[0]
                        
                        # Bevorzuge route_short_name, dann route_long_name
                        if not route_name:
                            route_name = route_row.get('route_short_name') or route_row.get('route_long_name')
                
                # Hole Richtung aus trip_headsign
                if not direction:
                    direction = trip_row.get('trip_headsign')
        except Exception as e:
            print(f"Debug: Fehler beim Extrahieren der Linieninfo: {e}")
    
    # Formatiere die Ausgabe
    line_part = f"Linie {route_name}" if route_name else "Unbekannte Linie"
    direction_part = f"Richtung {direction}" if direction else "Richtung unbekannt"
    
    return f"{direction_part}"

def calculate_travel_time(start_time_str, end_time_str):
    """
    Berechnet die Fahrtzeit zwischen zwei Zeitpunkten
    """
    from datetime import datetime, timedelta
    
    try:
        start = datetime.strptime(start_time_str, "%H:%M")
        end = datetime.strptime(end_time_str, "%H:%M")
        
        # Behandle Tagesübergang
        if end < start:
            end += timedelta(days=1)
        
        diff = end - start
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}min"
        else:
            return f"{minutes}min"
    except:
        return "unbekannt"

def stop_id_to_name(stop_id, stops_df):
    """
    Gibt den Haltestellennamen für eine gegebene stop_id zurück.
    """
    row = stops_df[stops_df['stop_id'] == stop_id]
    if not row.empty:
        return row.iloc[0]['stop_name']
    else:
        return f"Unbekannte Haltestelle ({stop_id})"
    
def format_time_with_day_hint(start_time, end_time):
    start_dt = datetime.strptime(start_time, "%H:%M")
    end_dt = datetime.strptime(end_time, "%H:%M")
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
        return end_dt.strftime("%H:%M") + " (+1 Tag)"
    else:
        return end_dt.strftime("%H:%M")

def get_valid_service_ids(calendar_df, date):
    weekday = date.strftime('%A').lower()
    valid_services = calendar_df[
        (calendar_df[weekday] == 1) &
        (calendar_df['start_date'] <= date) &
        (calendar_df['end_date'] >= date)
    ]['service_id'].tolist()
    
    return valid_services
