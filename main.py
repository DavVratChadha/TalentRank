import warnings
import logging

#suppressing warnings because we know what we are doing
from transformers import logging as transformers_logging
warnings.filterwarnings("ignore")
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
transformers_logging.set_verbosity_error()

import os
import abc
import numpy as np
import chromadb
import json
from sentence_transformers import SentenceTransformer
from collections import defaultdict
import pickle
import similarity.similarity_functions as sim
import data_processor.job_details_processor as jdp
import data_processor.processor as processor
import util.data_cleaner as dc
import click
import re

#fixing seeds to 42
np.random.seed(42)


class IRSystem(metaclass=abc.ABCMeta):
    """
    IRSystem class to be use for TalentRank
    """

    def __init__(self, data_dir, edu_file, work_file, screening_ques, rank_type):
        self.data_dir = data_dir
        dc.format_it_correctly_because_stakeholders_are_watching(edu_file, work_file, screening_ques, self.data_dir)
        processor.vectorizer(self.data_dir)
        self.candidates = json.load(open(os.path.join(self.data_dir, "candidates.json"), "r"))
        self.n = len(self.candidates)
        if rank_type != "r3":
            self.model_id = "jjzha/jobbert_skill_extraction"
            self.model = SentenceTransformer(self.model_id)
            self.create_index()
            self.create_parser_searcher()

    def create_index(self):
        """
        INPUT:
            None
        OUTPUT:
            None
        """
        chroma_client = chromadb.Client()

        name = 'talentrank'

        if name in [collection.name for collection in chroma_client.list_collections()]:
            chroma_client.delete_collection(name)

        self.index_sys = chroma_client.create_collection(name=name, metadata={"hnsw:space": "ip", "hnsw:M": 400, "hnsw:construction_ef": 400, "hnsw:search_ef": 200}) #HNSW parameters explained better https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md and https://www.pinecone.io/learn/series/faiss/hnsw/

    def add_files(self):
        """
        INPUT:
            None
        OUTPUT:
            None
        """
        for candidate in self.candidates:
            self.index_sys.add(ids = candidate,
                                embeddings = (3*self.model.encode(self.candidates[candidate]["education"]) + 5*self.model.encode(self.candidates[candidate]["work_history"]) - 2*self.model.encode(f'Years of Experience = {self.candidates[candidate]["yrs_of_experience"]}')).tolist())
            if int(candidate) % 100 == 0:
                print(f"Already indexed: {candidate} candidates")
        print("Done indexing.")

    def create_parser_searcher(self):
        """
        INPUT:
            None
        OUTPUT:
            None
        """
        self.query_parser = self.model
        self.searcher = self.index_sys

    def perform_search(self, job_details=None):
        """
        INPUT:
            job_details: string
        OUTPUT:
            topicResults: dict

        Utilize self.query_parser and self.searcher to calculate the result for job_details
        """
        if job_details is not None:
            query_embeddings = self.query_parser.encode(job_details).tolist()
        else:
            path = os.path.join(self.data_dir, "business_analyst_target_vector.pkl")
            with open(path, "rb") as f:
                mean_vecs = pickle.load(f)
                query_embeddings = np.array(mean_vecs["r2"])
        topicResults = self.searcher.query(query_embeddings=query_embeddings, n_results=self.n)
        return topicResults["ids"][0]

    def r3_ranking(self):
        path = os.path.join(self.data_dir, "vectors.pkl")
        with open(path, "rb") as f:
            vectors = pickle.load(f)

        path = os.path.join(self.data_dir, "business_analyst_target_vector.pkl")
        with open(path, "rb") as f:
            mean_vecs = pickle.load(f)

        mean = np.array(mean_vecs["r3"])

        similarity = []
        for candidate in vectors:
            vector = vectors[candidate]
            similarity.append((candidate, sim.cosine_similarity(mean, vector)))

        ranks = sorted(similarity, key=lambda x: x[1], reverse=True)
        r3_ranking_list = [str(r[0]) for r in ranks]
        return r3_ranking_list

    def create_candidate_embeddings(self):
        path = os.path.join(self.data_dir, "candidates.json")
        with open(path, "r") as f:
            candidates = json.load(f)

        #encode the education and work history of each candidate
        candidate_embeddings = defaultdict(dict)
        for candidate_id in candidates:
            candidate = candidates[candidate_id]
            candidate_embeddings[candidate_id]["embedding"] = (3*self.model.encode(candidate["education"]) + 5*self.model.encode(candidate["work_history"]) - 2*self.model.encode(f'Years of Experience = {candidate["yrs_of_experience"]}')).tolist()

        #write to a new json
        path = os.path.join(self.data_dir, "candidate_embeddings.json")
        with open(path, "w") as f:
            json.dump(candidate_embeddings, f)
        return candidate_embeddings

    def get_consolidated_scoring(self,r1_ranking_list, r2_ranking_list, r3_ranking_list):
        def fill_missing_ranks(consolidated_scoring, lenght):
            for candidate in consolidated_scoring:
                for _ in  range(lenght - len(consolidated_scoring[candidate])):
                    consolidated_scoring[candidate].append(1e-10)
            return consolidated_scoring

        consolidated_scoring = {}

        for i, r in enumerate(r1_ranking_list):
            consolidated_scoring[int(r)] = [1/(i + 1)]

        for i, r in enumerate(r2_ranking_list):
            if int(r) in consolidated_scoring:
                consolidated_scoring[int(r)].append(1/(i + 1))
            else:
                consolidated_scoring[int(r)] = [1e-10, 1/(i + 1)]

        consolidated_scoring = fill_missing_ranks(consolidated_scoring, 2)

        for i, r in enumerate(r3_ranking_list):
            if int(r) in consolidated_scoring:
                consolidated_scoring[int(r)].append(1/(i + 1))
            else:
                consolidated_scoring[int(r)] = [1e-10, 1e-10, 1/(i + 1)]

        consolidated_scoring = fill_missing_ranks(consolidated_scoring, 3)
        return consolidated_scoring

    def final_rank(self, r1_ranking_list, r2_ranking_list, r3_ranking_list):
        consolidated_scoring = self.get_consolidated_scoring(r1_ranking_list, r2_ranking_list, r3_ranking_list)

        a, b, c = 2.2, 0.2, 1.2
        final_score = {}
        for candidate in consolidated_scoring:
            final_score[candidate] = a*consolidated_scoring[candidate][0] + b*consolidated_scoring[candidate][1] + c*consolidated_scoring[candidate][2]
        ranks = sorted(final_score.items(), key=lambda x: x[1], reverse=True)
        r4_ranking_list = [str(r[0]) for r in ranks]
        return r4_ranking_list

    def reranking(self, ranked_list):
        path = os.path.join(self.data_dir, "blacklist.json")
        with open(path, "r") as f:
            blacklist = json.load(f)
        #if blacklist is empty, return the ranked_list
        if blacklist == {"educational_institution": [], "work_company": []}:
            return ranked_list
        
        new_ranked_list = []
        for candidate in ranked_list:
            remove = False
            #use regex to find pattern College Name: <some text>; and extract <some text>
            pattern = re.compile(r"College Name: (.*?);")
            # find all matches
            matches = pattern.findall(self.candidates[candidate]["education"])
            for match in matches:
                if match.lower() in blacklist["educational_institution"]:
                    ranked_list.remove(candidate)
                    remove = True
                    break
            if remove:
                continue
            #also do it for work_history
            pattern = re.compile(r"Company Name: (.*?),")
            matches = pattern.findall(self.candidates[candidate]["work_history"])
            for match in matches:
                if match.lower() in blacklist["work_company"]:
                    ranked_list.remove(candidate)
                    remove = True
                    break
            
            if not remove:
                new_ranked_list.append(candidate)
        return new_ranked_list


