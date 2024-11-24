from util import util
import os


def format_it_correctly_because_stakeholders_are_watching(edu_file, work_file, screening_ques, data_dir):
    try:
        path = os.path.join(data_dir, "work_details.csv")
        util.xlsx_to_csv(work_file, path)
        path = os.path.join(data_dir, "education_details.csv")
        util.xlsx_to_csv(edu_file, path)
        path = os.path.join(data_dir, "screening_questions.csv")
        util.xlsx_to_csv(screening_ques, path)
        
    except Exception as e:
        print("Error in converting xlsx to csv. Are you sure your file format it correct?")
        raise e