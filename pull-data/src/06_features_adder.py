#!/usr/bin/env python3
"""
ATP Matches Feature Engineering
Adds advanced features for machine learning prediction:
- Surface-specific win rates (Clay, Grass, Hard)
- Ranking differential and features
- Recent form/momentum (last 5, 10 matches)
- Fatigue indicators (days since last match)
- Serve statistics (first serve %, ace rate, DF rate)
- Home advantage
- Experience metrics
- Additional performance indicators

Reads from parsed_data/05_atp_matches.csv and outputs to parsed_data/06_atp_matches.csv
"""

import pandas as pd
import numpy as np
import os
from collections import defaultdict
from datetime import datetime, timedelta

def compute_surface_specific_stats(df):
    """Compute win rates by surface (Clay, Grass, Hard)."""
    print("🎾 Computing surface-specific statistics...")
    
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Track wins and losses by surface
    # player -> surface -> [wins, losses]
    surface_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    
    # Lists for output
    winner_clay_wins = []
    winner_clay_losses = []
    winner_clay_pct = []
    winner_grass_wins = []
    winner_grass_losses = []
    winner_grass_pct = []
    winner_hard_wins = []
    winner_hard_losses = []
    winner_hard_pct = []
    
    loser_clay_wins = []
    loser_clay_losses = []
    loser_clay_pct = []
    loser_grass_wins = []
    loser_grass_losses = []
    loser_grass_pct = []
    loser_hard_wins = []
    loser_hard_losses = []
    loser_hard_pct = []
    
    for idx, row in df_sorted.iterrows():
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        surface = row['court_surface']
        
        # Get stats BEFORE this match
        w_clay = surface_stats[winner]['Clay']
        w_grass = surface_stats[winner]['Grass']
        w_hard = surface_stats[winner]['Hard']
        
        l_clay = surface_stats[loser]['Clay']
        l_grass = surface_stats[loser]['Grass']
        l_hard = surface_stats[loser]['Hard']
        
        # Calculate percentages
        def calc_pct(wins, losses):
            total = wins + losses
            return (wins / total * 100) if total > 0 else 0.0
        
        # Winner stats
        winner_clay_wins.append(w_clay[0])
        winner_clay_losses.append(w_clay[1])
        winner_clay_pct.append(round(calc_pct(w_clay[0], w_clay[1]), 2))
        
        winner_grass_wins.append(w_grass[0])
        winner_grass_losses.append(w_grass[1])
        winner_grass_pct.append(round(calc_pct(w_grass[0], w_grass[1]), 2))
        
        winner_hard_wins.append(w_hard[0])
        winner_hard_losses.append(w_hard[1])
        winner_hard_pct.append(round(calc_pct(w_hard[0], w_hard[1]), 2))
        
        # Loser stats
        loser_clay_wins.append(l_clay[0])
        loser_clay_losses.append(l_clay[1])
        loser_clay_pct.append(round(calc_pct(l_clay[0], l_clay[1]), 2))
        
        loser_grass_wins.append(l_grass[0])
        loser_grass_losses.append(l_grass[1])
        loser_grass_pct.append(round(calc_pct(l_grass[0], l_grass[1]), 2))
        
        loser_hard_wins.append(l_hard[0])
        loser_hard_losses.append(l_hard[1])
        loser_hard_pct.append(round(calc_pct(l_hard[0], l_hard[1]), 2))
        
        # Update stats AFTER recording
        surface_stats[winner][surface][0] += 1  # Win
        surface_stats[loser][surface][1] += 1   # Loss
    
    # Add columns
    df_sorted['winner_clay_wins'] = winner_clay_wins
    df_sorted['winner_clay_losses'] = winner_clay_losses
    df_sorted['winner_clay_win_pct'] = winner_clay_pct
    df_sorted['winner_grass_wins'] = winner_grass_wins
    df_sorted['winner_grass_losses'] = winner_grass_losses
    df_sorted['winner_grass_win_pct'] = winner_grass_pct
    df_sorted['winner_hard_wins'] = winner_hard_wins
    df_sorted['winner_hard_losses'] = winner_hard_losses
    df_sorted['winner_hard_win_pct'] = winner_hard_pct
    
    df_sorted['loser_clay_wins'] = loser_clay_wins
    df_sorted['loser_clay_losses'] = loser_clay_losses
    df_sorted['loser_clay_win_pct'] = loser_clay_pct
    df_sorted['loser_grass_wins'] = loser_grass_wins
    df_sorted['loser_grass_losses'] = loser_grass_losses
    df_sorted['loser_grass_win_pct'] = loser_grass_pct
    df_sorted['loser_hard_wins'] = loser_hard_wins
    df_sorted['loser_hard_losses'] = loser_hard_losses
    df_sorted['loser_hard_win_pct'] = loser_hard_pct
    
    return df_sorted

