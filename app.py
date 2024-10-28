from flask import Flask, request, render_template
import PyPDF2
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import os

app = Flask(__name__)

def read_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text.replace("\n", " ")
    except Exception as e:
        print(f"Error reading the resume: {e}")
        return text

def ats_compatibility_score(resume_text, job_description_text):
    try:
        documents = [resume_text, job_description_text]
        vectorizer = CountVectorizer().fit_transform(documents)
        vectors = vectorizer.toarray()
        cosine_similarity = np.dot(vectors[0], vectors[1]) / (np.linalg.norm(vectors[0]) * np.linalg.norm(vectors[1]))
        percentage_score = round(cosine_similarity * 100, 2)
        return percentage_score
    except Exception as e:
        print(f"Unable to calculate ATS Score at the moment: {e}")
        return 0.0

@app.route('/', methods=['GET', 'POST'])
def index():
    score = None
    apply = None
    if request.method == 'POST':
        job_description = request.form['job_description']
        resume_file = request.files['resume']

        if resume_file and resume_file.filename.endswith('.pdf'):
            resume_path = os.path.join('uploads', resume_file.filename)
            resume_file.save(resume_path)
            resume_text = read_pdf(resume_path)

            if resume_text and job_description:
                score = ats_compatibility_score(resume_text, job_description)
                apply = score >= 70
            
            # Clean up the saved file
            os.remove(resume_path)

    return render_template('index.html', score=score, apply=apply)

if __name__ == "__main__":
    app.run(debug=True)
