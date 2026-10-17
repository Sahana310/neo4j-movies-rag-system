"""Password-free CineGraph: public sample graph with deterministic grounded answers."""
import json
import os
import re
from pathlib import Path
from flask import Flask, jsonify, render_template, request

BASE = Path(__file__).resolve().parent
app = Flask(__name__)
MOVIES = json.loads((BASE / 'data' / 'movies.json').read_text(encoding='utf-8'))
STOP = set('what which who when where tell about movie movies film films the was were did does with and for from directed acted starred actors actor director directors released year show list give me in is of a an to by on'.split())

def retrieve(question):
    terms = [w.lower() for w in re.findall(r"[\w']+", question) if len(w) > 2 and w.lower() not in STOP]
    if not terms:
        return []
    found = []
    for movie in MOVIES:
        title = movie['title'].lower()
        people = [p['name'].lower() for p in movie['people']]
        score = sum(8 * (t in title) + 5 * any(t in p for p in people) + 4 * (t == str(movie['released'])) + 2 * (t in movie.get('tagline','').lower()) for t in terms)
        if score:
            found.append(dict(movie, score=score))
    return sorted(found, key=lambda m: (-m['score'], m['title']))[:8]

def answer_question(question, movies):
    if not movies:
        return 'I could not find a matching movie or person in the bundled Neo4j Movies sample. Try The Matrix, Top Gun, Tom Hanks, or Keanu Reeves.', 'no_match'
    q = question.lower()
    # Questions about a particular film should not mix in less-relevant films.
    m = movies[0]
    cast = [p['name'] for p in m['people'] if p['role'] == 'ACTED_IN']
    directors = [p['name'] for p in m['people'] if p['role'] == 'DIRECTED']
    if any(s in q for s in ('directed', 'director')):
        answer = f"{m['title']} was directed by {', '.join(directors)}." if directors else f"The dataset does not list a director for {m['title']}."
    elif any(s in q for s in ('acted', 'actor', 'cast', 'starred', 'stars', 'played')):
        answer = f"The cast recorded for {m['title']} includes {', '.join(cast)}." if cast else f"The dataset does not list actors for {m['title']}."
    elif 'when' in q or 'year' in q or 'released' in q:
        answer = f"{m['title']} was released in {m['released']}."
    elif any(s in q for s in ('movies', 'films')) and not any(t in q for t in (m['title'].lower(),)):
        names = [f"{x['title']} ({x['released']})" for x in movies]
        answer = 'Matching movies in the sample: ' + ', '.join(names) + '.'
    else:
        answer = f"{m['title']} ({m['released']})."
        if directors:
            answer += ' Directed by ' + ', '.join(directors) + '.'
        if cast:
            answer += ' Cast includes ' + ', '.join(cast) + '.'
        if m.get('tagline'):
            answer += ' Tagline: ' + m['tagline'] + '.'
    key = os.getenv('OPENAI_API_KEY', '').strip()
    if key:
        try:
            from openai import OpenAI
            context = json.dumps(movies, ensure_ascii=False)
            response = OpenAI(api_key=key).chat.completions.create(model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'), temperature=0, messages=[{'role':'system','content':'Answer using ONLY the supplied movie records. If the answer is missing, say so. No invented facts.'},{'role':'user','content':f'Movie records: {context}\nQuestion: {question}'}])
            return response.choices[0].message.content or answer, 'llm'
        except Exception:
            pass  # The password-free mode always remains usable.
    return answer, 'grounded_template'

@app.get('/')
def index():
    return render_template('index.html')

@app.get('/api/health')
def health():
    return jsonify(status='connected', source='bundled public sample', movie_count=len(MOVIES), llm_configured=bool(os.getenv('OPENAI_API_KEY')))

@app.post('/api/ask')
def ask():
    question = str((request.get_json(silent=True) or {}).get('question', '')).strip()
    if not question or len(question) > 500:
        return jsonify(error='Enter a question between 1 and 500 characters.'), 400
    movies = retrieve(question)
    answer, mode = answer_question(question, movies)
    return jsonify(answer=answer, mode=mode, sources=movies)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
