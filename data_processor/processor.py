import pandas as pd
from collections import defaultdict
import json
import preprocessor
import pickle
import numpy as np

DATA_DIR = "data/"

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
        candidates[row["Candidate Deidentified ID"]][out[0]] = out[1]
        
    # write dict to json
    with open(f"{DATA_DIR}candidates.json", "w") as f:
        json.dump(candidates, f, indent=4)

    #lets do some sanity check
    #check if all candidates have all the answers
    for candidate in candidates:
        #is assert fails, print candidate id
        assert len(candidates[candidate]) == 7, candidate
    return candidates

def vectorizer():
    #first run process
    candidates = process()
    key_set = ["legal_work", "skill_experience", "stat_experience", "stat_analysis", "degree_status", "salary", "extract_skills"]
    
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
def salary():
    with open(f"{DATA_DIR}candidates.json", "r") as f:
        candidates = json.load(f)
    
    salaries = []
    for candidate in candidates:
        salaries.append((candidate, candidates[candidate]["salary"]))
    
    salaries.sort(key=lambda x: x[1])
    print(salaries)

if __name__ == "__main__":
    vectorizer()
    # salary()