def compute_recent_form(df):
    """Compute recent form - wins in last 5 and 10 matches."""
    print("📈 Computing recent form statistics...")
    
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Track recent results for each player
    # player -> list of recent results (1=win, 0=loss)
    recent_results = defaultdict(list)
    
    winner_last5_wins = []
    winner_last10_wins = []
    loser_last5_wins = []
    loser_last10_wins = []
    
    for idx, row in df_sorted.iterrows():
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        
        # Get recent form BEFORE this match
        w_results = recent_results[winner]
        l_results = recent_results[loser]
        
        # Count wins in last 5 and 10 matches
        winner_last5_wins.append(sum(w_results[-5:]))
        winner_last10_wins.append(sum(w_results[-10:]))
        loser_last5_wins.append(sum(l_results[-5:]))
        loser_last10_wins.append(sum(l_results[-10:]))
        
        # Update results AFTER recording
        recent_results[winner].append(1)  # Winner won
        recent_results[loser].append(0)   # Loser lost
    
    df_sorted['winner_last5_wins'] = winner_last5_wins
    df_sorted['winner_last10_wins'] = winner_last10_wins
    df_sorted['loser_last5_wins'] = loser_last5_wins
    df_sorted['loser_last10_wins'] = loser_last10_wins
    
    return df_sorted

def compute_fatigue_and_experience(df):
    """Compute days since last match and total career matches."""
    print("⏱️  Computing fatigue and experience metrics...")
    
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Track last match date and total matches
    last_match_date = {}
    total_matches = defaultdict(int)
    
    winner_days_since_last = []
    loser_days_since_last = []
    winner_career_matches = []
    loser_career_matches = []
    
    for idx, row in df_sorted.iterrows():
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        match_date = pd.to_datetime(str(row['tournament_date']), format='%Y%m%d')
        
        # Calculate days since last match
        if winner in last_match_date:
            days_diff = (match_date - last_match_date[winner]).days
            winner_days_since_last.append(days_diff)
        else:
            winner_days_since_last.append(np.nan)
        
        if loser in last_match_date:
            days_diff = (match_date - last_match_date[loser]).days
            loser_days_since_last.append(days_diff)
        else:
            loser_days_since_last.append(np.nan)
        
        # Career matches before this one
        winner_career_matches.append(total_matches[winner])
        loser_career_matches.append(total_matches[loser])
        
        # Update AFTER recording
        last_match_date[winner] = match_date
        last_match_date[loser] = match_date
        total_matches[winner] += 1
        total_matches[loser] += 1
    
    df_sorted['winner_days_since_last_match'] = winner_days_since_last
    df_sorted['loser_days_since_last_match'] = loser_days_since_last
    df_sorted['winner_career_matches'] = winner_career_matches
    df_sorted['loser_career_matches'] = loser_career_matches
    
    return df_sorted

