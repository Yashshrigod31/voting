# app.py

from flask import Flask, render_template, request, redirect, url_for

# Initialize the Flask application
app = Flask(_name_)

# A simple in-memory dictionary to store candidates and their vote counts.
# In a real application, you would use a database.
poll_data = {
    'candidates': {}
}

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Home page route.
    GET: Displays a form to enter candidate names.
    POST: Processes the submitted names and redirects to the voting page.
    """
    if request.method == 'POST':
        # Get candidate names from the form, split by comma, and strip whitespace
        candidates_str = request.form.get('candidates')
        if candidates_str:
            candidate_names = [name.strip() for name in candidates_str.split(',')]
            # Reset previous poll data and initialize new candidates with 0 votes
            poll_data['candidates'] = {name: 0 for name in candidate_names if name}
            return redirect(url_for('vote'))
    
    # On GET request, just render the home page
    return render_template('home.html')


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    """
    Voting page route.
    GET: Displays the list of candidates with radio buttons for voting.
    POST: Processes the vote and shows the results.
    """
    if request.method == 'POST':
        # Get the selected candidate from the form
        selected_candidate = request.form.get('candidate')
        if selected_candidate and selected_candidate in poll_data['candidates']:
            # Increment the vote count for the selected candidate
            poll_data['candidates'][selected_candidate] += 1
        
        # After voting, show the results
        return render_template('results.html', results=poll_data['candidates'])

    # On GET request, if candidates are set, show the voting page
    if not poll_data['candidates']:
        return redirect(url_for('home'))
        
    return render_template('vote.html', candidates=poll_data['candidates'])

if _name_ == '_main_':
    # The "debug=True" argument is convenient for development but should be
    # removed in a production environment.
    app.run(debug=True)