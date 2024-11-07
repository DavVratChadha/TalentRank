import pandas as pd
from collections import defaultdict
import json
import preprocessor
import pickle
import numpy as np

DATA_DIR = "data/"
MONTHS = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}


def process():
    # Read the CSV file, ignoring the first column
    df1 = pd.read_csv(f"{DATA_DIR}screening_questions_1.csv", index_col=0)

    #now we read the second file
    df2 = pd.read_csv(f"{DATA_DIR}screening_questions_2.csv", index_col=0)

    #need to fix candidate deidentified id
    #first find the id of last candidate in first file
    last_id = df1["Candidate Deidentified ID"].iloc[-1]
    #now add this id to the second file
    df2["Candidate Deidentified ID"] = df2["Candidate Deidentified ID"] + last_id

    #combine the two dataframes
    df = pd.concat([df1, df2])

    def answer_question(row):
        question = row["Screening Form Question"].lower()
        answer = row["Screening Form Answer"]
        # if answer is nan, print row number
        if pd.isna(answer):
            print(f"{row.name=}")
            raise ValueError("Answer is nan")
        
        if "salary" in question:
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
    return candidates, last_id

def vectorizer():
    #first run process
    candidates, last_id = process()
    candidates = normalize_salary(candidates)
    candidates = normalize_screening_score(candidates)
    
    candidates = gather_education_details(candidates, last_id)
    candidates = gather_work_details(candidates, last_id)
    
    print(f"{len(candidates)=}")
    # write dict to json
    with open(f"{DATA_DIR}candidates.json", "w") as f:
        json.dump(candidates, f, indent=4)
    
    # key_set = ["legal_work", "skill_experience", "stat_experience", "stat_analysis", "degree_status", "salary", "extract_skills", "Screening Form Total Score"]
    # key_set = ["skill_experience", "stat_experience", "salary", "extract_skills", "Screening Form Total Score"]
    key_set = ["skill_experience", "stat_experience", "salary", "extract_skills"]
    
    #now for each candidate, build a vector of answers
    vectors = {}
    for candidate in candidates:
        if candidates[candidate]["legal_work"] == 0 or candidates[candidate]["degree_status"] == 0 or candidates[candidate]["stat_analysis"] == 0:
            continue
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


def gather_education_details(candidates, last_id):
    #extract education details as a df from csv
    df1 = pd.read_csv(f"{DATA_DIR}education_details_1.csv")
    df2 = pd.read_csv(f"{DATA_DIR}education_details_2.csv")
    
    #fix candidate deidentified id
    df2["Candidate Deidentified ID"] = df2["Candidate Deidentified ID"] + last_id
    
    #combine the two dataframes
    df = pd.concat([df1, df2])
    
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

def gather_work_details(candidates, last_id):
    #extract work details as a df from csv
    df1 = pd.read_csv(f"{DATA_DIR}work_details_1.csv")
    df2 = pd.read_csv(f"{DATA_DIR}work_details_2.csv")
    
    #fix candidate deidentified id
    df2["Candidate Deidentified ID"] = df2["Candidate Deidentified ID"] + last_id
    
    #combine the two dataframes
    df = pd.concat([df1, df2])
    
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
    
    #remove candidates without education details
    for candidate in list(candidates.keys()):
        if "work_history" not in candidates[candidate]:
            del candidates[candidate]
    
    return candidates
    
if __name__ == "__main__":
    vectorizer()
    