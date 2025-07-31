from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here' # Required for flash messages

# Poll configuration
poll_data = {
    'question': 'Vote for your preferred candidate',
    'active': False # Poll starts inactive until candidates are added
}

CANDIDATES_FILE = 'candidates.json'
VOTES_FILE = 'votes.txt'

def load_candidates():
    """Load candidates from JSON file."""
    if os.path.exists(CANDIDATES_FILE):
        with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_candidates(candidates):
    """Save candidates to JSON file."""
    with open(CANDIDATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, indent=2)

def save_vote(candidate_id):
    """Save vote to file."""
    with open(VOTES_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{candidate_id}\n')

def tally_results():
    """Count votes for each candidate."""
    candidates = load_candidates()
    results = {c['id']: {'name': c['name'], 'votes': 0} for c in candidates}
    
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                candidate_id = line.strip()
                if candidate_id in results:
                    results[candidate_id]['votes'] += 1
    return results

@app.route('/')
def index():
    candidates = load_candidates()
    if not candidates:
        return redirect(url_for('manage_candidates'))
    
    # Inline HTML template for voting page
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>{{ data.question }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .candidate { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
            .candidate label { cursor: pointer; }
            .alert { background: #f2dede; padding: 10px; margin: 10px 0; border: 1px solid #ebccd1; }
        </style>
    </head>
    <body>
        <h1>{{ data.question }}</h1>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <form action="/vote" method="get">
            {% for candidate in candidates %}
                <div class="candidate">
                    <label>
                        <input type="radio" name="candidate" value="{{ candidate.id }}" required>
                        <strong>{{ candidate.name }}</strong>
                    </label>
                    {% if candidate.description %}
                        <p>{{ candidate.description }}</p>
                    {% endif %}
                </div>
            {% endfor %}
            
            <button type="submit">Submit Vote</button>
        </form>

        <p>
            <a href="/results">View Results</a> | 
            <a href="/manage">Manage Candidates</a>
        </p>
    </body>
    </html>
    '''
    
    return render_template_string(html, data=poll_data, candidates=candidates)

@app.route('/manage')
def manage_candidates():
    candidates = load_candidates()
    
    # Inline HTML template for candidate management
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>Manage Candidates</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .candidate { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
            .form-group { margin: 10px 0; }
            label { display: block; margin-bottom: 5px; }
            input, textarea { width: 300px; padding: 5px; }
            button { padding: 10px 15px; background: #007cba; color: white; border: none; cursor: pointer; }
            .success { background: #dff0d8; padding: 10px; margin: 10px 0; border: 1px solid #d6e9c6; }
        </style>
    </head>
    <body>
        <h1>Manage Candidates</h1>
        
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="success">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        <h2>Add New Candidate</h2>
        <form action="/add_candidate" method="post">
            <div class="form-group">
                <label for="name">Candidate Name:</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="description">Description/Bio:</label>
                <textarea id="description" name="description" rows="3" placeholder="Brief description of the candidate"></textarea>
            </div>
            
            <button type="submit">Add Candidate</button>
        </form>

        <h2>Current Candidates</h2>
        {% if candidates %}
            {% for candidate in candidates %}
                <div class="candidate">
                    <h3>{{ candidate.name }}</h3>
                    <p>{{ candidate.description or "No description provided" }}</p>
                    <small>ID: {{ candidate.id }}</small>
                </div>
            {% endfor %}
        {% else %}
            <p>No candidates added yet.</p>
        {% endif %}

        <p><a href="/">← Back to Voting</a></p>
    </body>
    </html>
    '''
    
    return render_template_string(html, candidates=candidates)

@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Candidate name is required!')
        return redirect(url_for('manage_candidates'))
    
    candidates = load_candidates()
    
    # Generate unique ID
    candidate_id = str(len(candidates) + 1)
    
    candidates.append({
        'id': candidate_id,
        'name': name,
        'description': description
    })
    
    save_candidates(candidates)
    flash(f'Candidate "{name}" added successfully!')
    return redirect(url_for('manage_candidates'))

@app.route('/vote')
def vote():
    candidate_id = request.args.get('candidate')
    candidates = load_candidates()
    
    # Verify candidate exists
    if candidate_id and any(c['id'] == candidate_id for c in candidates):
        save_vote(candidate_id)
        return redirect(url_for('thanks'))
    
    flash('Invalid candidate selection!')
    return redirect(url_for('index'))

@app.route('/thanks')
def thanks():
    html = '''
    <!doctype html>
    <html>
    <head><title>Thank you</title></head>
    <body style="font-family: Arial, sans-serif; margin: 20px;">
        <h2>Thanks for voting!</h2>
        <p><a href="/results">See results</a></p>
        <p><a href="/">Vote again</a></p>
    </body>
    </html>
    '''
    return render_template_string(html)

@app.route('/results')
def results():
    results_data = tally_results()
    
    html = '''
    <!doctype html>
    <html>
    <head>
        <title>Voting Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .result { padding: 10px; margin: 5px 0; background: #f5f5f5; }
        </style>
    </head>
    <body>
        <h1>Voting Results</h1>
        
        {% for candidate_id, result in results.items() %}
            <div class="result">
                <strong>{{ result.name }}</strong>: {{ result.votes }} vote(s)
            </div>
        {% endfor %}

        <p><a href="/">← Back to Voting</a></p>
    </body>
    </html>
    '''
    
    return render_template_string(html, results=results_data)

# Import render_template_string
from flask import render_template_string

if __name__ == '__main__':
    app.run(debug=True)
