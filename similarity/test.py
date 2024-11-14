import json
import matplotlib.pyplot as plt

# open json file, for all candidates, append the salary to a list, order the list, and plot it as a histogram
def plot_salary(candidates):
    salaries = []
    for candidate in candidates:
        salaries.append(candidates[candidate]["salary"])
    
    #plot the salaries on a log scale
    plt.hist(salaries, bins=20, color='orange')
    plt.yscale("log")
    # plt.xlabel("Salary [Normalized]")
    plt.xlabel("Salary")
    plt.ylabel("Frequency [log]")
    plt.title("Salary Distribution")
    
    plt.show()
    
    
    
if __name__ == "__main__":
    DATA_DIR = "data/"
    
    #open the json file
    with open(f"{DATA_DIR}candidates.json", "r") as f:
        candidates = json.load(f)
    
    plot_salary(candidates)