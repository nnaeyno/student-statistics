import pandas as pd
from abc import ABC, abstractmethod
from typing import List


class DataCleaner:
    """Handles cleaning of student data."""

    def __init__(self, data: pd.DataFrame):
        self.data = data

    def clean_data(self, method="fill_mean"):
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
            cleaned_data = self.data.dropna()
        elif method == "fill_zero":
            cleaned_data = self.data.fillna(0)
        elif method == "fill_mean":
            cleaned_data = self.data.fillna(self.data.mean(numeric_only=True))
        elif method == "fill_median":
            cleaned_data = self.data.fillna(self.data.median(numeric_only=True))
        elif method == "fill_ffill":
            cleaned_data = self.data.fillna(method="ffill")
        elif method == "fill_bfill":
            cleaned_data = self.data.fillna(method="bfill")
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
    def get_semester_averages(self, data):
        pass


class DataHandler(IDataHandler):
    """Handles data loading and subject extraction."""

    def __init__(self, input_file: str = None):
        self.data = None
        if input_file is not None:
            self.load_data(input_file)

    def load_data(self, file_path: str) -> None:
        self.data = pd.read_csv(file_path)

    def get_data(self) -> pd.DataFrame:
        return self.data

    def get_subjects(self) -> List[str]:
        return self.data.columns.difference(['Student', 'Semester'])


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

    def get_semester_averages(self, data):
        subject_columns = self.get_subjects(data)
        return data.groupby('Semester')[subject_columns].mean()

    def get_highest_averages(self, data):
        subject_columns = self.get_subjects(data)
        result = {}

        for subject in subject_columns:
            max_scores_idx = data.groupby('Semester')[subject].idxmax()
            max_scores = data.loc[max_scores_idx, ['Student', 'Semester', subject]].drop_duplicates()
            result[subject] = max_scores
        final_result = pd.concat(result, axis=1)
        unique_students = pd.unique(final_result.xs('Student', axis=1, level=1).values.flatten())

        return unique_students

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
        df = data.sort_values(by=self.non_subjects)
        subject_columns = self.get_subjects(data)
        df['Improvement'] = df.groupby('Student')[subject_columns].diff().fillna(0).ge(0).all(axis=1)
        students_with_improvement = df.groupby('Student').filter(lambda x: x['Improvement'].all())

        return students_with_improvement['Student'].unique()

    def get_subjects(self, data):
        return data.columns.difference(self.non_subjects)

    def get_average_per_semester(self, data):
        subjects_column = self.get_subjects(data)
        avg_per_semester = data.groupby('Semester')[subjects_column].mean(axis=1).mean(axis=1)

        return avg_per_semester
