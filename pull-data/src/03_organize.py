#!/usr/bin/env python3
"""
ATP Matches Data Organizer
Renames columns to more understandable names and organizes them logically.
Reads from parsed_data/atp_matches_2011_2024.csv and outputs to 03_atp_matches.csv
"""

import pandas as pd
import os

def create_column_mapping():
    """Create mapping from current column names to more understandable names."""
    
    # Generic/Tournament columns
    generic_mapping = {
        'tourney_id': 'tournament_id',
        'tourney_name': 'tournament_name',
        'surface': 'court_surface',
        'draw_size': 'tournament_draw_size',
        'tourney_level': 'tournament_level',
        'tourney_points': 'tournament_points',
        'tourney_date': 'tournament_date',
        'match_num': 'match_number',
        'score': 'final_score',
        'best_of': 'best_of_sets',
        'round': 'tournament_round',
        'minutes': 'match_duration_minutes',
        'year': 'tournament_year',
        'month': 'tournament_month',
        'day': 'tournament_day',
        'month_name': 'tournament_month_name'
    }
    
    # Winner columns (w_ prefix)
    winner_mapping = {
        'winner_id': 'winner_player_id',
        'winner_seed': 'winner_tournament_seed',
        'winner_entry': 'winner_entry_type',
        'winner_name': 'winner_player_name',
        'winner_hand': 'winner_handedness',
        'winner_ht': 'winner_height_cm',
        'winner_ioc': 'winner_country_code',
        'winner_age': 'winner_age_years',
        'winner_rank': 'winner_atp_rank',
        'winner_rank_points': 'winner_atp_points',
        'w_ace': 'winner_aces',
        'w_df': 'winner_double_faults',
        'w_svpt': 'winner_serve_points_total',
        'w_1stIn': 'winner_first_serves_in',
        'w_1stWon': 'winner_first_serve_points_won',
        'w_2ndWon': 'winner_second_serve_points_won',
        'w_SvGms': 'winner_service_games',
        'w_bpSaved': 'winner_break_points_saved',
        'w_bpFaced': 'winner_break_points_faced'
    }
    
    # Loser columns (l_ prefix)
    loser_mapping = {
        'loser_id': 'loser_player_id',
        'loser_seed': 'loser_tournament_seed',
        'loser_entry': 'loser_entry_type',
        'loser_name': 'loser_player_name',
        'loser_hand': 'loser_handedness',
        'loser_ht': 'loser_height_cm',
        'loser_ioc': 'loser_country_code',
        'loser_age': 'loser_age_years',
        'loser_rank': 'loser_atp_rank',
        'loser_rank_points': 'loser_atp_points',
        'l_ace': 'loser_aces',
        'l_df': 'loser_double_faults',
        'l_svpt': 'loser_serve_points_total',
        'l_1stIn': 'loser_first_serves_in',
        'l_1stWon': 'loser_first_serve_points_won',
        'l_2ndWon': 'loser_second_serve_points_won',
        'l_SvGms': 'loser_service_games',
        'l_bpSaved': 'loser_break_points_saved',
        'l_bpFaced': 'loser_break_points_faced'
    }
    
    # Combine all mappings
    complete_mapping = {**generic_mapping, **winner_mapping, **loser_mapping}
    
    return complete_mapping, generic_mapping, winner_mapping, loser_mapping

def organize_columns(df, generic_mapping, winner_mapping, loser_mapping):
    """Organize columns in logical order: generic, winner, loser."""
    
    # Get column lists in desired order
    generic_cols = list(generic_mapping.values())
    winner_cols = list(winner_mapping.values())
    loser_cols = list(loser_mapping.values())
    
    # Filter to only include columns that actually exist in the dataframe
    existing_generic = [col for col in generic_cols if col in df.columns]
    existing_winner = [col for col in winner_cols if col in df.columns]
    existing_loser = [col for col in loser_cols if col in df.columns]
    
    # Combine in logical order
    ordered_columns = existing_generic + existing_winner + existing_loser
    
    # Add any remaining columns that weren't mapped
    remaining_cols = [col for col in df.columns if col not in ordered_columns]
    if remaining_cols:
        print(f"Warning: Found unmapped columns: {remaining_cols}")
        ordered_columns.extend(remaining_cols)
    
    return df[ordered_columns]

def organize_atp_matches():
    """Main function to organize and rename ATP matches data."""
    
    input_file = "parsed_data/atp_matches_2011_2024.csv"
    output_file = "parsed_data/03_atp_matches.csv"
    
    print("🏆 Starting ATP matches data organization...")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file {input_file} not found!")
        print("Please run the merge script first to create the input data.")
        return None
    
    try:
        # Read the data
        print(f"📖 Reading data from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df):,} matches with {len(df.columns)} columns")
        
        # Get column mappings
        complete_mapping, generic_mapping, winner_mapping, loser_mapping = create_column_mapping()
        
        # Show current vs new column names
        print(f"\n📋 Column renaming summary:")
        print(f"  Generic columns: {len(generic_mapping)}")
        print(f"  Winner columns: {len(winner_mapping)}")
        print(f"  Loser columns: {len(loser_mapping)}")
        print(f"  Total mapped: {len(complete_mapping)}")
        
        # Check for any unmapped columns
        current_cols = set(df.columns)
        mapped_cols = set(complete_mapping.keys())
        unmapped = current_cols - mapped_cols
        
        if unmapped:
            print(f"⚠️  Unmapped columns found: {sorted(unmapped)}")
        else:
            print("✅ All columns have mappings")
        
        # Rename columns
        print("\n🔄 Renaming columns...")
        df_renamed = df.rename(columns=complete_mapping)
        
        # Organize columns in logical order
        print("📊 Organizing columns in logical order...")
        df_organized = organize_columns(df_renamed, generic_mapping, winner_mapping, loser_mapping)
        
        # Display sample of new structure
        print(f"\n📈 New column structure:")
        print("Generic/Tournament columns:")
        for i, col in enumerate(df_organized.columns):
            if col in generic_mapping.values():
                print(f"  {i+1:2d}. {col}")
        
        print("\nWinner columns:")
        for i, col in enumerate(df_organized.columns):
            if col in winner_mapping.values():
                print(f"  {i+1:2d}. {col}")
        
        print("\nLoser columns:")
        for i, col in enumerate(df_organized.columns):
            if col in loser_mapping.values():
                print(f"  {i+1:2d}. {col}")
        
        # Save organized data
        print(f"\n💾 Saving organized data to {output_file}...")
        df_organized.to_csv(output_file, index=False)
        
        # File statistics
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")
        
        # Show sample of organized data
        print(f"\n🔍 Sample of organized data (first 3 rows, first 8 columns):")
        sample_cols = df_organized.columns[:8].tolist()
        print(df_organized[sample_cols].head(3).to_string(index=False))
        
        print(f"\n✅ Successfully created {output_file}")
        print(f"Total columns: {len(df_organized.columns)}")
        print(f"Total matches: {len(df_organized):,}")
        
        return df_organized
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        return None

if __name__ == "__main__":
    try:
        result_df = organize_atp_matches()
        if result_df is not None:
            print("\n🎾 ATP matches organization completed successfully!")
        else:
            print("\n❌ ATP matches organization failed!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise