from datetime import datetime, timedelta
from collections import deque

def find_next_departure_time(G, start_stop, end_stop, dep_time, search_hours=6):    #G = ÖPNV-Netzwerk, start_stop = Start-Halte, end_stop = End-Halte, dep_time = Gewünschte Abfahrtszeit, search_hours = Wie lang (in Std.) maximal gesucht werden soll (Standard = 6)
    
    """
    Findet die nächste realistische Abfahrtszeit für eine Route
    """
    
    today = datetime.today().date()
    current_time = datetime.combine(today, dep_time)
    # Bis hier wird das heutige Datum genommen und mit der gewünschten Abfahrtszeit zu einem vollständigen "datetime"- Objekt kombiniert

    # Suche in 5-Minuten-Schritten
    for minutes in range(0, search_hours * 60, 5):      # Funktion sucht in 5-min schritten nach einer möglichen verbindung
        search_time = current_time + timedelta(minutes=minutes)
        route = plan_route_with_transfers_ignore_time(G, start_stop, end_stop, dep_time) #für jeden schritt wird die hauptrouting funktion (unten) aufgerufen
        
        #sobald route gefunden -> wird diese ausgegeben
        if route:
            print(f"Route gefunden mit Abfahrt um {search_time.strftime('%H:%M')}")
            return route
    
    return []   # Falls innerhalb des Suchzeitraums keine Route gefunden -> Funktion gibt leere Liste zurück


def plan_route_with_transfers_ignore_time(G, start_stop, end_stop, stops_df, max_transfers=4, max_depth=200):
    """
    Routenplanung mit Umstiegslogik OHNE Zeitangaben.
    Arbeitet rein topologisch (d.h. auf Basis von Haltestellen und Linienwechseln).
    Nutzt trip_id zur Umstiegsdetektion.
    """
    if start_stop not in G.nodes or end_stop not in G.nodes:
        return []

    queue = deque()
    queue.append((start_stop, None, 0, []))  # (aktuelle Haltestelle, letztes trip_id, Umstiege, Pfad)

    visited = set()  # (Haltestelle, trip_id)

    while queue:
        curr_stop, curr_trip, transfers, path = queue.popleft()

        if transfers > max_transfers or len(path) > max_depth:
            continue

        if curr_stop == end_stop:
            return path

        for next_stop, edge_data in G[curr_stop].items():
            next_trip = edge_data.get('trip_id')
            transfer_needed = curr_trip is not None and next_trip != curr_trip        
            new_transfers = transfers + 1 if transfer_needed else transfers
            #if curr_trip and next_trip and curr_trip != next_trip:
            #    if not is_same_station_area(curr_stop, next_stop, stops_df):
            #        continue

            state = (next_stop, next_trip)
            if state in visited:
                continue
            visited.add(state)

            leg = {
                'from_stop': curr_stop,
                'to_stop': next_stop,
                'route_name': edge_data.get('route_name', 'Unbekannt'),
                'direction': edge_data.get('direction', 'Unbekannt'),
                'trip_id': next_trip,
                'transfer': transfer_needed
            }

            queue.append((next_stop, next_trip, new_transfers, path + [leg]))

    return []
