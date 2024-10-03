import pandas as pd
from abc import ABC, abstractmethod
from typing import List


class DataCleaner:
    """Handles cleaning of student data."""

    def clean_data(self, data, method="fill_mean"):
        """
        Cleans the dataset by handling NaN values.
        :param method: The method to clean data. Options are:
            - 'drop': Drop rows with any NaN.
            - 'fill_zero': Replace NaN with 0.
            - 'fill_mean': Replace NaN with the mean of the respective column.
            - 'fill_median': Replace NaN with the median of the respective column.
            - 'fill_ffill': Use forward fill to replace NaN.
            - 'fill_bfill': Use backward fill to replace NaN.
        :return: Cleaned DataFrame.
        """
        if method == "drop":
            cleaned_data = data.dropna()
        elif method == "fill_zero":
            cleaned_data = data.fillna(0)
        elif method == "fill_mean":
            cleaned_data = data.fillna(data.mean(numeric_only=True))
        elif method == "fill_median":
            cleaned_data = data.fillna(data.median(numeric_only=True))
        elif method == "fill_ffill":
            cleaned_data = data.fillna(method="ffill")
        elif method == "fill_bfill":
            cleaned_data = data.fillna(method="bfill")
        else:
            raise ValueError(f"Unknown cleaning method: {method}")

        return cleaned_data


class IDataHandler(ABC):
    """Interface for data handling."""

    @abstractmethod
    def load_data(self, filepath: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_data(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_subjects(self) -> List[str]:
        pass

    @abstractmethod
    def clean(self, method='drop'):
        pass


class IFileWriter(ABC):
    """Interface for writing files."""

    @abstractmethod
    def save(self, data: pd.DataFrame, file_path: str) -> None:
        pass


class IAnalyzer(ABC):
    """Interface for data analysis."""

    @abstractmethod
    def get_highest_averages(self, data):
        pass

    @abstractmethod
    def get_hardest_subjects(self, data):
        pass

    @abstractmethod
    def get_improved_students(self, data):
        pass

    @abstractmethod
    def get_failed_students(self, data):
        pass

    @abstractmethod
    def get_subject_semester_averages(self, data):
        pass

    @abstractmethod
    def get_average_per_semester(self, data):
        pass


class DataHandler(IDataHandler):
    """Handles data loading and subject extraction."""

    def __init__(self, cleaner: DataCleaner, input_file: str = None):
        self.cleaner = cleaner
        self.data = None
        if input_file is not None:
            self.load_data(input_file)

    def load_data(self, file_path: str) -> None:
        self.data = pd.read_csv(file_path)

    def get_data(self) -> pd.DataFrame:
        return self.data

    def get_subjects(self) -> List[str]:
        return self.data.columns.difference(['Student', 'Semester'])

    def clean(self, method='drop'):
        self.data = self.cleaner.clean_data(self.data, method)


class ExcelFileWriter(IFileWriter):
    """Handles writing data to an Excel file."""

    def save(self, data: pd.DataFrame, file_path: str) -> None:
        data.to_excel(file_path, index=True, engine='openpyxl')


class Analyzer(IAnalyzer):
    def __init__(self):
        self.non_subjects = ['Student', 'Semester']

    def get_failed_students(self, data):
        subject_columns = self.get_subjects(data)
        failed_students = data[data[subject_columns].lt(50).any(axis=1)]['Student']
        return failed_students.unique()

    def get_subject_semester_averages(self, data):
        subject_columns = self.get_subjects(data)
        return data.groupby('Semester')[subject_columns].mean()

    def get_highest_averages(self, data):
        subject_columns = self.get_subjects(data)
        average_grades = data.groupby(self.non_subjects)[subject_columns].mean().reset_index()
        average_grades['Overall Average'] = average_grades[subject_columns].mean(axis=1)
        average_grades = average_grades.groupby('Student')['Overall Average'].mean().reset_index()
        return average_grades.max()
        # max_overall_avg = average_grades.groupby('Semester')['Overall Average'].max().reset_index()
        # result_per_semester = pd.merge(max_overall_avg, average_grades, on=['Semester', 'Overall Average'], how='inner')
        # average_scores = data.groupby('Student').mean(numeric_only=True).reset_index()
        #
        # highest_scores = {}
        #
        # for subject in subject_columns:
        #     max_score = average_scores[subject].max()
        #     students_with_max = average_scores[average_scores[subject] == max_score]['Student'].unique()
        #     highest_scores[subject] = {
        #         'Max Score': max_score,
        #         'Students': students_with_max
        #     }
        #
        # return highest_scores.items(), result_per_semester

    def get_hardest_subjects(self, data):
        subject_columns = self.get_subjects(data)
        subject_averages = data.groupby('Semester')[subject_columns].mean()
        lowest_averages = subject_averages.idxmin(axis=1)
        lowest_avg_values = subject_averages.min(axis=1)
        result = pd.DataFrame({
            'Semester': lowest_averages.index,
            'Subject': lowest_averages.values,
            'Average Score': lowest_avg_values.values
        })
        return result

    def get_improved_students(self, data):
        subjects_column = self.get_subjects(data)
        df = data.groupby(self.non_subjects)[subjects_column].sum().reset_index()
        df['Total Score'] = df[subjects_column].sum(axis=1)
        increasing = df['Total Score'].lt(df.groupby('Student')['Total Score'].shift(-1))
        increase_group = increasing.groupby(df['Student'], group_keys=False).apply(lambda v: v.ne(v.shift(1))).cumsum()
        consec_increases = increasing.groupby(increase_group).transform(lambda v: v.cumsum().max())
        inds_per_group = (
            increase_group[consec_increases >= 3]
            .groupby(increase_group)
            .apply(lambda g: list(g.index) + [max(g.index) + 1])
        )

        out_df = pd.concat(df.loc[inds].assign(group=i) for i, inds in enumerate(inds_per_group))
        return out_df['Student'].unique()

    def get_subjects(self, data):
        return data.columns.difference(self.non_subjects)

    def get_average_per_semester(self, data):
        subjects_column = self.get_subjects(data)
        data['Semester Average'] = data[subjects_column].mean(axis=1)
        semester_averages = data.groupby('Semester')['Semester Average'].mean()

        return semester_averages
