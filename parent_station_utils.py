import pandas as pd

def get_all_stop_ids_for_station(stops_df, stop_id):
    """
    Gibt alle stop_ids zurück, die zur gleichen Station (parent_station) gehören wie stop_id.
    """
    # Prüfe, ob stop_id ein parent_station ist
    if stop_id in stops_df['parent_station'].values:
        return stops_df[stops_df['parent_station'] == stop_id]['stop_id'].tolist()
    
    # Sonst: Hole parent_station von stop_id
    row = stops_df[stops_df['stop_id'] == stop_id]
    if not row.empty and pd.notna(row.iloc[0]['parent_station']):
        parent = row.iloc[0]['parent_station']
        return stops_df[stops_df['parent_station'] == parent]['stop_id'].tolist()
    else:
        return [stop_id]

def get_all_stop_ids_for_name(stops_df, stop_name):
    """
    Gibt alle stop_ids zurück, die zu einer Haltestelle mit gegebenem Namen gehören.
    """
    # Exakte Übereinstimmung
    exact = stops_df[stops_df['stop_name'].str.lower() == stop_name.lower()]
    if not exact.empty:
        return exact['stop_id'].tolist()
    
    # Teilstring-Suche mit regex=False
    partial = stops_df[stops_df['stop_name'].str.lower().str.contains(stop_name.lower(), na=False, regex=False)]
    return partial['stop_id'].tolist()

def is_same_station_area(stop_id1, stop_id2, stops_df):
    """
    Prüft, ob zwei stop_ids zur selben Umsteigestation (parent_station) gehören.
    """
    group1 = set(get_all_stop_ids_for_station(stops_df, stop_id1))
    group2 = set(get_all_stop_ids_for_station(stops_df, stop_id2))
    return not group1.isdisjoint(group2)
