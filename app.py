from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

app = Flask(__name__)
import os
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///todos.db')
db = SQLAlchemy(app)

class Category(Enum):
    WORK = "Work"
    PERSONAL = "Personal"
    URGENT = "Urgent"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(20), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def index():
    # Get the filter parameters from the query string
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    completed = request.args.get('completed', '')

    # Build the query with conditions based on the filters
    query = Task.query
    if search:
        query = query.filter(Task.title.contains(search) | Task.description.contains(search))
    if category:
        query = query.filter(Task.category == category)
    if completed:
        query = query.filter(Task.completed == (completed == 'True'))
    
    tasks = query.all()
    
    return render_template('index.html', tasks=tasks, categories=[c.value for c in Category])

@app.route('/add_task', methods=['POST'])
def add_task_web():
    new_task = Task(
        title=request.form['title'],
        description=request.form['description'],
        category=request.form['category']
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_task/<int:task_id>', methods=['POST'])
def edit_task_web(task_id):
    task = Task.query.get_or_404(task_id)
    task.title = request.form['title']
    task.description = request.form['description']
    task.category = request.form['category']
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>')
def delete_task_web(task_id):
    db.session.delete(Task.query.get_or_404(task_id))
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete_task/<int:task_id>')
def complete_task_web(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run()


