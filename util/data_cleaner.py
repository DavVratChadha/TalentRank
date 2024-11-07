import util


#turn xlsx to csv
util.xlsx_to_csv("Business Intelligence Analyst Role (Requisition 2) - Screening Questions Responses (RR Final).xlsx", "screening_questions_2.csv")
util.xlsx_to_csv("Business Intelligence Analyst Role (Requisition 2) - Candidate Details (RR Final).xlsx", "candidate_details_2.csv")
util.xlsx_to_csv("Shortlisted.xlsx", "shortlisted_1.csv")
util.xlsx_to_csv("Business Intelligence Analyst Role (Requisition 2) - Education history.xlsx", "education_details_2.csv")

# load csv as dataframe
screening_questions_df = util.load_csv_as_df("screening_questions_1.csv")
candidate_details_df = util.load_csv_as_df("candidate_details_1.csv")
shortlisted_df = util.load_csv_as_df("shortlisted_1.csv")


unique_questions = screening_questions_df["Screening Form Question"].unique()

screening_filename = "screening_questions_1.txt"
for question in unique_questions:
    with open(screening_filename, "a") as file:
        file.write(f"\n\nScreening Question: {question}")
    
        #for each question get the unique answers and their counts
        question_df = screening_questions_df[screening_questions_df["Screening Form Question"] == question]
        unique_answers = question_df["Screening Question Form Answer"].unique()
        #also get the counts
        for answer in unique_answers:
            count = len(question_df[question_df["Screening Question Form Answer"] == answer])
            file.write(f"\nAnswer: {answer} Count: {count}")
    
    