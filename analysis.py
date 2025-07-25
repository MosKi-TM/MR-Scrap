import pandas as pd
from collections import defaultdict


df = pd.read_json('all_match_results.json')


# Filter matches involving Tom Foucher
skipper = "simon bertheau"

# Filter matches involving the skipper
matches = df[(df['winner'] == skipper) | (df['loser'] == skipper)]

# Separate qualification and final phase matches
qualification_matches = matches[matches['race'] == 0]
final_matches = matches[matches['race'] != 0]

# Compute stats for qualification phase
qual_total = len(qualification_matches)
qual_wins = (qualification_matches['winner'] == skipper).sum()
qual_winrate = qual_wins / qual_total if qual_total > 0 else 0.0

# Compute stats for final phase
final_total = len(final_matches)
final_wins = (final_matches['winner'] == skipper).sum()
final_winrate = final_wins / final_total if final_total > 0 else 0.0

# Display results
print(f"Qualification Phase (race == 0):")
print(f"  Total Matches: {qual_total}")
print(f"  Winrate: {round(qual_winrate * 100, 2)}%")

print(f"\nFinal Phase (race != 0):")
print(f"  Total Matches: {final_total}")
print(f"  Winrate: {round(final_winrate * 100, 2)}%")



stats = defaultdict(lambda: {'wins': 0, 'losses': 0})

for _, row in df.iterrows():
    stats[row['winner']]['wins'] += 1
    stats[row['loser']]['losses'] += 1

# Create DataFrame from stats
summary = pd.DataFrame([
    {
        'skipper': skipper,
        'wins': values['wins'],
        'losses': values['losses'],
        'matches': values['wins'] + values['losses'],
        'winrate': values['wins'] / (values['wins'] + values['losses']) if (values['wins'] + values['losses']) > 0 else 0.0
    }
    for skipper, values in stats.items()
])

# Filter skippers with at least 100 matches
filtered = summary[summary['matches'] >= 100]

# Sort by winrate descending
top_skippers = filtered.sort_values(by='winrate', ascending=False).reset_index(drop=True)

# Display top skippers
print(top_skippers)