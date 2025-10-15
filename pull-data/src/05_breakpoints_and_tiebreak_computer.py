#!/usr/bin/env python3
"""
ATP Matches Breakpoints and Tiebreak Computer
Computes additional statistics for each player in each match:
- Breakpoints won YTD (year-to-date) and percentage
- Breakpoints won career and percentage
- Tiebreaks played YTD and career
- Tiebreaks won YTD and career (and percentages)

A tiebreak is identified by a set score of 7-6 (winner) or 6-7 (loser).

Reads from parsed_data/04_atp_matches.csv and outputs to parsed_data/05_atp_matches.csv
"""

import pandas as pd
import numpy as np
import os
import re
from collections import defaultdict

def count_tiebreaks_in_score(score, player_won_match):
    """
    Count tiebreaks won and played from a match score.
    Returns (tiebreaks_won, tiebreaks_played)
    
    A tiebreak is played when a set goes to 7-6 or 6-7.
    The player who won 7-6 won that tiebreak.
    The player who lost 6-7 lost that tiebreak.
    """
    if pd.isna(score) or score == '':
        return 0, 0
    
    tiebreaks_won = 0
    tiebreaks_played = 0
    
    # Split score into sets (e.g., "6-4 7-6(3) 6-2" -> ["6-4", "7-6(3)", "6-2"])
    sets = score.strip().split()
    
    for set_score in sets:
        # Remove tiebreak score in parentheses for checking
        set_main = re.sub(r'\([0-9]+\)', '', set_score)
        
        # Check if this set went to a tiebreak
        if '7-6' in set_main:
            tiebreaks_played += 1
            if player_won_match:
                # Winner won this set at 7-6, so they won the tiebreak
                tiebreaks_won += 1
        elif '6-7' in set_main:
            tiebreaks_played += 1
            if not player_won_match:
                # Loser had 6-7, which means they lost the tiebreak
                # But from loser's perspective, they didn't win it
                # If we're counting for the winner, they won this tiebreak
                tiebreaks_won += 1
    
    return tiebreaks_won, tiebreaks_played

