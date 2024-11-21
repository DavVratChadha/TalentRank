import pandas as pd
from collections import defaultdict
import json
import preprocessor
import pickle
import numpy as np
from datetime import datetime
import calendar

DATA_DIR = "data/"
MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def process():
    # Read the CSV file, ignoring the first column
    df1 = pd.read_csv(f"{DATA_DIR}screening_questions_1.csv", index_col=0)
    df2 = pd.read_csv(f"{DATA_DIR}screening_questions_2.csv", index_col=0)
    # df3 = pd.read_csv(f"{DATA_DIR}screening_questions_3.csv", index_col=0)
    # df4 = pd.read_csv(f"{DATA_DIR}screening_questions_4.csv", index_col=0)
    # df5 = pd.read_csv(f"{DATA_DIR}screening_questions_5.csv", index_col=0)
    
    #sort each df by Candidate Deidentified ID
    df1.sort_values("Candidate Deidentified ID", inplace=True)
    df2.sort_values("Candidate Deidentified ID", inplace=True)
    # df3.sort_values("Candidate Deidentified ID", inplace=True)
    # df4.sort_values("Candidate Deidentified ID", inplace=True)
    # df5.sort_values("Candidate Deidentified ID", inplace=True)
    

    #need to fix candidate deidentified id
    #first find the id of last candidate in first file
    last_id1 = df1["Candidate Deidentified ID"].iloc[-1]
    #now add this id to the second file
    df2["Candidate Deidentified ID"] = df2["Candidate Deidentified ID"] + last_id1
    last_id2 = df2["Candidate Deidentified ID"].iloc[-1]
    #now add this id to the third file
    # df3["Candidate Deidentified ID"] = df3["Candidate Deidentified ID"] + last_id2
    # last_id3 = df3["Candidate Deidentified ID"].iloc[-1]
    # #now add this id to the fourth file
    # df4["Candidate Deidentified ID"] = df4["Candidate Deidentified ID"] + last_id3
    # last_id4 = df4["Candidate Deidentified ID"].iloc[-1]
    # #now add this id to the fifth file
    # df5["Candidate Deidentified ID"] = df5["Candidate Deidentified ID"] + last_id4
    
    print(f"DF2 starts at {last_id1=}")
    print(f"DF3 starts at {last_id2=}")
    # print(f"DF4 starts at {last_id3=}")
    # print(f"DF5 starts at {last_id4=}")
    
    #combine the dataframes in that order
    df = pd.concat([df1, df2])
    # df = pd.concat([df1, df2, df3, df4, df5])
    #remove duplicate rows
    df.drop_duplicates(inplace=True)

    def answer_question(row):
        question = row["Screening Form Question"].lower()
        answer = row["Screening Form Answer"]
        # if answer is nan, print row number
        if pd.isna(answer):
            print(f"{row.name=}")
            print(f"{question=}")
            print(f"{answer=}")
            print(f'{row["Candidate Deidentified ID"]=}')
            raise ValueError("Answer is nan")
        
        if "salary" in question:
            # s = preprocessor.extract_salary(answer)
            # if s > 200000:
            #     print(f"{row.name=}")
            #     print(f'{row["Candidate Deidentified ID"]=}')
            #     print(f"{answer=}")
            #     raise ValueError("Salary is too high")
            return ("salary", preprocessor.extract_salary(answer))
        
        if "comfortable" in question:
            return ("stat_analysis", preprocessor.stat_analysis(answer))
        
        if "years of experience" in question:
            if "working with" in question:
                return ("skill_experience", preprocessor.skill_experience(answer))
            #else
            return ("stat_experience", preprocessor.stat_experience(answer))

        if "degree" in question:
            return ("degree_status", preprocessor.degree_status(answer))
        
        if "covid-19 vaccine" in question:
            return ("covid_vaccine", preprocessor.covid_vaccine(answer))
        
        if "level of expertise" in question:
            return ("extract_skills", preprocessor.extract_skills(answer))
        
        if "legal" in question:
            return ("legal_work", preprocessor.legal_work(answer))

        print(f"{row.name=}")
        print(f"{question=}")
        raise ValueError("Question not found")

    # for row in df, make a dict of candidates with the answers to the questions
    candidates = defaultdict(dict)
    for _, row in df.iterrows():
        out = answer_question(row)
        if out[0] == "covid_vaccine":
            continue #because its not consistent across all years
        if "Screening Form Total Score" not in candidates[row["Candidate Deidentified ID"]]:
            candidates[row["Candidate Deidentified ID"]]["Screening Form Total Score"] = row["Screening Form Total Score"]
        candidates[row["Candidate Deidentified ID"]][out[0]] = out[1]

    #lets do some sanity check
    #check if all candidates have all the answers
    # for candidate in candidates:
    #     #is assert fails, print candidate id
    #     assert len(candidates[candidate]) == 8, candidate
    return candidates, last_id1, last_id2
    # return candidates, last_id1, last_id2, last_id3, last_id4

