#!/usr/bin/env python3
"""
ATP Matches Win Computer
Computes additional statistics for each player in each match:
- Number of matches won that year (up to that match)
- Number of matches lost that year (up to that match)
- Win percentage that year (up to that match)
- Head-to-head record against the opponent (up to that match)

Reads from parsed_data/03_atp_matches.csv and outputs to parsed_data/04_atp_matches.csv
"""

import pandas as pd
import os
from collections import defaultdict

def compute_yearly_stats(df):
    """Compute yearly win/loss statistics for each player."""
    print("📊 Computing yearly win/loss statistics...")
    
    # Sort by date to ensure chronological order
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Initialize tracking dictionaries
    yearly_wins = defaultdict(lambda: defaultdict(int))  # player -> year -> wins
    yearly_losses = defaultdict(lambda: defaultdict(int))  # player -> year -> losses
    
    # Lists to store the computed stats for each match
    winner_wins_ytd = []
    winner_losses_ytd = []
    winner_win_pct_ytd = []
    loser_wins_ytd = []
    loser_losses_ytd = []
    loser_win_pct_ytd = []
    
    for idx, row in df_sorted.iterrows():
        year = row['tournament_year']
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        
        # Get current year-to-date stats BEFORE this match
        winner_wins_before = yearly_wins[winner][year]
        winner_losses_before = yearly_losses[winner][year]
        loser_wins_before = yearly_wins[loser][year]
        loser_losses_before = yearly_losses[loser][year]
        
        # Calculate win percentages (handle division by zero)
        winner_total_before = winner_wins_before + winner_losses_before
        loser_total_before = loser_wins_before + loser_losses_before
        
        winner_pct_before = (winner_wins_before / winner_total_before * 100) if winner_total_before > 0 else 0.0
        loser_pct_before = (loser_wins_before / loser_total_before * 100) if loser_total_before > 0 else 0.0
        
        # Store the stats for this match
        winner_wins_ytd.append(winner_wins_before)
        winner_losses_ytd.append(winner_losses_before)
        winner_win_pct_ytd.append(round(winner_pct_before, 2))
        
        loser_wins_ytd.append(loser_wins_before)
        loser_losses_ytd.append(loser_losses_before)
        loser_win_pct_ytd.append(round(loser_pct_before, 2))
        
        # Update the counters AFTER recording stats for this match
        yearly_wins[winner][year] += 1  # Winner gets a win
        yearly_losses[loser][year] += 1  # Loser gets a loss
    
    # Add the computed columns to dataframe
    df_sorted['winner_wins_ytd'] = winner_wins_ytd
    df_sorted['winner_losses_ytd'] = winner_losses_ytd
    df_sorted['winner_win_pct_ytd'] = winner_win_pct_ytd
    df_sorted['loser_wins_ytd'] = loser_wins_ytd
    df_sorted['loser_losses_ytd'] = loser_losses_ytd
    df_sorted['loser_win_pct_ytd'] = loser_win_pct_ytd
    
    return df_sorted

