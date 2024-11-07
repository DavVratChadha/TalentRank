import re


DATA_DIR = "data/"

#read job_details.txt
with open(DATA_DIR + "job_details.txt", "r") as f:
    job_details = f.read()
# print(job_details)


#extract Position Available:      Business Intelligence Analyst    
position = re.search(r"Position Available:\s+([A-Za-z\s]+)\n", job_details).group(1)
# print("Position Available: ", position)

# extract position summary
position_summary = re.search(r"Position Summary:\n([\s\S]+?)Responsibilities:", job_details).group(1)
# print("Position Summary: ", position_summary)

# extract responsibilities
responsibilities = re.search(r"Responsibilities:\n([\s\S]+?)Qualifications and Experience:", job_details).group(1)
# print("Responsibilities: ", responsibilities)

# extract qualifications and experience until an empty line or a line with just tabs or spaces
qualifications_and_experience = re.search(r"Qualifications and Experience:\n([\s\S]+?)(?:\n\s+|\n$)", job_details).group(1)
# print("Qualifications and Experience: ", qualifications_and_experience)

#restructre doc
restructed_job_details = f"Position:\n{position}\n\nPosition Summary:\n{position_summary}\nResponsibilities:\n{responsibilities}\nQualifications and Experience:\n{qualifications_and_experience}"
print(restructed_job_details)

#write restructured doc to a new file
with open(f"{DATA_DIR}restructured_job_details.txt", "w") as f:
    f.write(restructed_job_details)