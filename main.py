import pandas as pd

from statistics import IDataHandler, IFileWriter, IAnalyzer, DataHandler, ExcelFileWriter, Analyzer, DataCleaner
from visualizer import DataVisualizer

"""თქვენ გეძლევათ CSV ფაილი (student_scores_random_names.csv), რომელიც შეიცავს სტუდენტთა ქულებს სხვადასხვა საგნებსა და სემესტრებზე. 
თქვენი ამოცანაა გამოიყენოთ pandas ბიბლიოთეკა ამ მონაცემების გასაწმენდად და ანალიზისთვის.


csv ფაილი ჩატვირთენ პანდას დატაფრეიმში და ჩაატარეთ შემდეგი გამოთვლები:

1. გამოიტანეთ იმ სტუდენტთა სია, რომლებმაც არ ჩააბარეს რომელიმე საგანი (ქულა ნაკლებია 50-ზე).
2. თითოეული საგნისთვის გამოთვალეთ საშუალო ქულა თითო სემესტრში.
3. იპოვეთ ის სტუდენტი(ები), რომელთაც აქვთ ყველაზე მაღალი საშუალო ქულა ყველა სემესტრსა და საგანში.
4. იპოვეთ საგანი, რომელშიც სტუდენტებს ყველაზე მეტად გაუჭირდათ (ყველაზე დაბალი საშუალო ქულა ყველა სემესტრში).
5. შექმენით ახალი დატაფრეიმი სადაც დააგენერირებთ საგნების საშუალო ქულებს სემესტრის მიხედვით და შემდეგ შეინახავთ ექსელის ფაილში (ინდექსები შეუსაბამეთ სემესტრებს)

ბონუსი (არასავალდებულო):
6. გამოავლინეთ სტუდენტები, რომლებმაც თანმიმდევრულად გააუმჯობესეს ქულები სემესტრებში.

ვიზუალიზაცია:
შექმენით სვეტების დიაგრამა, რომელიც აჩვენებს თითო საგნის საშუალო ქულას ყველა სემესტრში.
შექმენით ხაზოვანი გრაფიკი, რომელიც აჩვენებს საშუალო საერთო ქულას სემესტრების მიხედვით."""


class ReportGenerator:
    """Generates reports by coordinating various components."""

    def __init__(self, data_handler: IDataHandler, file_writer: IFileWriter, analyzer: IAnalyzer):
        self.data_handler = data_handler
        self.file_writer = file_writer
        self.analyzer = analyzer
        self.visualizer = DataVisualizer()

        # if user wants to work on diff data, it has different options as well
        # ბევრი ვარიანტია იმისი თუ როგორ უნდა გაიწმინდოს დატა და დამოკიდებულია ამოცანა როგორაა დასმული
        # შესაბამისად სხვადასხვა ვარიანტების იმპლემენტაცია არის ფუნქციაში და თვითონ იუზერმა გადაწყვიტოს
        # როგორ ურჩევნია და ზუსტად რისი მიღება უნდა ან NaN რას ნიშნავს ამოცანის ჭრილში
        # self.data_handler.clean()

    def generate_subject_average_report(self, output_file: str):
        data = self.data_handler.get_data()
        avg_per_semester = self.analyzer.get_subject_semester_averages(data)
        self.file_writer.save(avg_per_semester, output_file)
        print("SUBJECT AVERAGES")
        print(avg_per_semester.to_string())
        self.visualizer.plot_subject_averages_per_semester(avg_per_semester)

    def generate_improvement_report(self):
        data = self.data_handler.get_data()
        improved_students = self.analyzer.get_improved_students(data)
        print("IMPROVED STUDENTS")
        print(improved_students)

    def generate_failed_report(self):
        data = self.data_handler.get_data()
        failed_students = self.analyzer.get_failed_students(data)
        print("FAILED STUDENTS")
        print(failed_students)

    def generate_highest_averages_report(self):
        data = self.data_handler.get_data()
        highest_averages = self.analyzer.get_highest_averages(data)
        print("HIGHEST AVERAGES")
        print(highest_averages.to_string())

    def generate_hardest_subjects_report(self):
        data = self.data_handler.get_data()
        hardest_subjects = self.analyzer.get_hardest_subjects(data)
        print("HARDEST SUBJECTS")
        print(hardest_subjects.to_string())

    def generate_semester_average_report(self):
        data = self.data_handler.get_data()
        semester_avg = self.analyzer.get_average_per_semester(data)
        self.visualizer.plot_semester_averages(semester_avg)


def main():
    data_cleaner = DataCleaner()
    data_handler = DataHandler(data_cleaner, input_file='student_scores_random_names.csv')
    file_writer = ExcelFileWriter()
    analyzer = Analyzer()
    report_generator = ReportGenerator(data_handler, file_writer, analyzer)

    avg_output_file = 'average_semester_report.xlsx'
    report_generator.generate_subject_average_report(avg_output_file)
    report_generator.generate_failed_report()
    report_generator.generate_improvement_report()
    report_generator.generate_highest_averages_report()
    report_generator.generate_hardest_subjects_report()
    report_generator.generate_semester_average_report()


if __name__ == "__main__":
    main()
