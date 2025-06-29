import folium

def visualize_route(itinerary, stops_df, filename="route_map.html"):
    """
    Visualisiert eine ÖPNV-Route interaktiv mit Folium.
    itinerary: Liste von Legs, wie sie vom Routing zurückgegeben wird.
    stops_df: DataFrame mit allen Haltestellen und deren Koordinaten.
    filename: Name der zu speichernden HTML-Datei.
    """
    if not itinerary or stops_df.empty:
        print("Keine Route oder Haltestellen zum Visualisieren.")
        return

    # Sammle alle Koordinaten der Route (von jedem Leg Start und Ziel)
    coords = []
    names = []
    for leg in itinerary:
        from_stop = leg['from_stop']
        to_stop = leg['to_stop']

        from_row = stops_df[stops_df['stop_id'] == from_stop]
        to_row = stops_df[stops_df['stop_id'] == to_stop]

        if not from_row.empty:
            coords.append((from_row.iloc[0]['stop_lat'], from_row.iloc[0]['stop_lon']))
            names.append(from_row.iloc[0]['stop_name'])
        # Ziel-Haltestelle nur beim letzten Leg hinzufügen
        if leg == itinerary[-1] and not to_row.empty:
            coords.append((to_row.iloc[0]['stop_lat'], to_row.iloc[0]['stop_lon']))
            names.append(to_row.iloc[0]['stop_name'])

    # Kartenzentrum auf Startpunkt setzen
    m = folium.Map(location=coords[0], zoom_start=13, tiles="OpenStreetMap")

    # Route als Linie einzeichnen
    folium.PolyLine(coords, color='blue', weight=5, opacity=0.8, tooltip="Route").add_to(m)

    # Marker für Start und Ziel
    folium.Marker(coords[0], popup=f"Start: {names[0]}", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(coords[-1], popup=f"Ziel: {names[-1]}", icon=folium.Icon(color='red')).add_to(m)

    # Marker für Zwischenhalte (optional)
    for i, (lat, lon) in enumerate(coords[1:-1], 1):
        folium.CircleMarker([lat, lon], radius=4, color='blue', fill=True,
                            fill_color='blue', popup=names[i]).add_to(m)

    m.save(filename)
    print(f"Interaktive Karte gespeichert als {filename}")

