from parent_station_utils import get_all_stop_ids_for_station
from routing import plan_route_with_transfers_ignore_time #plan_route_with_transfers, plan_route_extended_transfers
from typing import Any, NoReturn

def auto_choose_stop_direction_aware(start_name, end_name, stops_df, transit_graph, start_stop, end_stop, gtfs) -> tuple[str, str, list[dict[str, Any]]]:
    # start_name und end_name = Name der Start und End halten (Strings)
    # stops_df = DataFrame mit Haltestellen Daten
    # transit_graph = Transit Graph aus build_transit_graph
    # t_obj = Zeitobjekt -> Abfahrtszeit für die Routenplanung
    # Rückgabe eines Tupels (start_stop_id, end_stop_id, itinierary), itinerary = Liste mit Verbindugsabschnitten
    """
    Richtungsabhängige stop_id-Auswahl für zweigleisige Systeme
    """
    # Alle stop_ids für beide Haltestellen -> Findet Haltestellen deren Namen den Suchtstring enthalten
    start_matches = stops_df[stops_df['stop_name'].str.lower().str.contains(start_name.lower(), na=False, regex=False)]
    end_matches = stops_df[stops_df['stop_name'].str.lower().str.contains(end_name.lower(), na=False, regex=False)]
    
    # Filtere Ersatzhalte aus
    start_regular = start_matches[~start_matches['stop_name'].str.contains('Ersatz', na=False)]
    end_regular = end_matches[~end_matches['stop_name'].str.contains('Ersatz', na=False)]
    
    if start_regular.empty:
        start_regular = start_matches
    if end_regular.empty:
        end_regular = end_matches
    
    # Für jede gefundene haltestelle werden alle zugehörigen Stop_ids ermittelt, doppelte ids werden mit set() entfernt
    start_ids = []
    for s in start_regular['stop_id']:
        start_ids.extend(get_all_stop_ids_for_station(stops_df, s))
    end_ids = []
    for e in end_regular['stop_id']:
        end_ids.extend(get_all_stop_ids_for_station(stops_df, e))
    start_ids = list(set(start_ids))
    end_ids = list(set(end_ids))
    
    # Gruppiere stop_ids nach Richtung -> mögl. Fehlerquelle: ist mehr oder weniger hardcode aber sollte mit den kvv gtfs daten funktionieren
    def get_direction_groups(stop_ids):
        groups = {"direction_1": [], "direction_2": [], "other": []}
        for stop_id in stop_ids:
            if stop_id.endswith(":1:1") or stop_id.endswith(":1:2"):
                groups["direction_1"].append(stop_id)
            elif stop_id.endswith(":2:2") or stop_id.endswith(":2:1"):
                groups["direction_2"].append(stop_id)
            else:
                groups["other"].append(stop_id)
        return groups
    
    start_groups = get_direction_groups(start_ids)
    end_groups = get_direction_groups(end_ids)
    
    
    # Teste verschiedene Richtungskombinationen
    test_combinations = [
        # Gleiche Richtung
        (start_groups["direction_1"], end_groups["direction_1"], "Richtung 1 -> 1"),
        (start_groups["direction_2"], end_groups["direction_2"], "Richtung 2 -> 2"),
        # Kreuzrichtungen
        (start_groups["direction_1"], end_groups["direction_2"], "Richtung 1 -> 2"),
        (start_groups["direction_2"], end_groups["direction_1"], "Richtung 2 -> 1"),
        # Fallback: alle anderen
        (start_groups["other"], end_groups["other"], "Andere"),
        # Notfall: alle Kombinationen
        (start_ids, end_ids, "Alle Kombinationen")
    ]
    
    # Für jede Kombi von Start und Ziel IDs wird versucht eine Route zu planen
    for start_list, end_list, beschreibung in test_combinations:
        for s in start_list:
            for e in end_list:
                # Zuerst einfache Umstiegs-Funktion probieren
                itinerary = plan_route_with_transfers_ignore_time(transit_graph, s, e, gtfs['stops'])


                # Falls das nicht funktioniert, erweiterte Version probieren
                if not itinerary:
                    itinerary = plan_route_with_transfers_ignore_time(transit_graph, s, e, gtfs['stops'])


                # Falls immer noch nichts gefunden, auf leere Liste setzen
                if itinerary is None:
                    itinerary = []
                # Erfolg: Rückgabe
                if itinerary:
                    print(f"  ERFOLG!")
                    return s, e, itinerary

    return ("", "", [])



def raise_no_return_error() -> NoReturn:
       raise ValueError("Keine Route mit richtungsabhängiger Suche gefunden.") 