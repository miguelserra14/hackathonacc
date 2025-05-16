# app.py (Flask app with login and dashboard)

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from email_reader import fetch_emails

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Dummy user credentials
dummy_users = {
    "user@example.com": "password123",
    "admin@example.com": "admin123",
    "admin@admin" : "admin"
}

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            if email in dummy_users and dummy_users[email] == password:
                session['user'] = email
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid email or password."
        else:
            error = "Please enter both email and password."
    theme = session.get('theme', 'light')
    return render_template('login.html', error=error, theme=theme)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = session['user']
    
    # Check if email account is configured
    if 'email_account' not in session or not session['email_account']:
        flash('Please configure your email address first', 'warning')
        return redirect(url_for('settings'))
    
    emails = fetch_emails("14-May-2025", "17-May-2025")
    unread_count = len(emails)
    session['emails_to_summarize'] = emails
    theme = session.get('theme', 'light')

    return render_template('dashboard.html', user=user, unread_count=unread_count, emails=emails, theme=theme)

@app.route('/summarize')
def summarize():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Check if email account is configured
    if 'email_account' not in session or not session['email_account']:
        flash('Please configure your email address first', 'warning')
        return redirect(url_for('settings'))
        
    # Here you would connect to Gmail/Outlook and run LLM summary on unread emails
    theme = session.get('theme', 'light')
    return render_template('summary.html', theme=theme)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        email = request.form.get('emailAccount')
        password = request.form.get('emailPassword')
        language = request.form.get('language')
        auto_summarize = request.form.get('autoSummarize') == 'on'
        
        if email and password:
            session['email_account'] = email
            session['email_password'] = password  # In production, store securely
            session['language'] = language
            session['auto_summarize'] = auto_summarize
            flash('Email settings saved successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter both email address and password', 'danger')
    
    # Get stored email account from session or use default
    email_account = session.get('email_account', '')
    language = session.get('language', 'English')
    auto_summarize = session.get('auto_summarize', False)
    theme = session.get('theme', 'light')
    
    return render_template('settings.html', 
                          email_account=email_account,
                          language=language,
                          auto_summarize=auto_summarize,
                          theme=theme)

@app.route('/set_theme')
def set_theme():
    """Endpoint to set theme preference in session"""
    theme = request.args.get('theme', 'light')
    session['theme'] = theme
    return jsonify({"status": "success", "theme": theme})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/summaries')
def summaries():
    if 'user' not in session:
        return redirect(url_for('login'))

    summaries = session.get('summaries', [])
    return render_template('summaries.html', summaries=summaries)

if __name__ == '__main__':
    app.run(debug=True)