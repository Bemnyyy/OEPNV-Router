import gc
from datetime import datetime, time
from gtfs_processing import load_gtfs_data, build_transit_graph
from routing import plan_route_with_transfers, find_next_departure_time
from utils import is_stop_name, geocode_address, choose_stop, load_address_data, print_clean_route
from auto_choose import auto_choose_stop_direction_aware


# Beide funktionen zur Speicherverbrauch minimierung aufgrund von imensem Speicherverbrauch
def save_transit_graph(graph, filename='graph.pkl'):
    import pickle
    with open(filename, 'wb') as f:
        pickle.dump(graph, f)

def load_transit_graph(filename='graph.pkl'):
    import pickle
    import os
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    else:
        return None

def main():
    print("=" * 50)
    print("Willkommen beim ÖPNV-Router Karlsruhe")
    print("=" * 50)
    
    # Modusauswahl
    mode = input("Geben Sie 1 (Nur Bahn) oder 2 (Bus und Bahn) ein: ")
    mode = int(mode) if mode in ['1', '2'] else 2
    
    # Adressdatensatz laden
    print("Lade Adressdatensatz...")
    address_df = load_address_data()
    print("Adressdatensatz geladen.")
    
    # Benutzereingaben
    start_loc = input("Start (Haltestelle): ")
    end_loc = input("Ziel (Haltestelle): ")
    
    # Zeitangabe
    time_input = input("Bitte Startzeit angeben (HH:MM) oder (HH:MM:SS): ")
    try:
        if len(time_input.split(':')) == 2:
            t_obj = datetime.strptime(time_input, "%H:%M").time()
        else:
            t_obj = datetime.strptime(time_input, "%H:%M:%S").time()
    except ValueError:
        print("Ungültige Zeitangabe. Verwende 12:00:00.")
        t_obj = time(12, 0)
    
    routing_date = datetime(2024, 12, 16).date()
    routing_datetime = datetime.combine(routing_date, t_obj)

    print(f"Verwendete Startzeit: {t_obj}")
    
    # GTFS-Daten laden
    print("Lade GTFS-Daten...")
    gtfs = load_gtfs_data()
    print("GTFS-Daten geladen.")

    print("Routing-Datum:", routing_datetime.date())

    # Transit-Graph laden oder bauen
    print("Baue oder lade Transit-Graph...")
    transit_graph = load_transit_graph()
    if transit_graph is not None:
        print("Transit-Graph geladen.")
    else:
        print("Transit-Graph wird neu aufgebaut...")
        transit_graph = build_transit_graph(gtfs, mode=mode, routing_time=routing_datetime)
        save_transit_graph(transit_graph)
        print("Transit-Graph gespeichert.")
    
    
    # Speicher aufräumen
    collected = gc.collect()
    print(f"Garbage collector: collected {collected} objects.")
    
    # Validierung
    valid_stops = set(gtfs["stops"]["stop_id"])
    invalid_edges = [(u, v) for u, v in transit_graph.edges() if u not in valid_stops or v not in valid_stops]
    print(f"Anzahl ungültiger Kanten: {len(invalid_edges)}")

    # Start- und Zielhaltestelle bestimmen
    if is_stop_name(start_loc, gtfs['stops']) and is_stop_name(end_loc, gtfs['stops']):
        # Beide sind Haltestellen
        start_coord = None
        end_coord = None
        start_stop, end_stop, itinerary = auto_choose_stop_direction_aware(
            start_loc, end_loc, gtfs['stops'], transit_graph, t_obj, plan_route_with_transfers)
        
    else:
        # Einzelbehandlung für Start und Ziel
        if is_stop_name(start_loc, gtfs['stops']):
            start_coord = None
            start_stop = choose_stop(start_loc, gtfs['stops'])
        else:
            # Nur wenn es KEINE Haltestelle ist, als Adresse behandeln
            if not address_df.empty:
                start_coord, start_stop = geocode_address(start_loc, gtfs['stops'], address_df)
            else:
                print(f"Fehler: '{start_loc}' ist weder eine bekannte Haltestelle noch ist eine Adressdatenbank verfügbar.")
                return
        
        if is_stop_name(end_loc, gtfs['stops']):
            end_coord = None
            end_stop = choose_stop(end_loc, gtfs['stops'])
        else:
            # Nur wenn es KEINE Haltestelle ist, als Adresse behandeln
            if not address_df.empty:
                end_coord, end_stop = geocode_address(end_loc, gtfs['stops'], address_df)
            else:
                print(f"Fehler: '{end_loc}' ist weder eine bekannte Haltestelle noch ist eine Adressdatenbank verfügbar.")
                return
        
        itinerary = None
    
    # Routing durchführen
    if itinerary is None:
        print(f"Starte Routing von {start_stop} nach {end_stop} um {t_obj}")
        itinerary = plan_route_with_transfers(transit_graph, start_stop, end_stop, t_obj)
        if not itinerary:
            print("Keine Route zum gewünschten Zeitpunkt gefunden.")
            print("Suche spätere Abfahrten...")
            itinerary = find_next_departure_time(transit_graph, start_stop, end_stop, t_obj, search_hours=6)
    # Ergebnisse ausgeben
    if itinerary:
        print("Gefundene Route:")
        print_clean_route(itinerary, gtfs['stops'], gtfs)
    else:
        print("Keine Route gefunden.")

if __name__ == "__main__":
    main()