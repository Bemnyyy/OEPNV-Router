import folium

def visualize_route(itinerary, stops_df, filename="route_map.html"):
    """
    Visualisiert eine ÖPNV-Route interaktiv mit Folium.
    """
    if not itinerary or stops_df.empty:
        print("Keine Route oder Haltestellen zum Visualisieren.")
        return

    # Sammle alle Koordinaten der Route
    coords = []
    names = []
    transfer_points = []
    
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
        
        # Umstiegserkennung
        if leg.get('transfer', False):
            transfer_points.append(len(coords) - 1)

    # Kartenerstellung
    m = folium.Map(location=coords[0], zoom_start=13, tiles="OpenStreetMap")

    # Route als Linie
    folium.PolyLine(coords, color='blue', weight=5, opacity=0.8, tooltip="Route").add_to(m)

    # Marker für Start und Ziel
    folium.Marker(coords[0], popup=f"🚌 Start: {names[0]}", 
                  icon=folium.Icon(color='green', icon='play')).add_to(m)
    folium.Marker(coords[-1], popup=f"🏁 Ziel: {names[-1]}", 
                  icon=folium.Icon(color='red', icon='stop')).add_to(m)

    # Umstiegspunkte
    for transfer_idx in transfer_points:
        if transfer_idx < len(coords):
            folium.Marker(coords[transfer_idx], 
                         popup=f"🔄 UMSTIEG: {names[transfer_idx]}", 
                         icon=folium.Icon(color='orange', icon='refresh')).add_to(m)

    # Normale Haltestellen
    for i, (lat, lon) in enumerate(coords[1:-1], 1):
        if i not in transfer_points:
            folium.CircleMarker([lat, lon], radius=4, color='blue', fill=True,
                               fill_color='blue', popup=f"🚏 {names[i]}").add_to(m)

    # Legende - KORRIGIERTE VERSION
    legend_html = """
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <h4>Legende</h4>
    <p><i class="fa fa-play" style="color:green"></i> Start</p>
    <p><i class="fa fa-stop" style="color:red"></i> Ziel</p>
    <p><i class="fa fa-refresh" style="color:orange"></i> Umstieg</p>
    <p><i class="fa fa-circle" style="color:blue"></i> Haltestelle</p>
    </div>
    """
    
    # KORRIGIERTE METHODE - ohne .html
    m.get_root().add_child(folium.Element(legend_html))

    # Route-Informationen
    umstieg_count = len(transfer_points)
    print(f"Route visualisiert mit {umstieg_count} Umstieg(en)")
    
    m.save(filename)
    print(f"Interaktive Karte gespeichert als {filename}")