def rank_candidates(rank_type="merged", k=200, data_dir="data/", edu_file = "education_details.xlsx", work_file = "work_details.xlsx", screening_ques = "screening_questions.xlsx", job_details_file = "job_details.txt"):
    talentrank = IRSystem(data_dir, edu_file, work_file, screening_ques, rank_type)

    if rank_type == "merged":
        job_details = jdp.process_job_deats(job_details_file)
        talentrank.add_files()
        r1_ranking_list = talentrank.perform_search(job_details=job_details)
        r2_ranking_list = talentrank.perform_search()
        r3_ranking_list = talentrank.r3_ranking()
        final_ranking = talentrank.final_rank(r1_ranking_list, r2_ranking_list, r3_ranking_list)
    elif rank_type == "r1":
        job_details = jdp.process_job_deats(job_details_file)
        talentrank.add_files()
        final_ranking = talentrank.perform_search(job_details=job_details)
    
    elif rank_type == "r2":
        talentrank.add_files()
        final_ranking = talentrank.perform_search()
    
    elif rank_type == "r3":
        final_ranking = talentrank.r3_ranking()
    
    #rerank the final ranking
    final_ranking = talentrank.reranking(final_ranking)
    
    return final_ranking[:k]


#using click to make the script more user friendly
@click.command()
@click.option("--rank_type", default="merged", help="Type of ranking to perform. Options: merged, r1")
@click.option("--k", default=200, help="Number of candidates to rank")
@click.option("--data_dir", default="data/", help="Directory where the data is/will be stored")
@click.option("--education_file", default="education_details.xlsx", help="Name of the education details file")
@click.option("--work_file", default="work_details.xlsx", help="Name of the work details file")
@click.option("--screening_questions_file", default="screening_questions.xlsx", help="Name of the screening questions file")
@click.option("--job_details_file", default="job_details.txt", help="Name of the job details file")
def main(rank_type, k, data_dir, education_file, work_file, screening_questions_file, job_details_file):
    top_k = rank_candidates(rank_type=rank_type, k=k, data_dir=data_dir, edu_file=education_file, work_file=work_file, screening_ques=screening_questions_file, job_details_file=job_details_file)
    
    #write to a file
    with open("top_candidates.txt", "w") as f:
        f.write("\n".join(top_k))
    
    print(f"Found {len(top_k)} good candidates.")
    print("Top candidates written to top_candidates.txt")


if __name__ == "__main__":
    main()