from flask import Flask, render_template, session, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from datetime import datetime
from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
db = SQLAlchemy(app)


class Users(db.Model):
    __tablename__ = 'Users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    hash = db.Column(db.String,  nullable=False)
    email = db.Column(db.String, default=None)
    tasks = db.relationship("Tasks", backref="creator", lazy=True)

    def __repr__(self):
        return '<User %r>' % self.user_id

class Tasks(db.Model):
    __tablename__ = 'Tasks'
    task_id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))
    deadline = db.Column(db.Date)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.task_id


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
@login_required
def index():
    """"The main page of the app. You can view and modify your tasks from here"""

    # Get the user's tasks
    tasks = Tasks.query.filter_by(user_id = session["user_id"]).all()

    return render_template('index.html', tasks = tasks)

@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():

    """Lets you add a new task"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure task was not empty
        task = request.form.get("add_task")
        if not task:
            return apology("task must not be empty", 403)

        # Check if the user wants to set a deadline
        deadline = request.form.get("deadline")

        if deadline:

            # Get the deadline date and turn it into a datetime data type
            date_string = request.form.get("date")
            try:
                date = datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return apology("you have to select a date if you want a deadline", 403)
            date = date.date()

            # Ensure that the deadline is in the future
            current_date = datetime.today().date()

            if current_date > date:
                return apology("the deadline date must not be in the past", 403)

            # Insert the new task into the database with the deadline
            task = Tasks(
                deadline = date,
                task = task,
                user_id = session["user_id"],
            )

        else:
            # Insert the new task into the database without the deadline
            task = Tasks(
                task = task,
                user_id = session["user_id"],
            )

        db.session.add(task)
        db.session.commit()

        # Redirect user to the main page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add_task.html")


@app.route("/delete_task", methods=["POST"])
@login_required
def delete_task():

    """Lets you delete a task"""
    # Get the id of the task we wish to delete
    task_id = request.form.get("task_id")

    # Get the desired task from the database
    task_to_delete = Tasks.query.get_or_404(task_id)

    # Delete the task
    db.session.delete(task_to_delete)
    db.session.commit()

    # Redirect user to the main page
    return redirect("/")


@app.route("/task_completion", methods=["POST"])
@login_required
def task_completion():

    """Lets you change whether the task was completed or not"""
    # Get the id of the task
    task_id = request.form.get("task_id")

    # Get the desired task from the database
    task = Tasks.query.get_or_404(task_id)

    # Flip the status of the task
    if task.completed == False:
        status = True
    else:
        status = False
    task.completed = status
    db.session.commit()

    # Redirect user to the main page
    return redirect("/")

@app.route("/edit_task", methods=["POST"])
@login_required
def edit_task():

    """Lets you edit a task"""
    # Get the info about the task we wish to edit
    task_id = request.form.get("task_id")
    task = request.form.get("task")
    deadline = request.form.get("deadline")

    # Pass the information onto the page
    return render_template("edit_task.html", task_id = task_id, task = task, deadline = deadline)


@app.route("/update_task", methods=["POST"])
@login_required
def update_task():

    """Update the edited task"""
    # Get the id of the task we wish to delete
    task_id = request.form.get("task_id")
    print(task_id)

    # Get the edited task
    task = request.form.get("update_task")
    # Ensure task was not empty
    if not task:
        return apology("task must not be empty", 403)

    # Check if the user wants to set a deadline
    deadline = request.form.get("deadline")

    if deadline:

        # Get the deadline date and turn it into a datetime data type
        date_string = request.form.get("date")
        try:
            date = datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            return apology("you have to select a date if you want a deadline", 403)
        date = date.date()

        # Ensure that the deadline is in the future
        current_date = datetime.today().date()
        if current_date > date:
            return apology("the deadline date must not be in the past", 403)

        # Update the task with the deadline
        updated_task = Tasks.query.get_or_404(task_id)
        updated_task.task = task
        updated_task.deadline = date
        db.session.commit()

    else:
        # Update the task without the deadline
        updated_task = Tasks.query.get_or_404(task_id)
        updated_task.task = task
        updated_task.deadline = None
        db.session.commit()

    # Redirect user to the main page
    return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Get information from user
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Query database for username
        user = Users.query.filter_by(username=username).scalar()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.user_id

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get information from user
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Query database for username
        user = Users.query.filter_by(username=username).scalar()

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Check if the username is not taken
        elif user:
            return apology("username is alreaaady taken", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure that confirmation was submitted
        elif not confirmation:
            return apology("must provide confirmation", 400)

        # Ensure password is the same as in confirmation
        elif password != confirmation:
            return apology("passwords don't match", 400)

        # Hash the user's password
        password_hash = generate_password_hash(password)

        # Insert new user into the database
        user = Users(
            username = username,
            hash = password_hash,
        )
        db.session.add(user)
        db.session.commit()

        # Query database for user id
        user = Users.query.filter_by(username=username).scalar()
        print(user.user_id)

        # Remember which user has logged in
        session["user_id"] = user.user_id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