def calculate_month_difference(start_month, start_year, end_month, end_year):
    # Convert inputs into datetime objects
    start_date = datetime(year=start_year, month=start_month, day=1)
    end_date = datetime(year=end_year, month=end_month, day=1)
    
    # Calculate the difference in months
    month_difference = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return month_difference

def vectorizer():
    last_id1, last_id2, last_id3, last_id4 = 0, 0, 0, 0
    #first run process
    # candidates, last_id1, last_id2, last_id3, last_id4 = process()
    candidates, last_id1, last_id2 = process()
    candidates = normalize_salary(candidates)
    candidates = normalize_screening_score(candidates)
    
    candidates = gather_education_details(candidates, last_id1, last_id2, last_id3, last_id4)
    candidates = gather_work_details(candidates, last_id1, last_id2, last_id3, last_id4)
    
    for candidate in list(candidates.keys()):
        if candidates[candidate]["legal_work"] == 0 or candidates[candidate]["degree_status"] == 0 or candidates[candidate]["stat_analysis"] == 0:
            del candidates[candidate]
    
    # round up years of experience
    for candidate in candidates:
        candidates[candidate]["yrs_of_experience"] = round(candidates[candidate]["yrs_of_experience"])
                
    print(f"{len(candidates)=}")
    # write dict to json
    with open(f"{DATA_DIR}candidates.json", "w") as f:
        json.dump(candidates, f, indent=4)
    
    # key_set = ["legal_work", "skill_experience", "stat_experience", "stat_analysis", "degree_status", "salary", "extract_skills", "Screening Form Total Score"]
    # key_set = ["skill_experience", "stat_experience", "salary", "extract_skills", "Screening Form Total Score"]
    key_set = ["skill_experience", "stat_experience", "salary", "extract_skills", "yrs_of_experience"]
    
    #now for each candidate, build a vector of answers
    vectors = {}
    for candidate in candidates:
        vector = []
        for key in key_set:
            vector.append(candidates[candidate][key])
        vectors[candidate] = np.array(vector)
    
    #write vectors to pickle
    with open(f"{DATA_DIR}vectors.pkl", "wb") as f:
        pickle.dump(vectors, f)

#open the json file, for all candidates, append the salary to a list, order the list, and print it
def normalize_salary(candidates):
    salaries = []
    for candidate in candidates:
        salaries.append(candidates[candidate]["salary"])
    
    #find mean and std of salaries
    mean = np.mean(salaries)
    std = np.std(salaries)
    
    #normalize salaries
    for candidate in candidates:
        candidates[candidate]["salary"] = (candidates[candidate]["salary"] - mean) / std
    
    return candidates


def normalize_screening_score(candidates):
    scores = []
    for candidate in candidates:
        scores.append(candidates[candidate]["Screening Form Total Score"])
    
    #find mean and std of scores
    mean = np.mean(scores)
    std = np.std(scores)
    
    #normalize scores
    for candidate in candidates:
        candidates[candidate]["Screening Form Total Score"] = (candidates[candidate]["Screening Form Total Score"] - mean) / std
    
    return candidates


def gather_education_details(candidates, last_id1 = 0, last_id2 = 0, last_id3 = 0, last_id4 = 0):
    #extract education details as a df from csv
    df1 = pd.read_csv(f"{DATA_DIR}education_details_1.csv")
    df2 = pd.read_csv(f"{DATA_DIR}education_details_2.csv")
    # df3 = pd.read_csv(f"{DATA_DIR}education_details_3.csv")
    # df4 = pd.read_csv(f"{DATA_DIR}education_details_4.csv")
    # df5 = pd.read_csv(f"{DATA_DIR}education_details_5.csv")
    
    #sort each df by Candidate Deidentified ID
    df1.sort_values("Candidate Deidentified ID", inplace=True)
    df2.sort_values("Candidate Deidentified ID", inplace=True)
    # df3.sort_values("Candidate Deidentified ID", inplace=True)
    # df4.sort_values("Candidate Deidentified ID", inplace=True)
    # df5.sort_values("Candidate Deidentified ID", inplace=True)
    
    #fix candidate deidentified id
    df2["Candidate Deidentified ID"] = df2["Candidate Deidentified ID"] + last_id1
    # df3["Candidate Deidentified ID"] = df3["Candidate Deidentified ID"] + last_id2
    # df4["Candidate Deidentified ID"] = df4["Candidate Deidentified ID"] + last_id3
    # df5["Candidate Deidentified ID"] = df5["Candidate Deidentified ID"] + last_id4
    
    #combine the dataframes
    # df = pd.concat([df1, df2, df3, df4, df5])
    df = pd.concat([df1, df2])
    df.drop("Unnamed: 0", axis=1, inplace=True)
    # print(df.tail(10))
    df.drop_duplicates(inplace=True)    
    
    #drop Education Start Date,Education End Date,Education Degree Type,Education Major
    df.drop(["Education Start Date", "Education End Date", "Education Degree Type", "Education Major"], axis=1, inplace=True)
    
    #if a row is nan, remove it
    df.dropna(inplace=True)
    
    #for candidate in df, add the education details to candidates dict. if educatiion details are not present, remove the candidate from candidates dict
    for _, row in df.iterrows():
        candidate = row["Candidate Deidentified ID"]
        if candidate in candidates:
            candidates[candidate]["education"] = f'{candidates[candidate].get("education", "")}Degree Name: {row["Education Degree Name"]}, College Number: {int(row["Education College Deidentified ID"])};\n'
        else:
            print(f"{candidate=}")
            print(f"{row=}")
            raise ValueError("Candidate not found")
    
    #remove candidates without education details
    for candidate in list(candidates.keys()):
        if "education" not in candidates[candidate]:
            del candidates[candidate]
    
    return candidates

