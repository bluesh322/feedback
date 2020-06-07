from flask import Flask, request, render_template, redirect, flash, jsonify, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterUserForm, LoginUserForm, FeedbackForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'somemoregoodfun'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
sess = db.session
debug = DebugToolbarExtension(app)

"""
General Comments: Adding admin priveliges was the most interesting part of this, and I believe I'm going about it
in a way that is very naive. I also think the design of the app lends to that, and it would be nice to see
how other apps handle this type of thing, or if there is a template for it. 

The coolest part was when the workflow for adding a new feature became streamlined and I only needed to look up
one new thing to implement a feature. Had I developed tests early on, maybe the process for developing the app
could be even more so streamlined as the tests would have built up on another as the modules did.
"""

@app.route('/')
def index():
    return redirect('/register')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.route('/register', methods=["GET", "POST"])
def register_user_form():
    if 'user_username' in session:
        return redirect(f"/user/{session['user_username']}")
    form = RegisterUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        new_user.email = form.email.data
        new_user.first_name = form.first_name.data
        new_user.last_name = form.last_name.data
        sess.add(new_user)
        sess.commit()
        session['user_username'] = new_user.username
        flash('Successfully Registered')
        return redirect(f'/user/{new_user.username}')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user_form():
    if 'user_username' in session:
        return redirect(f"/user/{session['user_username']}")
    form = LoginUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            flash(f'Login successful for user: {user.username}!')
            session['user_username'] = user.username
            return redirect(f'/user/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def logout_user():
    session.pop('user_username')
    flash('Logged Out')
    return redirect('/')

@app.route('/user/<username>')
def show_secret(username):
    """I could optimize this for non-admins to have fewer queries"""
    if 'user_username' not in session:
        flash('Please login')
        return redirect('/login')
    user = User.query.get_or_404(username)
    all_feedback = Feedback.query.filter(Feedback.username == username)
    admin_feedback = Feedback.query.all()
    admin_users = User.query.filter(User.username != user.username)
    return render_template('secret.html',
                            user=user,
                            all_feedback=all_feedback,
                            admin_feedback=admin_feedback,
                            admin_users=admin_users)

@app.route('/user/<username>/delete', methods=["POST"])
def delete_user(username):
    if 'user_username' not in session:
        flash('Please login')
        return redirect('/login')
    sess_user = User.query.get_or_404(session['user_username'])
    user = User.query.get_or_404(username)
    if (sess_user.is_admin and user.is_admin) and (sess_user is not user):
        flash(f"Admin Delete other admin: {user.username}")
        sess.delete(user)
        sess.commit()
        return redirect('/')
    elif sess_user.is_admin and not user.is_admin:
        flash(f"Admin Deleted not admin: {user.username}")
        sess.delete(user)
        sess.commit()
        return redirect('/')
    elif sess_user is user:
        flash(f"User is deleting their account: {sess_user.username}")
        sess.delete(user)
        sess.commit()
        session.pop('user_username')
        return redirect('/')
    else:
        flash(f"You don't have permission to do that!")
        return redirect('/')

@app.route('/user/<username>/feedback/add', methods=['GET', 'POST'])
def show_add_feedback_form(username):
    if 'user_username' not in session:
        flash('Please login')
        return redirect('/login')
    form = FeedbackForm()
    user = User.query.get_or_404(username)
    if form.validate_on_submit() and user:
        new_feedback = Feedback(title=form.title.data, content=form.content.data, username=username)
        sess.add(new_feedback)
        sess.commit()
        return redirect(f'/user/{user.username}')
    else:
        return render_template('feedbackForm.html', form=form, user=user)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def show_update_feedback_form(feedback_id):
    if 'user_username' not in session:
        flash('Please login')
        return redirect('/login')
    
    print(f"USER: {request.args.get('username')}, feedback: {feedback_id}")
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(session['user_username'])
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        sess.commit()
        return redirect(f'/user/{user.username}')
    else:
        return render_template('updateFeedbackForm.html', form=form, feedback=feedback)

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    if 'user_username' not in session:
        flash('Please login')
        return redirect('/login')
    print(feedback_id)
    feedback = Feedback.query.get_or_404(feedback_id)
    user = User.query.get_or_404(session['user_username'])
    if feedback:
        sess.delete(feedback)
        sess.commit()
        return redirect(f'/user/{user.username}')
    else:
        flash("That feedback doesn't exist")
        return redirect(f'/user/{user.username}')
