import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from threading import Thread
import sys
import io
import gc
from contextlib import redirect_stdout, redirect_stderr

# Import der bestehenden Module
from gtfs_processing import load_gtfs_data, build_transit_graph
from routing import plan_route_with_transfers_ignore_time
from utils import is_stop_name, geocode_address, choose_stop, load_address_data, print_route_grouped
from auto_choose import auto_choose_stop_direction_aware
from visualize_route import visualize_route

class OPNVRouterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ÖPNV-Router Karlsruhe")
        self.root.geometry("900x700")
        
        # Initialisiere Backend-Komponenten
        self.gtfs = None
        self.transit_graph = None
        self.address_df = None
        self.current_route = None
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Header
        header_label = ttk.Label(main_frame, text="ÖPNV-Router Karlsruhe", 
                                font=('Arial', 16, 'bold'))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Routenplanung", padding="15")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Start location
        ttk.Label(input_frame, text="Start:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.start_entry = ttk.Entry(input_frame, width=50, font=('Arial', 10))
        self.start_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # End location
        ttk.Label(input_frame, text="Ziel:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.end_entry = ttk.Entry(input_frame, width=50, font=('Arial', 10))
        self.end_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        self.search_button = ttk.Button(button_frame, text="Route suchen", 
                                       command=self.search_route, width=15)
        self.search_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Leeren", 
                                      command=self.clear_inputs, width=15)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.show_map_button = ttk.Button(button_frame, text="Karte anzeigen", 
                                         command=self.show_map, state=tk.DISABLED, width=15)
        self.show_map_button.pack(side=tk.LEFT)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Ergebnisse", padding="15")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=80, 
                                                     font=('Consolas', 10))
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress and status section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Lade Daten...")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        input_frame.columnconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        progress_frame.columnconfigure(0, weight=1)
        
        # Bind Enter key to search
        self.start_entry.bind('<Return>', lambda e: self.search_route())
        self.end_entry.bind('<Return>', lambda e: self.search_route())
        
    def load_data(self):
        # Lade Daten in separatem Thread
        thread = Thread(target=self._load_data_thread)
        thread.daemon = True
        thread.start()
        
    def _load_data_thread(self):
        try:
            self.root.after(0, lambda: self.progress.start())
            
            # Adressdatensatz laden
            self.root.after(0, lambda: self.status_label.config(text="Lade Adressdaten..."))
            self.address_df = load_address_data()
            
            # GTFS-Daten laden
            self.root.after(0, lambda: self.status_label.config(text="Lade GTFS-Daten..."))
            self.gtfs = load_gtfs_data()
            
            # Transit-Graph laden/erstellen
            self.root.after(0, lambda: self.status_label.config(text="Erstelle Transit-Graph..."))
            try:
                self.transit_graph = self.load_transit_graph()
                if self.transit_graph is None:
                    self.transit_graph = build_transit_graph(self.gtfs)
                    self.save_transit_graph(self.transit_graph)
            except Exception as e:
                self.transit_graph = build_transit_graph(self.gtfs)
            
            gc.collect()
            
            self.root.after(0, self._data_loaded)
            
        except Exception as e:
            error_msg = f"Fehler beim Laden der Daten: {str(e)}"
            self.root.after(0, lambda: self._show_error(error_msg))
    
    def _data_loaded(self):
        self.progress.stop()
        self.status_label.config(text="Bereit - Geben Sie Start und Ziel ein")
        self.search_button.config(state=tk.NORMAL)
        
    def _show_error(self, error_msg):
        self.progress.stop()
        self.status_label.config(text="Fehler beim Laden")
        messagebox.showerror("Fehler", error_msg)
        
    def search_route(self):
        if not self.gtfs or not self.transit_graph:
            messagebox.showwarning("Daten nicht geladen", "Bitte warten Sie, bis die Daten geladen sind.")
            return
            
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        
        if not start or not end:
            messagebox.showwarning("Eingabe fehlt", "Bitte geben Sie Start und Ziel ein.")
            return
        
        # Starte Suche in Hintergrund-Thread
        self.search_button.config(state=tk.DISABLED)
        self.show_map_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_label.config(text="Suche Route...")
        
        # Lösche vorherige Ergebnisse
        self.results_text.delete(1.0, tk.END)
        
        # Starte Suche in separatem Thread
        thread = Thread(target=self._search_route_thread, args=(start, end))
        thread.daemon = True
        thread.start()
        
    def _search_route_thread(self, start, end):
        try:
            # Capture stdout to redirect print statements
            output_buffer = io.StringIO()
            
            with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
                # Bestimme Start- und Zielhaltestellen
                if is_stop_name(start, self.gtfs['stops']) and is_stop_name(end, self.gtfs['stops']):
                    start_stop, end_stop, itinerary = auto_choose_stop_direction_aware(
                        start, end, self.gtfs['stops'], self.transit_graph, None, None, self.gtfs)
                else:
                    # Einzelbehandlung für Start und Ziel
                    if is_stop_name(start, self.gtfs['stops']):
                        start_stop = choose_stop(start, self.gtfs['stops'])
                    else:
                        if not self.address_df.empty:
                            _, start_stop = geocode_address(start, self.gtfs['stops'], self.address_df)
                        else:
                            raise ValueError(f"'{start}' ist weder Haltestelle noch Adresse verfügbar.")
                    
                    if is_stop_name(end, self.gtfs['stops']):
                        end_stop = choose_stop(end, self.gtfs['stops'])
                    else:
                        if not self.address_df.empty:
                            _, end_stop = geocode_address(end, self.gtfs['stops'], self.address_df)
                        else:
                            raise ValueError(f"'{end}' ist weder Haltestelle noch Adresse verfügbar.")
                    
                    itinerary = plan_route_with_transfers_ignore_time(
                        self.transit_graph, start_stop, end_stop, self.gtfs['stops'])
                
                # Formatiere Ergebnisse
                if itinerary:
                    print_route_grouped(itinerary, self.gtfs['stops'])
                    self.current_route = itinerary
                    success = True
                else:
                    print("Keine Route gefunden.")
                    success = False
            
            # Hole gesamten Output
            output_text = output_buffer.getvalue()
            
            # Update GUI im Hauptthread
            self.root.after(0, self._update_results, output_text, success)
            
        except Exception as e:
            error_msg = f"Fehler bei der Routensuche:\n{str(e)}"
            self.root.after(0, self._update_results, error_msg, False)
    
    def _update_results(self, result, success):
        self.results_text.insert(tk.END, result)
        self.search_button.config(state=tk.NORMAL)
        self.progress.stop()
        
        if success:
            self.status_label.config(text="Route gefunden")
            self.show_map_button.config(state=tk.NORMAL)
        else:
            self.status_label.config(text="Keine Route gefunden")
            
    def show_map(self):
        if self.current_route:
            try:
                self.status_label.config(text="Erstelle Karte...")
                visualize_route(self.current_route, self.gtfs['stops'])
                self.status_label.config(text="Karte gespeichert, Sie können diese nun über ihren Browser öffnen")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen der Karte: {str(e)}")
                self.status_label.config(text="Fehler bei Kartenerstellung")
        else:
            messagebox.showwarning("Keine Route", "Bitte suchen Sie zuerst eine Route.")
    
    def clear_inputs(self):
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.current_route = None
        self.show_map_button.config(state=tk.DISABLED)
    
    def save_transit_graph(self, graph, filename='graph.pkl'):
        import pickle
        try:
            with open(filename, 'wb') as f:
                pickle.dump(graph, f)
        except Exception as e:
            print(f"Fehler beim Speichern des Graphen: {e}")
    
    def load_transit_graph(self, filename='graph.pkl'):
        import pickle
        import os
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Fehler beim Laden des Graphen: {e}")
                return None
        return None

def main():
    root = tk.Tk()
    app = OPNVRouterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