def gather_work_details(candidates, last_id1 = 0, last_id2 = 0, last_id3 = 0, last_id4 = 0):
    #extract work details as a df from csv
    df1 = pd.read_csv(f"{DATA_DIR}work_details_1.csv")
    df2 = pd.read_csv(f"{DATA_DIR}work_details_2.csv")
    # df3 = pd.read_csv(f"{DATA_DIR}work_details_3.csv")
    # df4 = pd.read_csv(f"{DATA_DIR}work_details_4.csv")
    # df5 = pd.read_csv(f"{DATA_DIR}work_details_5.csv")
    
    #sort each df by Candidate Deidentified ID
    df1.sort_values("Candidate Deidentified ID", inplace=True)
    df2.sort_values("Candidate Deidentified ID", inplace=True)
    # df3.sort_values("Candidate Deidentified ID", inplace=True)
    # df4.sort_values("Candidate Deidentified ID", inplace=True)
    # df5.sort_values("Candidate Deidentified ID", inplace=True)
    
    #fix candidate deidentified id
    df2["Candidate Deidentified ID"] = df2["Candidate Deidentified ID"] + last_id1
    # df3["Candidate Deidentified ID"] = df3["Candidate Deidentified ID"] + last_id2
    # df4["Candidate Deidentified ID"] = df4["Candidate Deidentified ID"] + last_id3
    # df5["Candidate Deidentified ID"] = df5["Candidate Deidentified ID"] + last_id4
    
    #combine the two dataframes
    # df = pd.concat([df1, df2, df3, df4, df5])
    df = pd.concat([df1, df2])
    #drop the Unnamed: 0 column
    df.drop("Unnamed: 0", axis=1, inplace=True)
    df.drop_duplicates(inplace=True)
    
    df["Work History Title"].fillna("Did not declare", inplace=True)
    df["Work History End Year"].fillna(2024, inplace=True)
    df["Work History Start Month"].fillna(1, inplace=True)
    df["Work History End Month"].fillna(11, inplace=True)
    
    # nan_rows = df[df.isnull().any(axis=1)]
    # print(f"{nan_rows=}")
    #print candidate ids with nan values
    # print(f"{list(nan_rows['Candidate Deidentified ID'].unique())}")
    
    #if a row is nan, remove it
    df.dropna(inplace=True)
    
    # ,Candidate Deidentified ID,Work Company Name Deidentified ID,Work History Title,Work History Start Year,Work History End Year,Work History Start Month,Work History End Month
    for _, row in df.iterrows():
        candidate = row["Candidate Deidentified ID"]
        if candidate in candidates:
            candidates[candidate]["work_history"] = f'{candidates[candidate].get("work_history", "")}Company Number: {int(row["Work Company Name Deidentified ID"])}, Work Title: {row["Work History Title"]}, Start: {MONTHS[int(row["Work History Start Month"])]} {int(row["Work History Start Year"])}, End: {MONTHS[int(row["Work History End Month"])]} {int(row["Work History End Year"])};\n'
            candidates[candidate]["yrs_of_experience"] = candidates[candidate].get("yrs_of_experience", 0) + calculate_month_difference(int(row["Work History Start Month"]), int(row["Work History Start Year"]), int(row["Work History End Month"]), int(row["Work History End Year"])) / 12
    
    #remove candidates without education details
    for candidate in list(candidates.keys()):
        if "work_history" not in candidates[candidate]:
            del candidates[candidate]
    
    return candidates
    
if __name__ == "__main__":
    vectorizer()
    