def compute_breakpoint_and_tiebreak_stats(df):
    """
    Compute breakpoint and tiebreak statistics for each player.
    
    For each match, we compute:
    - Breakpoints won/faced YTD and career
    - Tiebreaks won/played YTD and career
    - Corresponding percentages
    """
    print("📊 Computing breakpoint and tiebreak statistics...")
    
    # Sort by date to ensure chronological order
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Initialize tracking dictionaries
    # Career stats (all-time)
    career_bp_won = defaultdict(int)  # player -> breakpoints won (saved when serving)
    career_bp_faced = defaultdict(int)  # player -> breakpoints faced
    career_tb_won = defaultdict(int)  # player -> tiebreaks won
    career_tb_played = defaultdict(int)  # player -> tiebreaks played
    
    # Yearly stats (YTD)
    yearly_bp_won = defaultdict(lambda: defaultdict(int))  # player -> year -> bp won
    yearly_bp_faced = defaultdict(lambda: defaultdict(int))  # player -> year -> bp faced
    yearly_tb_won = defaultdict(lambda: defaultdict(int))  # player -> year -> tb won
    yearly_tb_played = defaultdict(lambda: defaultdict(int))  # player -> year -> tb played
    
    # Lists to store computed stats for each match
    winner_bp_won_ytd = []
    winner_bp_faced_ytd = []
    winner_bp_pct_ytd = []
    winner_bp_won_career = []
    winner_bp_faced_career = []
    winner_bp_pct_career = []
    
    loser_bp_won_ytd = []
    loser_bp_faced_ytd = []
    loser_bp_pct_ytd = []
    loser_bp_won_career = []
    loser_bp_faced_career = []
    loser_bp_pct_career = []
    
    winner_tb_won_ytd = []
    winner_tb_played_ytd = []
    winner_tb_pct_ytd = []
    winner_tb_won_career = []
    winner_tb_played_career = []
    winner_tb_pct_career = []
    
    loser_tb_won_ytd = []
    loser_tb_played_ytd = []
    loser_tb_pct_ytd = []
    loser_tb_won_career = []
    loser_tb_played_career = []
    loser_tb_pct_career = []
    
    for idx, row in df_sorted.iterrows():
        year = row['tournament_year']
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        score = row['final_score']
        
        # Get breakpoint stats for this match
        winner_bp_saved = row['winner_break_points_saved'] if pd.notna(row['winner_break_points_saved']) else 0
        winner_bp_faced_match = row['winner_break_points_faced'] if pd.notna(row['winner_break_points_faced']) else 0
        loser_bp_saved = row['loser_break_points_saved'] if pd.notna(row['loser_break_points_saved']) else 0
        loser_bp_faced_match = row['loser_break_points_faced'] if pd.notna(row['loser_break_points_faced']) else 0
        
        # Get tiebreak stats for this match
        winner_tb_won_match, winner_tb_played_match = count_tiebreaks_in_score(score, player_won_match=True)
        loser_tb_won_match, loser_tb_played_match = count_tiebreaks_in_score(score, player_won_match=False)
        
        # Note: tiebreaks are symmetric - if winner played N tiebreaks, so did loser
        # But winner won X and loser won (N-X)
        
        # Get stats BEFORE this match (YTD)
        winner_bp_won_ytd_before = yearly_bp_won[winner][year]
        winner_bp_faced_ytd_before = yearly_bp_faced[winner][year]
        loser_bp_won_ytd_before = yearly_bp_won[loser][year]
        loser_bp_faced_ytd_before = yearly_bp_faced[loser][year]
        
        winner_tb_won_ytd_before = yearly_tb_won[winner][year]
        winner_tb_played_ytd_before = yearly_tb_played[winner][year]
        loser_tb_won_ytd_before = yearly_tb_won[loser][year]
        loser_tb_played_ytd_before = yearly_tb_played[loser][year]
        
        # Get stats BEFORE this match (Career)
        winner_bp_won_career_before = career_bp_won[winner]
        winner_bp_faced_career_before = career_bp_faced[winner]
        loser_bp_won_career_before = career_bp_won[loser]
        loser_bp_faced_career_before = career_bp_faced[loser]
        
        winner_tb_won_career_before = career_tb_won[winner]
        winner_tb_played_career_before = career_tb_played[winner]
        loser_tb_won_career_before = career_tb_won[loser]
        loser_tb_played_career_before = career_tb_played[loser]
        
        # Calculate percentages (YTD)
        winner_bp_pct_ytd_val = (winner_bp_won_ytd_before / winner_bp_faced_ytd_before * 100) if winner_bp_faced_ytd_before > 0 else 0.0
        loser_bp_pct_ytd_val = (loser_bp_won_ytd_before / loser_bp_faced_ytd_before * 100) if loser_bp_faced_ytd_before > 0 else 0.0
        
        winner_tb_pct_ytd_val = (winner_tb_won_ytd_before / winner_tb_played_ytd_before * 100) if winner_tb_played_ytd_before > 0 else 0.0
        loser_tb_pct_ytd_val = (loser_tb_won_ytd_before / loser_tb_played_ytd_before * 100) if loser_tb_played_ytd_before > 0 else 0.0
        
        # Calculate percentages (Career)
        winner_bp_pct_career_val = (winner_bp_won_career_before / winner_bp_faced_career_before * 100) if winner_bp_faced_career_before > 0 else 0.0
        loser_bp_pct_career_val = (loser_bp_won_career_before / loser_bp_faced_career_before * 100) if loser_bp_faced_career_before > 0 else 0.0
        
        winner_tb_pct_career_val = (winner_tb_won_career_before / winner_tb_played_career_before * 100) if winner_tb_played_career_before > 0 else 0.0
        loser_tb_pct_career_val = (loser_tb_won_career_before / loser_tb_played_career_before * 100) if loser_tb_played_career_before > 0 else 0.0
        
        # Store stats for this match (BEFORE this match)
        # YTD Breakpoints
        winner_bp_won_ytd.append(winner_bp_won_ytd_before)
        winner_bp_faced_ytd.append(winner_bp_faced_ytd_before)
        winner_bp_pct_ytd.append(round(winner_bp_pct_ytd_val, 2))
        
        loser_bp_won_ytd.append(loser_bp_won_ytd_before)
        loser_bp_faced_ytd.append(loser_bp_faced_ytd_before)
        loser_bp_pct_ytd.append(round(loser_bp_pct_ytd_val, 2))
        
        # Career Breakpoints
        winner_bp_won_career.append(winner_bp_won_career_before)
        winner_bp_faced_career.append(winner_bp_faced_career_before)
        winner_bp_pct_career.append(round(winner_bp_pct_career_val, 2))
        
        loser_bp_won_career.append(loser_bp_won_career_before)
        loser_bp_faced_career.append(loser_bp_faced_career_before)
        loser_bp_pct_career.append(round(loser_bp_pct_career_val, 2))
        
        # YTD Tiebreaks
        winner_tb_won_ytd.append(winner_tb_won_ytd_before)
        winner_tb_played_ytd.append(winner_tb_played_ytd_before)
        winner_tb_pct_ytd.append(round(winner_tb_pct_ytd_val, 2))
        
        loser_tb_won_ytd.append(loser_tb_won_ytd_before)
        loser_tb_played_ytd.append(loser_tb_played_ytd_before)
        loser_tb_pct_ytd.append(round(loser_tb_pct_ytd_val, 2))
        
        # Career Tiebreaks
        winner_tb_won_career.append(winner_tb_won_career_before)
        winner_tb_played_career.append(winner_tb_played_career_before)
        winner_tb_pct_career.append(round(winner_tb_pct_career_val, 2))
        
        loser_tb_won_career.append(loser_tb_won_career_before)
        loser_tb_played_career.append(loser_tb_played_career_before)
        loser_tb_pct_career.append(round(loser_tb_pct_career_val, 2))
        
        # Update counters AFTER recording stats for this match
        # YTD
        yearly_bp_won[winner][year] += winner_bp_saved
        yearly_bp_faced[winner][year] += winner_bp_faced_match
        yearly_bp_won[loser][year] += loser_bp_saved
        yearly_bp_faced[loser][year] += loser_bp_faced_match
        
        yearly_tb_won[winner][year] += winner_tb_won_match
        yearly_tb_played[winner][year] += winner_tb_played_match
        yearly_tb_won[loser][year] += loser_tb_won_match
        yearly_tb_played[loser][year] += loser_tb_played_match
        
        # Career
        career_bp_won[winner] += winner_bp_saved
        career_bp_faced[winner] += winner_bp_faced_match
        career_bp_won[loser] += loser_bp_saved
        career_bp_faced[loser] += loser_bp_faced_match
        
        career_tb_won[winner] += winner_tb_won_match
        career_tb_played[winner] += winner_tb_played_match
        career_tb_won[loser] += loser_tb_won_match
        career_tb_played[loser] += loser_tb_played_match
    
    # Add computed columns to dataframe
    # Breakpoint stats - YTD
    df_sorted['winner_bp_won_ytd'] = winner_bp_won_ytd
    df_sorted['winner_bp_faced_ytd'] = winner_bp_faced_ytd
    df_sorted['winner_bp_pct_ytd'] = winner_bp_pct_ytd
    df_sorted['loser_bp_won_ytd'] = loser_bp_won_ytd
    df_sorted['loser_bp_faced_ytd'] = loser_bp_faced_ytd
    df_sorted['loser_bp_pct_ytd'] = loser_bp_pct_ytd
    
    # Breakpoint stats - Career
    df_sorted['winner_bp_won_career'] = winner_bp_won_career
    df_sorted['winner_bp_faced_career'] = winner_bp_faced_career
    df_sorted['winner_bp_pct_career'] = winner_bp_pct_career
    df_sorted['loser_bp_won_career'] = loser_bp_won_career
    df_sorted['loser_bp_faced_career'] = loser_bp_faced_career
    df_sorted['loser_bp_pct_career'] = loser_bp_pct_career
    
    # Tiebreak stats - YTD
    df_sorted['winner_tb_won_ytd'] = winner_tb_won_ytd
    df_sorted['winner_tb_played_ytd'] = winner_tb_played_ytd
    df_sorted['winner_tb_pct_ytd'] = winner_tb_pct_ytd
    df_sorted['loser_tb_won_ytd'] = loser_tb_won_ytd
    df_sorted['loser_tb_played_ytd'] = loser_tb_played_ytd
    df_sorted['loser_tb_pct_ytd'] = loser_tb_pct_ytd
    
    # Tiebreak stats - Career
    df_sorted['winner_tb_won_career'] = winner_tb_won_career
    df_sorted['winner_tb_played_career'] = winner_tb_played_career
    df_sorted['winner_tb_pct_career'] = winner_tb_pct_career
    df_sorted['loser_tb_won_career'] = loser_tb_won_career
    df_sorted['loser_tb_played_career'] = loser_tb_played_career
    df_sorted['loser_tb_pct_career'] = loser_tb_pct_career
    
    return df_sorted

