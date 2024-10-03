import pandas as pd
import matplotlib.pyplot as plt


class DataVisualizer:
    """Handles data visualization."""

    def __init__(self):
        self.subjects = 'Subjects'

    def plot_subject_averages_per_semester(self, data: pd.DataFrame):
        data.plot(kind='bar', figsize=(10, 6))

        plt.title('Average Scores per Subject in Each Semester')
        plt.xlabel('Semester')
        plt.ylabel('Average Score')
        plt.xticks(rotation=0)
        plt.legend(title=self.subjects, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def plot_semester_averages(self, data: pd.DataFrame):
        plt.figure(figsize=(10, 6))
        plt.plot(data.index, data.values, marker='o', linestyle='-', color='b')
        plt.title("Overall Average Scores per Semester")
        plt.xlabel("Semester")
        plt.ylabel("Average Score")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True)
        plt.show()
