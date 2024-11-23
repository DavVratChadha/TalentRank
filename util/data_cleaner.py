import util

def format_it_correctly_because_stakeholders_are_watching(edu_file, work_file, screening_ques):
    try:
        util.xlsx_to_csv(work_file, "work_details.csv")
        util.xlsx_to_csv(edu_file, "education_details.csv")
        util.xlsx_to_csv(screening_ques, "screening_questions.csv")
        
    except Exception as e:
        print("Error in converting xlsx to csv. Are you sure your file format it correct?")
        raise e