def compute_serve_stats(df):
    """Compute serve statistics - first serve %, ace rate, DF rate."""
    print("🎯 Computing serve statistics...")
    
    df_sorted = df.sort_values(['tournament_date', 'match_number']).copy()
    
    # Track serve stats
    # player -> [first_serves_in, first_serves_total, aces, dfs, service_games]
    serve_stats = defaultdict(lambda: [0, 0, 0, 0, 0])
    
    winner_first_serve_pct_career = []
    winner_aces_per_service_game = []
    winner_df_per_service_game = []
    loser_first_serve_pct_career = []
    loser_aces_per_service_game = []
    loser_df_per_service_game = []
    
    for idx, row in df_sorted.iterrows():
        winner = row['winner_player_name']
        loser = row['loser_player_name']
        
        # Get match stats
        w_first_in = row['winner_first_serves_in'] if pd.notna(row['winner_first_serves_in']) else 0
        w_serve_pts = row['winner_serve_points_total'] if pd.notna(row['winner_serve_points_total']) else 0
        w_aces = row['winner_aces'] if pd.notna(row['winner_aces']) else 0
        w_dfs = row['winner_double_faults'] if pd.notna(row['winner_double_faults']) else 0
        w_service_games = row['winner_service_games'] if pd.notna(row['winner_service_games']) else 0
        
        l_first_in = row['loser_first_serves_in'] if pd.notna(row['loser_first_serves_in']) else 0
        l_serve_pts = row['loser_serve_points_total'] if pd.notna(row['loser_serve_points_total']) else 0
        l_aces = row['loser_aces'] if pd.notna(row['loser_aces']) else 0
        l_dfs = row['loser_double_faults'] if pd.notna(row['loser_double_faults']) else 0
        l_service_games = row['loser_service_games'] if pd.notna(row['loser_service_games']) else 0
        
        # Get career stats BEFORE this match
        w_stats = serve_stats[winner]
        l_stats = serve_stats[loser]
        
        # Calculate career percentages/rates
        w_first_pct = (w_stats[0] / w_stats[1] * 100) if w_stats[1] > 0 else 0.0
        w_ace_rate = (w_stats[2] / w_stats[4]) if w_stats[4] > 0 else 0.0
        w_df_rate = (w_stats[3] / w_stats[4]) if w_stats[4] > 0 else 0.0
        
        l_first_pct = (l_stats[0] / l_stats[1] * 100) if l_stats[1] > 0 else 0.0
        l_ace_rate = (l_stats[2] / l_stats[4]) if l_stats[4] > 0 else 0.0
        l_df_rate = (l_stats[3] / l_stats[4]) if l_stats[4] > 0 else 0.0
        
        winner_first_serve_pct_career.append(round(w_first_pct, 2))
        winner_aces_per_service_game.append(round(w_ace_rate, 2))
        winner_df_per_service_game.append(round(w_df_rate, 2))
        
        loser_first_serve_pct_career.append(round(l_first_pct, 2))
        loser_aces_per_service_game.append(round(l_ace_rate, 2))
        loser_df_per_service_game.append(round(l_df_rate, 2))
        
        # Update AFTER recording
        serve_stats[winner][0] += w_first_in
        serve_stats[winner][1] += w_serve_pts
        serve_stats[winner][2] += w_aces
        serve_stats[winner][3] += w_dfs
        serve_stats[winner][4] += w_service_games
        
        serve_stats[loser][0] += l_first_in
        serve_stats[loser][1] += l_serve_pts
        serve_stats[loser][2] += l_aces
        serve_stats[loser][3] += l_dfs
        serve_stats[loser][4] += l_service_games
    
    df_sorted['winner_first_serve_pct_career'] = winner_first_serve_pct_career
    df_sorted['winner_aces_per_service_game'] = winner_aces_per_service_game
    df_sorted['winner_df_per_service_game'] = winner_df_per_service_game
    
    df_sorted['loser_first_serve_pct_career'] = loser_first_serve_pct_career
    df_sorted['loser_aces_per_service_game'] = loser_aces_per_service_game
    df_sorted['loser_df_per_service_game'] = loser_df_per_service_game
    
    return df_sorted

def compute_additional_features(df):
    """Compute additional derived features."""
    print("🔧 Computing additional features...")
    
    # Ranking differential (lower rank number is better)
    df['rank_diff'] = df['loser_atp_rank'] - df['winner_atp_rank']
    
    # Home advantage (1 if playing in home country, 0 otherwise)
    # Simple approach: check if country code appears in tournament name
    df['winner_is_home'] = 0
    df['loser_is_home'] = 0
    
    # Country-tournament mapping (common patterns)
    country_keywords = {
        'AUS': ['Australian', 'Brisbane', 'Sydney', 'Melbourne', 'Adelaide'],
        'USA': ['US Open', 'Indian Wells', 'Miami', 'Cincinnati', 'Washington', 'Atlanta', 'Houston', 'Newport', 'San Diego', 'Los Angeles', 'Las Vegas'],
        'FRA': ['French Open', 'Roland Garros', 'Paris', 'Lyon', 'Marseille', 'Montpellier', 'Metz'],
        'GBR': ['Wimbledon', 'London', 'Queens', 'Eastbourne', 'Birmingham', 'Nottingham'],
        'ESP': ['Madrid', 'Barcelona', 'Valencia', 'Mallorca'],
        'ITA': ['Rome', 'Italian Open', 'Milan', 'Florence'],
        'GER': ['Hamburg', 'Munich', 'Halle', 'Stuttgart'],
        'CHN': ['Shanghai', 'Beijing', 'Shenzhen'],
        'JPN': ['Tokyo', 'Japan Open'],
        'CAN': ['Montreal', 'Toronto', 'Rogers Cup', 'Canada'],
        'NED': ['Rotterdam', 'Netherlands'],
        'SUI': ['Basel', 'Geneva'],
        'BRA': ['Rio', 'Sao Paulo', 'Brazil'],
        'ARG': ['Buenos Aires', 'Argentina'],
        'RSA': ['South Africa'],
        'SWE': ['Stockholm', 'Sweden'],
        'AUT': ['Vienna', 'Austria']
    }
    
    for country, keywords in country_keywords.items():
        for keyword in keywords:
            mask = df['tournament_name'].str.contains(keyword, case=False, na=False)
            df.loc[mask & (df['winner_country_code'] == country), 'winner_is_home'] = 1
            df.loc[mask & (df['loser_country_code'] == country), 'loser_is_home'] = 1
    
    # Height differential
    df['height_diff_cm'] = df['winner_height_cm'] - df['loser_height_cm']
    
    # Age differential
    df['age_diff_years'] = df['winner_age_years'] - df['loser_age_years']
    
    # ATP points differential
    df['atp_points_diff'] = df['winner_atp_points'] - df['loser_atp_points']
    
    # Experience differential (career matches)
    df['experience_diff'] = df['winner_career_matches'] - df['loser_career_matches']
    
    # Momentum indicators (recent form differential)
    df['momentum_last5'] = df['winner_last5_wins'] - df['loser_last5_wins']
    df['momentum_last10'] = df['winner_last10_wins'] - df['loser_last10_wins']
    
    # Head-to-head differential
    df['h2h_diff'] = df['winner_h2h_wins'] - df['loser_h2h_wins']
    
    # YTD performance differential
    df['ytd_win_pct_diff'] = df['winner_win_pct_ytd'] - df['loser_win_pct_ytd']
    
    # Surface-specific performance differential (on current surface)
    df['surface_win_pct_diff'] = 0.0
    for surface in ['Clay', 'Grass', 'Hard']:
        mask = df['court_surface'] == surface
        col_name = f'winner_{surface.lower()}_win_pct'
        loser_col_name = f'loser_{surface.lower()}_win_pct'
        if col_name in df.columns and loser_col_name in df.columns:
            df.loc[mask, 'surface_win_pct_diff'] = df.loc[mask, col_name] - df.loc[mask, loser_col_name]
    
    # Seeding differential (lower seed number is better, handle NaN)
    df['seed_diff'] = df['loser_tournament_seed'].fillna(999) - df['winner_tournament_seed'].fillna(999)
    
    # Is upset? (lower ranked player won)
    df['is_upset'] = (df['winner_atp_rank'] > df['loser_atp_rank']).astype(int)
    
    # Match importance (based on round)
    round_importance = {
        'F': 7,
        'SF': 6,
        'QF': 5,
        'R16': 4,
        'R32': 3,
        'R64': 2,
        'R128': 1,
        'RR': 3,  # Round Robin
        'BR': 1   # Bronze Medal
    }
    df['round_importance'] = df['tournament_round'].map(round_importance).fillna(1)
    
    return df

