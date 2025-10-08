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

def parse_date(date_str):
    """Parse date from YYYYMMDD format to datetime object."""
    if pd.isna(date_str):
        return None
    try:
        date_str = str(int(date_str))  # Convert to string and remove decimals if any
        return datetime.strptime(date_str, '%Y%m%d')
    except (ValueError, TypeError):
        return None

def add_date_features(df):
    """Add year and month columns based on tourney_date."""
    # Parse the tournament date
    df['parsed_date'] = df['tourney_date'].apply(parse_date)
    
    # Extract year and month
    df['year'] = df['parsed_date'].dt.year
    df['month'] = df['parsed_date'].dt.month
    
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
    
    # Remove rows with invalid dates
    initial_count = len(combined_df)
    combined_df = combined_df.dropna(subset=['parsed_date'])
    print(f"Removed {initial_count - len(combined_df):,} matches with invalid dates")
    
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
    output_file = "atp_matches_2011_2024.csv"
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