def main():
    """Main function to process ATP matches and compute breakpoint/tiebreak statistics."""
    
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    input_file = os.path.join(project_dir, 'parsed_data', '04_atp_matches.csv')
    output_file = os.path.join(project_dir, 'parsed_data', '05_atp_matches.csv')
    
    print("=" * 60)
    print("ATP Matches - Breakpoint and Tiebreak Statistics Computer")
    print("=" * 60)
    print()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        print("Please run 04_win_computer.py first.")
        return
    
    # Read input data
    print(f"📂 Reading data from: {input_file}")
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} matches")
    print()
    
    # Compute breakpoint and tiebreak statistics
    df_with_stats = compute_breakpoint_and_tiebreak_stats(df)
    
    # Save results
    print()
    print(f"💾 Saving results to: {output_file}")
    df_with_stats.to_csv(output_file, index=False)
    print(f"   Saved {len(df_with_stats):,} matches with breakpoint and tiebreak stats")
    print()
    
    # Display sample statistics
    print("📊 Sample statistics (first 5 matches):")
    print()
    sample_cols = [
        'tournament_date', 'winner_player_name', 'loser_player_name',
        'final_score',
        'winner_bp_pct_ytd', 'winner_bp_pct_career',
        'winner_tb_played_ytd', 'winner_tb_played_career'
    ]
    print(df_with_stats[sample_cols].head())
    print()
    
    print("=" * 60)
    print("✅ Processing complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
