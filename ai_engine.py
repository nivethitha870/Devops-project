import os
import sys
import matplotlib.pyplot as plt

folder="resumes"

skills=[]

if len(sys.argv)>1:

    skills=sys.argv[1].lower().split(",")

valid_ext=('.txt','.pdf','.docx')

files=[f for f in os.listdir(folder) if f.lower().endswith(valid_ext)]

results=[]

total_skills=len(skills)

for file in files:

    path=os.path.join(folder,file)

    try:

        with open(path,'r',errors='ignore') as f:

            text=f.read().lower()

    except:

        text=""

    score=0

    for skill in skills:

        if skill.strip() in text:

            score+=1

    percent=(score/total_skills)*100 if total_skills>0 else 0

    results.append((file,score,int(percent)))

results.sort(key=lambda x:x[2],reverse=True)

# graph

names=[r[0] for r in results[:10]]

scores=[r[2] for r in results[:10]]

plt.figure()

plt.bar(names,scores)

plt.xticks(rotation=45)

plt.title("Top Resume Match %")

plt.savefig("static/graph.png")

# report

with open("report.txt","w") as f:

    for r in results:

        f.write(f"{r[0]} Score:{r[1]} Match:{r[2]}%\n")

print("TOP:"+results[0][0]+":"+str(results[0][2]))

for r in results:

    print(r[0]+","+str(r[1])+","+str(r[2]))

print("TOTAL:"+str(len(files)))
