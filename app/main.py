from . import db
from .models import User
from .models import Workout
from .models import Target
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/home')
def home():
    return render_template('main.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

#all workouts
@main.route("/all")
@login_required
def user_workouts():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    workouts = user.workouts  # Workout.query.filter_by(author=user).order_by(Workout.date_posted.desc())
    return render_template('all_workouts.html', workouts=workouts, user=user)

#all target
@main.route("/alltargets")
@login_required
def user_targets():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    targets = user.targets 
    return render_template('all_targets.html', targets=targets, user=user)

#new target
@main.route("/newtarget")
@login_required
def new_target():
    return render_template('target.html')

@main.route("/newtarget", methods=['POST'])
@login_required
def new_target_post():
    workout=request.form.get('workout')
    count = request.form.get('count')
    date = request.form.get('date')
    print(workout,count, date)
    workout = Target(workout=workout,count=count,target=date, author=current_user)
    db.session.add(workout)
    db.session.commit()
    flash('Your workout has been added!')
    return redirect(url_for('main.home'))

#new workout
@main.route("/new")
@login_required
def new_workout():
    return render_template('create_workout.html')

@main.route("/new", methods=['POST'])
@login_required
def new_workout_post():
    workout=request.form.get('workout')
    count = request.form.get('count')
    comment = request.form.get('comment')
    print(workout,count, comment)
    workout = Workout(workout=workout,count=count,comment=comment, author=current_user)
    db.session.add(workout)
    db.session.commit()
    flash('Your workout has been added!')
    return redirect(url_for('main.home'))

#update workout
@main.route("/workout/<int:workout_id>/update", methods=['GET', 'POST'])
@login_required
def update_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if request.method == "POST":
        workout.workout = request.form['workout']
        workout.count = request.form['count']
        workout.comment = request.form['comment']
        db.session.commit()
        flash('Your workout has been updated!')
        return redirect(url_for('main.user_workouts'))

    return render_template('update_workout.html', workout=workout)

#delete workout
@main.route("/workout/<int:workout_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    flash('Your workout has been deleted!')
    return redirect(url_for('main.user_workouts'))

#delete target
@main.route("/target/<int:target_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_target(target_id):
    target = Target.query.get_or_404(target_id)
    db.session.delete(target)
    db.session.commit()
    flash('Your target has been deleted!')
    return redirect(url_for('main.user_workouts'))