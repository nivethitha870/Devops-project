Kimport os
import re
import glob
from collections import defaultdict
from langdetect import detect
from PyPDF2 import PdfReader
from docx import Document

class Graph:

    def __init__(self):
        self.graph={}

    def add_edge(self,u,v):

        if u not in self.graph:
            self.graph[u]=[]

        if v not in self.graph:
            self.graph[v]=[]

        self.graph[u].append(v)
        self.graph[v].append(u)


    def dfs(self,start):

        visited=set()
        result=[]

        def dfs_recursive(vertex):

            visited.add(vertex)
            result.append(vertex)

            for neighbor in self.graph.get(vertex,[]):

                if neighbor not in visited:
                    dfs_recursive(neighbor)

        if start:
            dfs_recursive(start)

        return result



class ResumeShortlister:

    def __init__(self):

        self.keyword_hash=defaultdict(int)

        self.skill_graph=Graph()

        self.candidates=[]

        self.resume_texts={}



    def read_text_from_file(self,filepath):

        ext=os.path.splitext(filepath)[1].lower()

        try:

            if ext==".txt":

                with open(filepath,"r",encoding='utf-8',errors="ignore") as f:
                    return f.read()


            elif ext==".pdf":

                reader=PdfReader(filepath)

                text=""

                for page in reader.pages:

                    if page.extract_text():
                        text+=page.extract_text()

                return text


            elif ext==".docx":

                doc=Document(filepath)

                return "\n".join(p.text for p in doc.paragraphs)


        except:
            return ""

        return ""



    def process_resume(self,text,required_skills):

        try:
            detect(text)
        except:
            pass


        keywords=re.findall(r'\b\w+\b',text.lower())


        for word in keywords:

            self.keyword_hash[word]+=1


        for skill in required_skills:

            for related in required_skills:

                if skill!=related:
                    self.skill_graph.add_edge(skill,related)



        matched=set(keywords) & set(required_skills)


        root=next(iter(matched),'') if matched else ''


        related_skills=self.skill_graph.dfs(root) if root else []


        related_score=sum(1 for s in related_skills if s in matched)


        score=len(matched)*2 + related_score


        return score



if __name__=="__main__":

    print("\n===== AI Resume Processing Started =====\n")


    folder="resumes"


    required_skills=[
        "python",
        "java",
        "sql",
        "machine",
        "learning",
        "data",
        "docker",
        "kubernetes"
    ]


    app=ResumeShortlister()


    files=glob.glob(os.path.join(folder,'*'))


    supported_exts=('.txt','.pdf','.docx')


    files=[f for f in files if f.lower().endswith(supported_exts)]


    if not files:

        print("No resumes found")

        exit()


    for file in files:

        text=app.read_text_from_file(file)

        score=app.process_resume(text,required_skills)

        name=os.path.basename(file)

        app.candidates.append((-score,name))

        print(f"{name} Score : {score}")



    sorted_cands=sorted(app.candidates)


    print("\n===== FINAL RANKING =====\n")


    rank=1

    for neg_score,name in sorted_cands:

        print(f"Rank {rank} : {name} Score : {-neg_score}")

        rank+=1


    print("\n===== TOP 3 CANDIDATES =====\n")


    for i,(neg_score,name) in enumerate(sorted_cands[:3],1):

        print(f"{i}. {name} Score : {-neg_score}")


    print("\n===== AI Resume Processing Completed =====\n")
