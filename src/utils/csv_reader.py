"""
CSV file reading utilities for loading GPS coordinates from files.
"""

import csv
import os
import logging


def read_route_from_csv(filepath):
    """
    Read GPS coordinates from a CSV file.
    Expected format: lat,lon (one coordinate pair per line)
    Optional header row is automatically detected and skipped.
    
    Args:
        filepath (str): Path to CSV file
    
    Returns:
        list: List of (lat, lon) tuples, or None if error occurs
    """
    if not os.path.exists(filepath):
        logging.error(f"CSV file not found: {filepath}")
        return None
    
    route = []
    
    try:
        with open(filepath, 'r') as csvfile:
            # Try to detect if there's a header row
            sample = csvfile.read(1024)
            csvfile.seek(0)
            
            try:
                has_header = csv.Sniffer().has_header(sample)
            except csv.Error:
                # If detection fails, assume no header
                has_header = False
            
            reader = csv.reader(csvfile)
            
            # Skip header row if detected
            if has_header:
                next(reader)
            
            # Process each row
            for row_num, row in enumerate(reader, start=1):
                if len(row) < 2:
                    logging.warning(f"Skipping row {row_num}: insufficient columns")
                    continue
                
                try:
                    lat = float(row[0].strip())
                    lon = float(row[1].strip())
                    
                    # Validate coordinate ranges
                    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                        logging.warning(f"Skipping row {row_num}: invalid coordinates ({lat}, {lon})")
                        continue
                    
                    route.append((lat, lon))
                
                except ValueError:
                    logging.warning(f"Skipping row {row_num}: invalid number format")
                    continue
        
        # Check if any valid coordinates were found
        if not route:
            logging.error("No valid coordinates found in CSV file")
            return None
        
        logging.info(f"Loaded {len(route)} coordinates from CSV")
        return route
    
    except Exception as e:
        logging.error(f"Error reading CSV file: {str(e)}")
        return None
