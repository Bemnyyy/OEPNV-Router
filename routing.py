from datetime import timedelta


def find_next_departure_time(G, start_stop, end_stop, dep_time, search_hours=6):
    """
    Findet die nächste realistische Abfahrtszeit für eine Route
    """
    from datetime import datetime, timedelta
    
    today = datetime.today().date()
    current_time = datetime.combine(today, dep_time)
    
    # Suche in 30-Minuten-Schritten
    for minutes in range(0, search_hours * 60, 30):
        search_time = current_time + timedelta(minutes=minutes)
        route = plan_route_with_transfers(G, start_stop, end_stop, search_time.time())
        
        if route:
            print(f"Route gefunden mit Abfahrt um {search_time.strftime('%H:%M')}")
            return route
    
    return []

#
def plan_route_with_transfers(G, start_stop, end_stop, dep_time, max_transfers=2, max_total_duration=timedelta(hours=2)):
    import heapq
    from datetime import datetime, timedelta

    if start_stop not in G.nodes or end_stop not in G.nodes:
        return []

    today = datetime.today().date()
    start_datetime = datetime.combine(today, dep_time)
    counter = 0
    queue = [(start_datetime, counter, start_stop, None, 0, [])]
    visited = {}
    best_path = None
    best_arrival = None

    while queue:
        curr_time, _, curr_stop, curr_trip, transfers, path = heapq.heappop(queue)

        # Begrenzung der maximalen Gesamtreisezeit
        if (curr_time - start_datetime) > max_total_duration:
            continue

        # Prüfe, ob Ziel erreicht und kein Zyklus (Ziel nicht vorher im Pfad)
        if curr_stop == end_stop and (not path or path[-1]['to_stop'] != end_stop):
            # Prüfe, ob die Route direkt nach gewünschter Startzeit beginnt
            if path:
                first_departure = datetime.combine(today, datetime.strptime(path[0]['departure_time'], "%H:%M").time())
                if first_departure < start_datetime:
                    first_departure += timedelta(days=1)
                wait_time = (first_departure - start_datetime).total_seconds() / 60
                if wait_time > 30:
                    continue
            # Akzeptiere nur die Route mit frühester Ankunft
            if best_arrival is None or curr_time < best_arrival:
                best_arrival = curr_time
                best_path = path
            continue

        if transfers > max_transfers:
            continue

        state_key = (curr_stop, curr_trip)
        if state_key in visited and visited[state_key] <= curr_time:
            continue
        visited[state_key] = curr_time

        if curr_stop not in G:
            continue

        for next_stop, edge_data in G[curr_stop].items():
            next_trip = edge_data['trip_id']
            dep_time_edge = edge_data['departure_time']
            arr_time_edge = edge_data['arrival_time']
            dep_datetime = datetime.combine(today, dep_time_edge)
            arr_datetime = datetime.combine(today, arr_time_edge)
            if dep_datetime < curr_time:
                dep_datetime += timedelta(days=1)
                arr_datetime += timedelta(days=1)
            if dep_datetime < curr_time:
                continue

            # Zyklus-Prüfung: Ziel darf nicht erneut im Pfad vorkommen
            if next_stop == end_stop and any(leg['to_stop'] == end_stop for leg in path):
                continue

            transfer_needed = (curr_trip is not None and curr_trip != next_trip)
            new_transfers = transfers + (1 if transfer_needed else 0)
            if transfer_needed:
                min_departure = curr_time + timedelta(minutes=10)
                if dep_datetime < min_departure:
                    continue

            new_path = path + [{
                "from_stop": curr_stop,
                "to_stop": next_stop,
                "departure_time": dep_time_edge.strftime("%H:%M"),
                "arrival_time": arr_time_edge.strftime("%H:%M"),
                "route_name": edge_data['route_name'],
                "direction": edge_data['direction'],
                "trip_id": next_trip,
                "transfer": transfer_needed
            }]
            counter += 1
            heapq.heappush(queue, (arr_datetime, counter, next_stop, next_trip, new_transfers, new_path))

    return best_path if best_path else []


def plan_route_extended_transfers(G, start_stop, end_stop, dep_time, max_transfers=4, search_hours=8):
    """
    Erweiterte Umstiegs-Funktion für schwierige Routen
    """
    import heapq
    from datetime import datetime, timedelta
    
    if start_stop not in G.nodes or end_stop not in G.nodes:
        return []
    
    today = datetime.today().date()
    start_datetime = datetime.combine(today, dep_time)
    end_datetime = start_datetime + timedelta(hours=search_hours)
    
    counter = 0
    queue = [(start_datetime, counter, start_stop, None, 0, [])]
    visited = {}
    
    while queue:
        curr_time, _, curr_stop, curr_trip, transfers, path = heapq.heappop(queue)
        
        if curr_time > end_datetime:
            continue
            
        if curr_stop == end_stop:
            print(f"Ziel erreicht um {curr_time.strftime('%H:%M')} mit {transfers} Umstiegen")
            return path
        
        if transfers > max_transfers:
            continue
        
        state_key = (curr_stop, curr_trip)
        if state_key in visited and visited[state_key] <= curr_time:
            continue
        visited[state_key] = curr_time
        
        if curr_stop not in G:
            continue
        
        for next_stop, edge_data in G[curr_stop].items():
            next_trip = edge_data['trip_id']
            dep_time_edge = edge_data['departure_time']
            arr_time_edge = edge_data['arrival_time']
            
            dep_datetime = datetime.combine(today, dep_time_edge)
            arr_datetime = datetime.combine(today, arr_time_edge)
            
            # Behandle Zeiten über Mitternacht
            if dep_datetime < curr_time:
                dep_datetime += timedelta(days=1)
                arr_datetime += timedelta(days=1)
            
            if dep_datetime < curr_time or dep_datetime > end_datetime:
                continue
            
            transfer_needed = (curr_trip is not None and curr_trip != next_trip)
            new_transfers = transfers + (1 if transfer_needed else 0)
            
            if transfer_needed:
                min_departure = curr_time + timedelta(minutes=10)
                if dep_datetime < min_departure:
                    continue
            
            new_path = path + [{
                "from_stop": curr_stop,
                "to_stop": next_stop,
                "departure_time": dep_time_edge.strftime("%H:%M"),
                "arrival_time": arr_time_edge.strftime("%H:%M"),
                "route_name": edge_data['route_name'],
                "direction": edge_data['direction'],
                "trip_id": next_trip,
                "transfer": transfer_needed
            }]
            
            counter += 1
            heapq.heappush(queue, (arr_datetime, counter, next_stop, next_trip, new_transfers, new_path))
    
    return []
