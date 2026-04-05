from flask import Flask,render_template,request,send_file
import os
import subprocess

app=Flask(__name__)

UPLOAD_FOLDER="resumes"

@app.route('/')
def home():

    return render_template("index.html")


@app.route('/upload',methods=['POST'])

def upload():

    skills=request.form.get("skills","")

    files=request.files.getlist("resumes")

    names=[]

    for file in files:

        if file.filename!="":

            if file.filename.endswith(('.txt','.pdf','.docx')):

                filename=os.path.basename(file.filename)

                filepath=os.path.join(UPLOAD_FOLDER,filename)

                file.save(filepath)

                names.append(filename)

    result=subprocess.run(

    ["python3","ai_engine.py",skills],

    capture_output=True,

    text=True

    )

    output=result.stdout

    return render_template(

    "index.html",

    output=output,

    names=names

    )


@app.route('/download')

def download():

    return send_file("report.txt",as_attachment=True)


@app.route('/resume/<name>')

def resume(name):

    path=os.path.join("resumes",name)

    try:

        with open(path,'r',errors='ignore') as f:

            data=f.read()

    except:

        data="Cannot preview file"

    return data


if __name__=="__main__":

    app.run(host='0.0.0.0',port=5000)
