# ToDoThat
### Video Demo:  https://www.youtube.com/watch?v=27C7HAiYygI

## The idea:
ToDoThat is a simple ToDo app. I sometimes have trouble with my productivity, so I decided to use some sort of a system that I could use to get that it check, but I didn't really like using any of them. Because of that, I figured that I might as well create something by myself so that i would be incentivized to use it, and I could expand it to my liking over time, while also learning in the process.

The app is quite simple. The users create an account, where they can add tasks. Those tasks can have deadlines, they can change the completion status of the task, edit or delete it.
All the information about the users and the tasks is stored in the todo.db database.

### Technologies used:
- Flask
- Flask-SQLAlchemy
- SQLite3
- Bootstrap

### Database:
The SQLite database is connected to the app using flask-sqlalchemy. I created two tables in the database: users and tasks.
The user table contains user id, username, password hash and an e-mail adress(which is not implemented yet)
The task table contains task id, the task itself, a boolean indicating whether the task was completed or not, user_id foreign key, deadline date and the date created.

### WebApp:
The webaspp itself is based on the flask framework. As for the frontend, Bootstrap frameowrk is utilised, so the the design of the page is largerly similiar to the one found in the finance problem set. The apology messege API (https://github.com/jacebrowning/memegen) is also inspired by the problem set. In order to use the app, users need to create an account by providing a username and password. The id of the user is stored in the session. Once logged in, you can add new tasks, with an optional deadline date. Those task can then be marked as completed, edited to changee the the text or the deadline, or deleted. All of the changes are commited to the database.

### Possible improvements:
If there where some additions to be made to the app, this would be some of the more interesting ones:
- Implementing an e-mail notification system. this is something I am really interested in. Using the already implemented deadline, the server would check once a day whether the users have some tasks that have a deadline the following day, and would send an email to each user that does.
- Implementaion of a subtask system. Some tasks, such as writing an essay may need to be split into smaller, more manegable tasks. A new table containing subtasks would be necessary.
- Sorting and multiple views. sometimes it may be beneficial to view only a part of your tasks.
I intend to implement at least some of those features in the future.