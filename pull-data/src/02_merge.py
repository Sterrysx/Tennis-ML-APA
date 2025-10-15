#!/usr/bin/env python3
"""
ATP Matches Data Merger
Merges all ATP matches data from 2011-2024 into a single file,
organized by months and years.
"""

import pandas as pd
import glob
import os
from datetime import datetime
import calendar

def month_num_to_name(month):
    """Return month name for 1..12, otherwise None."""
    try:
        m = int(month)
    except (TypeError, ValueError):
        return None
    return calendar.month_name[m] if 1 <= m <= 12 else None

def parse_date(date_str):
    """Parse date from YYYYMMDD format to datetime object."""
    if pd.isna(date_str):
        return None
    try:
        date_str = str(int(date_str))  # Convert to string and remove decimals if any
        return datetime.strptime(date_str, '%Y%m%d')
    except (ValueError, TypeError):
        return None

def convert_tourney_level_to_points(df):
    """
    Convert tournament level codes to ATP ranking points awarded to the winner.
    
    ATP Point System:
    - G (Grand Slam): 2000 points
    - M (Masters 1000): 1000 points
    - F (ATP Finals): 1500 points
    - A (ATP 500): 500 points (larger draw: 48-56 players)
    - A (ATP 250): 250 points (smaller draw: 28-32 players)
    - D (Davis Cup): 0 points (team event, no individual ranking points)
    
    ATP 500 tournaments typically have draw sizes of 48 or 56.
    ATP 250 tournaments typically have draw sizes of 28 or 32.
    """
    
    # Known ATP 500 tournament names (as of 2011-2024)
    atp_500_tournaments = {
        'Barcelona', "Queen's Club", 'Hamburg', 'Washington', 'Winston-Salem',
        'Dubai', 'Rotterdam', 'Acapulco', 'Memphis', 'Rio de Janeiro',
        'Barcelona', 'Halle', 'London', 'Beijing', 'Tokyo', 'Basel',
        'Vienna', 'Barcelona Open', 'Aegon Championships', 'Fever-Tree Championships',
        'Citi Open', 'China Open', 'Rakuten Japan Open', 'Swiss Indoors Basel',
        'Erste Bank Open', 'ABN AMRO World Tennis Tournament'
    }
    
    def get_points(row):
        level = row['tourney_level']
        draw_size = row.get('draw_size', 0)
        tourney_name = row.get('tourney_name', '')
        
        # Grand Slam
        if level == 'G':
            return 2000
        # Masters 1000
        elif level == 'M':
            return 1000
        # ATP Finals
        elif level == 'F':
            return 1500
        # Davis Cup (no ranking points)
        elif level == 'D':
            return 0
        # ATP 250/500 - distinguish by draw size or tournament name
        elif level == 'A':
            # Check if it's a known ATP 500 tournament
            if any(atp_500 in str(tourney_name) for atp_500 in atp_500_tournaments):
                return 500
            # Otherwise use draw size heuristic
            # ATP 500 tournaments typically have 48 or 56 players
            # ATP 250 tournaments typically have 28 or 32 players
            elif draw_size >= 48:
                return 500
            else:
                return 250
        else:
            # Unknown level, return 0
            return 0
    
    df['tourney_points'] = df.apply(get_points, axis=1)
    
    return df

def add_date_features(df):
    """Add year, month and month_name columns based on tourney_date."""
    # Parse the tournament date
    df['parsed_date'] = df['tourney_date'].apply(parse_date)
    
    # Extract year and month
    df['year'] = df['parsed_date'].dt.year
    df['month'] = df['parsed_date'].dt.month
    df['day'] = df['parsed_date'].dt.day

    
    # Add lexical month name (January, February, ...)
    df['month_name'] = df['month'].apply(month_num_to_name)
    
    # Create a year-month column for easier sorting
    df['year_month'] = df['parsed_date'].dt.to_period('M')
    
    return df

def merge_atp_matches():
    """Merge all ATP matches from 2011-2024 into a single file."""
    print("Starting ATP matches merge process...")
    
    # Define the directory containing ATP matches
    data_dir = "atp_matches"
    
    # Get all CSV files in the atp_matches directory
    csv_files = glob.glob(os.path.join(data_dir, "atp_matches_*.csv"))
    csv_files.sort()  # Sort to ensure consistent order
    
    print(f"Found {len(csv_files)} ATP matches files:")
    for file in csv_files:
        print(f"  - {os.path.basename(file)}")
    
    # Read and combine all CSV files
    dataframes = []
    
    for file in csv_files:
        print(f"Reading {os.path.basename(file)}...")
        try:
            df = pd.read_csv(file)
            print(f"  - Loaded {len(df):,} matches")
            dataframes.append(df)
        except Exception as e:
            print(f"  - Error reading {file}: {e}")
            continue
    
    if not dataframes:
        print("No data files could be read!")
        return
    
    # Combine all dataframes
    print("\nCombining all dataframes...")
    combined_df = pd.concat(dataframes, ignore_index=True)
    print(f"Total matches before processing: {len(combined_df):,}")
    
    # Add date features
    print("Adding date features and organizing by year/month...")
    combined_df = add_date_features(combined_df)
    
    # Convert tournament levels to points
    print("Converting tournament levels to ATP ranking points...")
    combined_df = convert_tourney_level_to_points(combined_df)
    
    # Show tournament points distribution
    print("\nTournament points distribution:")
    points_dist = combined_df.groupby('tourney_points').size().sort_index(ascending=False)
    for points, count in points_dist.items():
        print(f"  {points:4d} points: {count:,} matches")
    
    # Remove rows with invalid dates
    initial_count = len(combined_df)
    combined_df = combined_df.dropna(subset=['parsed_date'])
    print(f"\nRemoved {initial_count - len(combined_df):,} matches with invalid dates")
    
    # Sort by date (year, month, then original date)
    print("Sorting matches chronologically...")
    combined_df = combined_df.sort_values(['year', 'month', 'tourney_date', 'match_num'])
    
    # Display some statistics
    print(f"\nFinal dataset statistics:")
    print(f"Total matches: {len(combined_df):,}")
    print(f"Date range: {combined_df['parsed_date'].min().strftime('%Y-%m-%d')} to {combined_df['parsed_date'].max().strftime('%Y-%m-%d')}")
    print(f"Years covered: {sorted(combined_df['year'].unique())}")
    
    # Show matches per year
    matches_per_year = combined_df.groupby('year').size()
    print(f"\nMatches per year:")
    for year, count in matches_per_year.items():
        print(f"  {year}: {count:,} matches")
    
    # Remove temporary columns used for processing
    columns_to_drop = ['parsed_date', 'year_month']
    combined_df = combined_df.drop(columns=columns_to_drop)
    
    # Save the merged dataset
    output_file = "parsed_data/atp_matches_2011_2024.csv"
    print(f"\nSaving merged dataset to {output_file}...")
    combined_df.to_csv(output_file, index=False)
    
    print(f"✅ Successfully created {output_file}")
    print(f"File size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    
    return combined_df

if __name__ == "__main__":
    try:
        merged_data = merge_atp_matches()
        print("\n🎾 ATP matches merge completed successfully!")
    except Exception as e:
        print(f"\n❌ Error during merge process: {e}")
        raise