def compute_h2h_stats(df):
    """Compute head-to-head statistics between players."""
    print("🤝 Computing head-to-head statistics...")
    
    # Sort by date to ensure chronological order
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Dictionary to track H2H records: (player1, player2) -> [wins_player1, wins_player2]
    h2h_records = defaultdict(lambda: [0, 0])
    
    # Lists to store H2H stats for each match
    winner_h2h_wins = []
    winner_h2h_losses = []
    loser_h2h_wins = []
    loser_h2h_losses = []
    
    for idx, row in df_sorted.iterrows():
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        
        # Create consistent key for H2H lookup (alphabetical order)
        if winner < loser:
            h2h_key = (winner, loser)
            winner_is_first = True
        else:
            h2h_key = (loser, winner)
            winner_is_first = False
        
        # Get current H2H record BEFORE this match
        current_record = h2h_records[h2h_key].copy()
        
        if winner_is_first:
            # winner is first in the key
            winner_h2h_wins_before = current_record[0]
            winner_h2h_losses_before = current_record[1]
            loser_h2h_wins_before = current_record[1]
            loser_h2h_losses_before = current_record[0]
        else:
            # loser is first in the key
            winner_h2h_wins_before = current_record[1]
            winner_h2h_losses_before = current_record[0]
            loser_h2h_wins_before = current_record[0]
            loser_h2h_losses_before = current_record[1]
        
        # Store the H2H stats for this match
        winner_h2h_wins.append(winner_h2h_wins_before)
        winner_h2h_losses.append(winner_h2h_losses_before)
        loser_h2h_wins.append(loser_h2h_wins_before)
        loser_h2h_losses.append(loser_h2h_losses_before)
        
        # Update H2H record AFTER recording stats for this match
        if winner_is_first:
            h2h_records[h2h_key][0] += 1  # Winner gets a H2H win
        else:
            h2h_records[h2h_key][1] += 1  # Winner gets a H2H win
    
    # Add H2H columns to dataframe
    df_sorted['winner_h2h_wins'] = winner_h2h_wins
    df_sorted['winner_h2h_losses'] = winner_h2h_losses
    df_sorted['loser_h2h_wins'] = loser_h2h_wins
    df_sorted['loser_h2h_losses'] = loser_h2h_losses
    
    return df_sorted

def compute_win_statistics():
    """Main function to compute win/loss and H2H statistics."""
    
    input_file = "parsed_data/03_atp_matches.csv"
    output_file = "parsed_data/04_atp_matches.csv"
    
    print("🏆 Starting ATP matches win statistics computation...")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file {input_file} not found!")
        print("Please run the organize script first to create the input data.")
        return None
    
    try:
        # Read the data
        print(f"📖 Reading data from {input_file}...")
        df = pd.read_csv(input_file)
        print(f"Loaded {len(df):,} matches with {len(df.columns)} columns")
        
        # Check required columns
        required_cols = ['winner_player_name', 'loser_player_name', 'tournament_year', 'tournament_date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Error: Missing required columns: {missing_cols}")
            return None
        
        # Compute yearly statistics
        df_with_yearly = compute_yearly_stats(df)
        
        # Compute H2H statistics
        df_with_h2h = compute_h2h_stats(df_with_yearly)
        
        # Display sample statistics
        print(f"\n📈 Sample yearly statistics:")
        sample_cols = ['winner_player_name', 'tournament_year', 'winner_wins_ytd', 'winner_losses_ytd', 'winner_win_pct_ytd']
        print(df_with_h2h[sample_cols].head(3).to_string(index=False))
        
        print(f"\n🤝 Sample H2H statistics:")
        sample_h2h_cols = ['winner_player_name', 'loser_player_name', 'winner_h2h_wins', 'winner_h2h_losses']
        print(df_with_h2h[sample_h2h_cols].head(3).to_string(index=False))
        
        # Save the enhanced dataset
        print(f"\n💾 Saving enhanced dataset to {output_file}...")
        df_with_h2h.to_csv(output_file, index=False)
        
        # File statistics
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")
        
        # Summary statistics
        total_cols = len(df_with_h2h.columns)
        new_cols = total_cols - len(df.columns)
        
        print(f"\n📊 Enhancement summary:")
        print(f"Total matches: {len(df_with_h2h):,}")
        print(f"Original columns: {len(df.columns)}")
        print(f"New columns added: {new_cols}")
        print(f"Total columns: {total_cols}")
        
        # Show new column names
        new_column_names = [
            'winner_wins_ytd', 'winner_losses_ytd', 'winner_win_pct_ytd',
            'loser_wins_ytd', 'loser_losses_ytd', 'loser_win_pct_ytd',
            'winner_h2h_wins', 'winner_h2h_losses', 'loser_h2h_wins', 'loser_h2h_losses'
        ]
        print(f"\nNew columns added:")
        for i, col in enumerate(new_column_names, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n✅ Successfully created {output_file}")
        
        return df_with_h2h
        
    except Exception as e:
        print(f"❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        result_df = compute_win_statistics()
        if result_df is not None:
            print("\n🎾 Win statistics computation completed successfully!")
        else:
            print("\n❌ Win statistics computation failed!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise