import pandas as pd
from typing import List, Dict, Tuple, Any, Set

def extract_codices_from_top50(top50_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Extrahiert die Codices und zugehörige Informationen aus der Top-50-Liste.
    
    Args:
        top50_df: DataFrame der Top-50-Liste
        
    Returns:
        Eine Liste von Dictionaries mit den Codices und zugehörigen Informationen
    """
    # Nur Zeilen mit gültigen Codices betrachten (nicht NaN)
    valid_rows = top50_df.dropna(subset=['Codice'])
    
    result = []
    for _, row in valid_rows.iterrows():
        full_codice = row['Codice']
        # Codice in den Teil vor und nach # aufteilen
        if '#' in str(full_codice):
            base_codice = full_codice.split('#')[0]
        else:
            base_codice = full_codice
            
        # Informationen sammeln
        entry = {
            'full_codice': full_codice,
            'base_codice': base_codice,
            'lagerbestand': row.get('Lagerbestand', None),
            'kundenauftraege': row.get('Kundenauftraegen', None),
            'monatlicher_verbrauch': row.get('Montatlicher Verbrauch', None)
        }
        result.append(entry)
        
    return result

def get_artikelnummern_for_codice(translator_df: pd.DataFrame, base_codice: str) -> List[str]:
    """
    Findet alle Artikelnummern für einen gegebenen Basis-Codice in der Übersetzungsdatei.
    
    Args:
        translator_df: DataFrame der Übersetzungsdatei
        base_codice: Der Basis-Codice (ohne #-Teil)
        
    Returns:
        Eine Liste von Artikelnummern, die dem Basis-Codice entsprechen
    """
    # Spalte D (Index 3) enthält den Basis-Codice
    # Spalte Q (Index 16) enthält die Artikelnummer
    
    # Alle Zeilen finden, in denen Spalte D dem Basis-Codice entspricht
    matching_rows = translator_df[translator_df.iloc[:, 3] == base_codice]
    
    # Artikelnummern aus Spalte Q extrahieren
    artikelnummern = []
    for _, row in matching_rows.iterrows():
        if pd.notna(row.iloc[16]):  # Prüfen, ob die Zelle nicht NaN ist
            artikelnummern.append(str(row.iloc[16]))
            
    return artikelnummern

def find_matches_in_ool(ool_df: pd.DataFrame, artikelnummern: List[str], codice_info: Dict[str, Any]) -> Tuple[List[int], List[Dict[str, Any]]]:
    """
    Findet Übereinstimmungen zwischen Artikelnummern und der Open Order List.
    Fügt auch zusätzliche Informationen aus dem Codice hinzu.
    
    Args:
        ool_df: DataFrame der Open Order List
        artikelnummern: Liste von Artikelnummern zum Abgleich
        codice_info: Dictionary mit Informationen zum Codice (Lagerbestand, etc.)
        
    Returns:
        Ein Tuple aus:
        - Liste von Zeilenindizes mit Übereinstimmungen
        - Liste von Dictionaries mit den gefundenen Zeilen und Informationen
    """
    match_indices = []
    matched_rows = []
    
    # Artikelnummern vorbereiten - verschiedene Formate berücksichtigen
    artikelnummern_set = set()
    for art in artikelnummern:
        # Das Original-Format hinzufügen
        artikelnummern_set.add(art)
        
        # Format für Integer-Vergleich hinzufügen (ohne führende Nullen)
        try:
            numeric_art = str(int(float(art)))
            artikelnummern_set.add(numeric_art)
        except (ValueError, TypeError):
            pass
        
        # Format mit führender '7' hinzufügen für potenziellen Vergleich mit OOL
        if not art.startswith('7') and art.isdigit():
            artikelnummern_set.add('7' + art)
    
    # Jede Zeile in der Open Order List überprüfen
    for idx, row in ool_df.iterrows():
        # Konvertiere die OOL-Artikelnummer in verschiedene Formate für den Vergleich
        ool_artikel = row['artikel no']
        ool_artikel_str = str(ool_artikel)
        
        # Auch Format ohne führende '7' in Betracht ziehen
        ool_ohne_7 = ool_artikel_str[1:] if ool_artikel_str.startswith('7') else ool_artikel_str
        
        # Überprüfe alle möglichen Formate
        if (ool_artikel_str in artikelnummern_set or 
            ool_ohne_7 in artikelnummern_set):
            match_indices.append(idx)
            matched_rows.append({
                'artikel_no': ool_artikel_str,
                'abmessung': row.get('Abmessung', ''),
                'gesamtmenge': row.get('Gesamtmenge', ''),
                'offene_menge': row.get('offene Menge', ''),
                # Zusätzliche Informationen aus dem Codice
                'lagerbestand': codice_info.get('lagerbestand', None),
                'kundenauftraege': codice_info.get('kundenauftraege', None),
                'monatlicher_verbrauch': codice_info.get('monatlicher_verbrauch', None),
                'full_codice': codice_info.get('full_codice', None),
                'base_codice': codice_info.get('base_codice', None)
            })
            
    return match_indices, matched_rows

def process_all_data(top50_df: pd.DataFrame, translator_df: pd.DataFrame, ool_df: pd.DataFrame) -> Tuple[List[int], List[Dict[str, Any]], pd.DataFrame]:
    """
    Verarbeitet alle Daten und führt den gesamten Matchingprozess durch.
    
    Args:
        top50_df: DataFrame der Top-50-Liste
        translator_df: DataFrame der Übersetzungsdatei
        ool_df: DataFrame der Open Order List
        
    Returns:
        Ein Tuple aus:
        - Liste von Zeilenindizes in der Open Order List, die hervorgehoben werden sollen
        - Liste von Dictionaries für die Zusammenfassungsdatei
        - Erweitertes OOL DataFrame mit zusätzlichen Spalten
    """
    # Alle zu markierenden Zeilenindizes sammeln
    all_match_indices = []
    
    # Daten für die Zusammenfassungsdatei
    summary_data = []
    
    # Zusätzliche Spalten für die OOL-Datei erstellen
    ool_df_extended = ool_df.copy()
    ool_df_extended['Lagerbestand'] = None
    ool_df_extended['Kundenauftraege'] = None
    ool_df_extended['Monatlicher Verbrauch'] = None
    ool_df_extended['Codice'] = None
    
    # Codices aus der Top-50-Liste extrahieren
    codices_data = extract_codices_from_top50(top50_df)
    
    # Für jeden Codice den Prozess durchführen
    for codice_entry in codices_data:
        full_codice = codice_entry['full_codice']
        base_codice = codice_entry['base_codice']
        
        # Artikelnummern für den Basis-Codice finden
        artikelnummern = get_artikelnummern_for_codice(translator_df, base_codice)
        
        # Übereinstimmungen in der Open Order List finden
        match_indices, matched_rows = find_matches_in_ool(ool_df, artikelnummern, codice_entry)
        
        # Indizes für die zu markierenden Zeilen sammeln
        all_match_indices.extend(match_indices)
        
        # Zusätzliche Daten in die erweiterte OOL-Datei eintragen
        for idx in match_indices:
            ool_df_extended.at[idx, 'Lagerbestand'] = codice_entry.get('lagerbestand')
            ool_df_extended.at[idx, 'Kundenauftraege'] = codice_entry.get('kundenauftraege')
            ool_df_extended.at[idx, 'Monatlicher Verbrauch'] = codice_entry.get('monatlicher_verbrauch')
            ool_df_extended.at[idx, 'Codice'] = full_codice
        
        # Zusammenfassungsdaten für jeden gefundenen Artikel sammeln
        for artikel_no in artikelnummern:
            # Formatvarianten der aktuellen Artikelnummer erstellen
            artikel_no_variants = [artikel_no]  # Original
            if not artikel_no.startswith('7') and artikel_no.isdigit():
                artikel_no_variants.append('7' + artikel_no)  # Mit führender 7
            
            # Prüfen, ob eine der Varianten in den Übereinstimmungen gefunden wurde
            matched = False
            for variant in artikel_no_variants:
                if any(variant in row['artikel_no'] or row['artikel_no'] in variant for row in matched_rows):
                    matched = True
                    break
            
            # Zusammenfassungseintrag erstellen
            summary_entry = {
                'codice_full': full_codice,
                'codice_base': base_codice,
                'artikelnummer': artikel_no,
                'lagerbestand': codice_entry['lagerbestand'],
                'kundenauftraege': codice_entry['kundenauftraege'],
                'monatlicher_verbrauch': codice_entry['monatlicher_verbrauch'],
                'gefunden_in_ool': "Ja" if matched else "Nein"
            }
            summary_data.append(summary_entry)
    
    return all_match_indices, summary_data, ool_df_extended 