import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


class StatsAnalyzer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.df = pd.read_csv(log_file)

    def analyze_best_decks(self):
        """Analyze deck performance based on waves survived and game duration."""
        # Group by deck composition and calculate mean stats
        deck_stats = self.df.groupby('deck_composition').agg({
            'wave_survived': ['mean', 'count'],
            'game_duration': 'mean'
        }).reset_index()

        # Sort by average waves survived
        deck_stats = deck_stats.sort_values(
            ('wave_survived', 'mean'), ascending=False)

        # Plot results
        plt.figure(figsize=(12, 6))
        plt.bar(range(len(deck_stats)), deck_stats[('wave_survived', 'mean')])
        plt.xticks(
            range(
                len(deck_stats)),
            deck_stats['deck_composition'],
            rotation=45)
        plt.title('Average Waves Survived by Deck Composition')
        plt.tight_layout()
        plt.savefig('deck_performance.png')
        plt.close()

        return deck_stats

    def analyze_skill_popularity(self):
        """Analyze individual skill popularity and effectiveness."""
        # Count skill occurrences across all positions
        all_skills = []
        for i in range(1, 5):
            all_skills.extend(self.df[f'skill{i}'].tolist())

        skill_counts = Counter(all_skills)

        # Calculate average waves for each skill
        skill_performance = {}
        for skill in skill_counts:
            # Find games where this skill was used
            skill_games = self.df[
                (self.df['skill1'] == skill) |
                (self.df['skill2'] == skill) |
                (self.df['skill3'] == skill) |
                (self.df['skill4'] == skill)
            ]
            avg_waves = skill_games['wave_survived'].mean()
            skill_performance[skill] = {
                'count': skill_counts[skill],
                'avg_waves': avg_waves
            }

        # Plot results
        plt.figure(figsize=(12, 6))
        skills = list(skill_counts.keys())
        counts = list(skill_counts.values())
        plt.bar(skills, counts)
        plt.xticks(rotation=45)
        plt.title('Skill Selection Frequency')
        plt.tight_layout()
        plt.savefig('skill_popularity.png')
        plt.close()

        return skill_performance

    def analyze_player_rankings(self):
        """Generate player rankings based on waves survived and game duration."""
        # Get best performance for each player
        player_stats = self.df.groupby('player_name').agg({
            'wave_survived': 'max',
            'game_duration': 'max'
        }).reset_index()

        # Sort by waves survived
        player_stats = player_stats.sort_values(
            'wave_survived', ascending=False)

        # Plot player rankings
        plt.figure(figsize=(12, 6))
        plt.bar(player_stats['player_name'], player_stats['wave_survived'])
        plt.xticks(rotation=45)
        plt.title('Player Rankings by Max Wave Survived')
        plt.tight_layout()
        plt.savefig('player_rankings.png')
        plt.close()

        return player_stats

    def generate_full_report(self):
        """Generate a complete analysis report."""
        print("Generating Game Statistics Report...")
        print("\n1. Best Deck Analysis")
        print("-" * 50)
        deck_stats = self.analyze_best_decks()
        print(deck_stats.head().to_string())

        print("\n2. Skill Popularity and Performance")
        print("-" * 50)
        skill_stats = self.analyze_skill_popularity()
        for skill, stats in skill_stats.items():
            print(
                f"{skill}: Used {
                    stats['count']} times, Avg waves: {
                    stats['avg_waves']:.2f}")

        print("\n3. Player Rankings")
        print("-" * 50)
        player_stats = self.analyze_player_rankings()
        print(player_stats.to_string())

        print("\nGraphs have been saved as:")
        print("- deck_performance.png")
        print("- skill_popularity.png")
        print("- player_rankings.png")


def main():
    analyzer = StatsAnalyzer("log.csv")
    analyzer.generate_full_report()


if __name__ == "__main__":
    main()
