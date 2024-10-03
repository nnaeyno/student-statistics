import pandas as pd

"""თქვენ გეძლევათ CSV ფაილი (student_scores_random_names.csv), რომელიც შეიცავს სტუდენტთა ქულებს სხვადასხვა საგნებსა და სემესტრებზე. თქვენი ამოცანაა გამოიყენოთ pandas ბიბლიოთეკა ამ მონაცემების გასაწმენდად და ანალიზისთვის.


csv ფაილი ჩატვირთენ პანდას დატაფრეიმში და ჩაატარეთ შემდეგი გამოთვლები:

გამოიტანეთ იმ სტუდენტთა სია, რომლებმაც არ ჩააბარეს რომელიმე საგანი (ქულა ნაკლებია 50-ზე).
თითოეული საგნისთვის გამოთვალეთ საშუალო ქულა თითო სემესტრში.
იპოვეთ ის სტუდენტი(ები), რომელთაც აქვთ ყველაზე მაღალი საშუალო ქულა ყველა სემესტრსა და საგანში.
იპოვეთ საგანი, რომელშიც სტუდენტებს ყველაზე მეტად გაუჭირდათ (ყველაზე დაბალი საშუალო ქულა ყველა სემესტრში).
შექმენით ახალი დატაფრეიმი სადაც დააგენერირებთ საგნების საშუალო ქულებს სემესტრის მიხედვით და შემდეგ შეინახავთ ექსელის ფაილში (ინდექსები შეუსაბამეთ სემესტრებს)

ბონუსი (არასავალდებულო):
გამოავლინეთ სტუდენტები, რომლებმაც თანმიმდევრულად გააუმჯობესეს ქულები სემესტრებში.

ვიზუალიზაცია:
შექმენით სვეტების დიაგრამა, რომელიც აჩვენებს თითო საგნის საშუალო ქულას ყველა სემესტრში.
შექმენით ხაზოვანი გრაფიკი, რომელიც აჩვენებს საშუალო საერთო ქულას სემესტრების მიხედვით."""


def get_highest_averages(df):
    result = {}
    for subject in subject_columns:
        max_scores = df.loc[df.groupby('Semester')[subject].idxmax()][['Student', 'Semester', subject]]
        result[subject] = max_scores
    final_result = pd.concat(result, axis=1)
    return final_result


def get_hardest_subjects(df):
    subject_columns = df.columns.difference(['Student', 'Semester'])
    subject_averages = df.groupby('Semester')[subject_columns].mean()
    lowest_averages = subject_averages.idxmin(axis=1)
    lowest_avg_values = subject_averages.min(axis=1)
    result = pd.DataFrame({
        'Semester': lowest_averages.index,
        'Subject': lowest_averages.values,
        'Average Score': lowest_avg_values.values
    })
    return result


def get_improved_students(df):
    df = df.sort_values(by=['Student', 'Semester'])
    subject_columns = df.columns.difference(['Student', 'Semester'])
    df['Improvement'] = df.groupby('Student')[subject_columns].diff().fillna(0).ge(0).all(axis=1)
    students_with_improvement = df.groupby('Student').filter(lambda x: x['Improvement'].all())

    return students_with_improvement[['Student', 'Semester'] + list(subject_columns)]


df = pd.read_csv('student_scores_random_names.csv')
subject_columns = df.columns.difference(['Student', 'Semester'])
failed_students = df[df[subject_columns].lt(50).any(axis=1)]['Student']
semester_averages = df.groupby('Semester')[subject_columns].mean()
highest_averages = get_highest_averages(df)
hardest_subjects = get_hardest_subjects(df)
semester_averages.to_excel('subject_averages_per_semester.xlsx', index=True)
improved_students = get_improved_students(df)
print(improved_students)
