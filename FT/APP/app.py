# app.py (Flask app with login and dashboard)

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from email_reader import fetch_emails
from summarizer import summarize_emails
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Dummy user credentials
dummy_users = {
    "user@example.com": "password123",
    "admin@example.com": "admin123",
    "admin@admin": "admin"
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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user = session['user']

    if 'email_account' not in session or not session['email_account']:
        flash('Please configure your email address first', 'warning')
        return redirect(url_for('settings'))

    emails = []
    unread_count = 0
    date_from = date_to = ""
    if request.method == 'POST':
        try:
            date_from = request.form.get('date_from')
            date_to = request.form.get('date_to')
            df = datetime.strptime(date_from, "%Y-%m-%d").strftime("%d-%b-%Y")
            dt = datetime.strptime(date_to, "%Y-%m-%d").strftime("%d-%b-%Y")
            emails = fetch_emails(df, dt)
            unread_count = len(emails)

            # Save emails to a temporary file
            os.makedirs("temp", exist_ok=True)
            temp_file_path = f"temp/{session['user']}_emails.json"
            with open(temp_file_path, "w", encoding="utf-8") as f:
                json.dump(emails, f, indent=2, ensure_ascii=False)

            # Store the file path in the session
            session['emails_file'] = temp_file_path
        except Exception as e:
            flash(f"Failed to fetch emails: {e}", "danger")

    theme = session.get('theme', 'light')
    return render_template('dashboard.html', user=user, unread_count=unread_count, emails=emails, theme=theme, date_from=date_from, date_to=date_to)

@app.route('/summarize')
def summarize():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'emails_file' not in session:
        flash("No emails found for summarization.", "warning")
        return redirect(url_for('dashboard'))

    # Load emails from the temporary file
    emails_file = session['emails_file']
    try:
        with open(emails_file, "r", encoding="utf-8") as f:
            emails = json.load(f)
    except Exception as e:
        flash(f"Failed to load emails: {e}", "danger")
        return redirect(url_for('dashboard'))

    prioritize = ["project", "client", "meeting", "security", "locklinked", "cvgen", "phoenix", "chimera", "alpha", "beta"]
    deprioritize = ["newsletter", "spam", "phishing", "recruitment", "job opportunities", "external news", "lottery", "seo"]

    # Call the summarizer function
    structured_summary = summarize_emails(
        emails,
        prioritize_keywords=prioritize,
        deprioritize_keywords=deprioritize
    )

    if not structured_summary:
        flash("Failed to generate summary.", "danger")
        return redirect(url_for('dashboard'))

    # Save the summary to a file
    os.makedirs("static/summaries", exist_ok=True)
    summary_path = f"static/summaries/{session['user']}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(structured_summary, f, indent=2, ensure_ascii=False)
    session['summary_path'] = summary_path

    # Pass the structured summary to the template
    return render_template('summaries.html', summaries=structured_summary)

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
            session['email_password'] = password
            session['language'] = language
            session['auto_summarize'] = auto_summarize
            flash('Email settings saved successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please enter both email address and password', 'danger')

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
    theme = request.args.get('theme', 'light')
    session['theme'] = theme
    return jsonify({"status": "success", "theme": theme})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
