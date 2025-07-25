import streamlit as st
import pandas as pd
from collections import defaultdict
import plotly.graph_objects as go
st.set_page_config(page_title="Matchracing Result Tracker",layout="wide")
# Chargement des données
df = pd.read_json('all_match_results.json')

# Titre principal
st.title("🏆 Skipper Stats & Leaderboard")

# Menu latéral
menu = st.sidebar.selectbox("Menu", ["🔍 Rechercher un skipper", "📊 Leaderboard"])

if menu == "🔍 Rechercher un skipper":
    skipper = st.text_input("Nom du skipper", "Simon Bertheau").lower()

    if skipper:
        matches = df[(df['winner'].str.lower() == skipper) | (df['loser'].str.lower() == skipper)]

        if matches.empty:
            st.warning("Aucun match trouvé pour ce skipper.")
        else:
            qualification_matches = matches[matches['race'] == 0]
            final_matches = matches[matches['race'] != 0]

            qual_total = len(qualification_matches)
            qual_wins = (qualification_matches['winner'].str.lower() == skipper).sum()
            qual_winrate = qual_wins / qual_total if qual_total > 0 else 0.0

            final_total = len(final_matches)
            final_wins = (final_matches['winner'].str.lower() == skipper).sum()
            final_winrate = final_wins / final_total if final_total > 0 else 0.0

            global_total = len(matches)
            global_wins = (matches['winner'].str.lower() == skipper).sum()
            global_winrate = global_wins / global_total if global_total > 0 else 0.0

            st.subheader("📋 Statistiques")
            
           
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🏁 Nombre de match disputés", f"{global_total}", delta=None)
                st.metric("🌍 Global Winrate", f"{global_winrate:.2%}", delta=None)

            with col2:
                st.metric("🏁 Nombre de Victoires", f"{global_wins}", delta=None)
                st.metric("🏁 Phase Qualif Winrate", f"{qual_winrate:.2%}", delta=None)

            with col3:
                st.metric("👑 Phase Finale Winrate", f"{final_winrate:.2%}", delta=None)

            


            c1,c2 = st.columns(2)

            

            # Pires adversaires
            losses = matches[matches['loser'].str.lower() == skipper]
            worst_counts = losses['winner'].value_counts()
            wins_against = matches[
                (matches['winner'].str.lower() == skipper) &
                (matches['loser'].isin(worst_counts.index))
            ]['loser'].value_counts()

            worst_opponents = pd.DataFrame({
                'Adversaire': worst_counts.index,
                'Défaites': worst_counts.values,
                'Victoires': worst_counts.index.map(wins_against).fillna(0).astype(int)
            })
            worst_opponents['Matchs'] = worst_opponents['Victoires'] + worst_opponents['Défaites']
            worst_opponents['Winrate'] = (worst_opponents['Victoires'] / worst_opponents['Matchs'] * 100).round(2)
            worst_opponents = worst_opponents.sort_values(by='Défaites', ascending=False)

            with c1:
                st.subheader("😖 Pires adversaires")
                st.dataframe(worst_opponents)

            # Meilleurs adversaires
            wins = matches[matches['winner'].str.lower() == skipper]
            best_counts = wins['loser'].value_counts()
            losses_against = matches[
                (matches['loser'].str.lower() == skipper) &
                (matches['winner'].isin(best_counts.index))
            ]['winner'].value_counts()

            best_opponents = pd.DataFrame({
                'Adversaire': best_counts.index,
                'Victoires': best_counts.values,
                'Défaites': best_counts.index.map(losses_against).fillna(0).astype(int)
            })
            best_opponents['Matchs'] = best_opponents['Victoires'] + best_opponents['Défaites']
            best_opponents['Winrate'] = (best_opponents['Victoires'] / best_opponents['Matchs'] * 100).round(2)
            best_opponents = best_opponents.sort_values(by='Victoires', ascending=False)
            with c2:
                st.subheader("😎 Meilleurs adversaires")
                st.dataframe(best_opponents)

            st.subheader("📁 Détails des matchs")
            st.dataframe(matches)

elif menu == "📊 Leaderboard":
    stats = defaultdict(lambda: {'wins': 0, 'losses': 0})
    for _, row in df.iterrows():
        stats[row['winner']]['wins'] += 1
        stats[row['loser']]['losses'] += 1

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

    min_matches = st.slider("Nombre minimum de matchs", 0, 200, 100)
    filtered = summary[summary['matches'] >= min_matches]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏅 Meilleur Winrate")
        top_winrate = filtered.sort_values(by='winrate', ascending=False).reset_index(drop=True)
        st.dataframe(top_winrate)

        st.subheader("🏅 Plus grand nombre de matchs")
        top_winrate = filtered.sort_values(by='matches', ascending=False).reset_index(drop=True)
        st.dataframe(top_winrate)


    with col2:
        st.subheader("🥇 Plus de victoires")
        top_winners = filtered.sort_values(by='wins', ascending=False).reset_index(drop=True)
        st.dataframe(top_winners)