def main():
    """Main function to add advanced features."""
    
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    input_file = os.path.join(project_dir, 'parsed_data', '05_atp_matches.csv')
    output_file = os.path.join(project_dir, 'parsed_data', '06_atp_matches.csv')
    
    print("=" * 70)
    print("ATP Matches - Advanced Feature Engineering")
    print("=" * 70)
    print()
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file not found: {input_file}")
        print("Please run 05_breakpoints_and_tiebreak_computer.py first.")
        return
    
    # Read input data
    print(f"📂 Reading data from: {input_file}")
    df = pd.read_csv(input_file)
    print(f"   Loaded {len(df):,} matches")
    print()
    
    # Compute surface-specific stats
    df = compute_surface_specific_stats(df)
    
    # Compute recent form
    df = compute_recent_form(df)
    
    # Compute fatigue and experience
    df = compute_fatigue_and_experience(df)
    
    # Compute serve statistics
    df = compute_serve_stats(df)
    
    # Compute additional features
    df = compute_additional_features(df)
    
    # Save results
    print()
    print(f"💾 Saving results to: {output_file}")
    df.to_csv(output_file, index=False)
    print(f"   Saved {len(df):,} matches with {len(df.columns)} features")
    print()
    
    # Display sample statistics
    print("📊 New features added:")
    new_features = [
        'Surface-specific win rates (Clay/Grass/Hard)',
        'Recent form (last 5 and 10 matches)',
        'Days since last match (fatigue)',
        'Career matches (experience)',
        'First serve % career',
        'Aces per service game',
        'Double faults per service game',
        'Ranking differential',
        'Home advantage indicators',
        'Height/Age/Points differentials',
        'Momentum indicators',
        'H2H differential',
        'Surface performance differential',
        'Upset indicator',
        'Round importance'
    ]
    for i, feature in enumerate(new_features, 1):
        print(f"   {i:2d}. {feature}")
    
    print()
    print(f"📈 Total columns: {len(df.columns)}")
    print()
    
    # Show sample data
    print("📋 Sample of new features (first match):")
    feature_cols = [
        'winner_player_name', 'loser_player_name',
        'rank_diff', 'momentum_last5', 'surface_win_pct_diff',
        'winner_days_since_last_match', 'winner_career_matches',
        'is_upset', 'round_importance'
    ]
    available_cols = [col for col in feature_cols if col in df.columns]
    print(df[available_cols].head(1).T)
    print()
    
    print("=" * 70)
    print("✅ Feature engineering complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()
