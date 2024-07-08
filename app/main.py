from . import db
from .models import User
from .models import Workout
from .models import Target
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from datetime import datetime

current_date_str = datetime.now().strftime('%Y-%m-%d')
current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/home')
def home():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    targets = user.targets
    targets_to_delete = []
    
    for target in targets:
        if target.target.day < current_date.day:
            targets_to_delete.append(target)

    for target in targets_to_delete:
        db.session.delete(target)

    db.session.commit()

    return render_template('main.html')


@main.route('/stats')
@login_required
def stats():
    return render_template('stats.html', name=current_user.name)

@main.route('/api/workout/<workout_name>')
def get_workout_data(workout_name):
    workouts = Workout.query.filter_by(workout=workout_name).order_by(Workout.date_posted).all()
    workout_data = [
        {
            'date': workout.date_posted.strftime('%Y-%m-%d'),
            'count': workout.count
        } for workout in workouts
    ]
    print(workout_data)
    return jsonify(workout_data)

#all workouts
@main.route("/all")
@login_required
def user_workouts():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    workouts = user.workouts  # Workout.query.filter_by(author=user).order_by(Workout.date_posted.desc())
    current_date = datetime.now()
    return render_template('all_workouts.html', workouts=workouts, user=user,current_date=current_date)

#all target
@main.route("/alltargets")
@login_required
def user_targets():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    targets = user.targets 
    return render_template('all_targets.html', targets=targets, user=user)

#new target
@main.route("/newtarget", methods=['POST'])
@login_required
def new_target_post():
    workout=request.form.get('workout')
    count = request.form.get('count')
    date = request.form.get('date')
    target_date=datetime.strptime(date, '%Y-%m-%d').date()
    print(workout,count, date)
    workout = Target(workout=workout,count=count,target=target_date, author=current_user)
    db.session.add(workout)
    db.session.commit()
    flash('New goal has been added!')
    return redirect(url_for('main.user_targets'))

#new workout
@main.route("/new")
@login_required
def new_workout():
    return render_template('create_workout.html')

@main.route("/new", methods=['POST'])
@login_required
def new_workout_post():
    workout_name=request.form.get('workout')
    count = request.form.get('count')
    comment = request.form.get('comment')
    print(workout_name,count, comment)

    workout = Workout(workout=workout_name,count=count,comment=comment, author=current_user)
    db.session.add(workout)
    db.session.commit()

    flash('Your workout has been added!')

    goal = Target.query.filter_by(workout=workout_name).first()
    if goal and goal.target.day>current_date.day:
        if goal.count>int(count):
            goal.count-=int(count)
            goal.comment=f"You still have {goal.count} no. of {workout_name} to complete the goal."
        else:
            goal.count=0
            goal.comment="You completed the goal"
        
        db.session.commit()

    return redirect(url_for('main.user_workouts'))

#update workout
@main.route("/workout/<int:workout_id>/update", methods=['GET', 'POST'])
@login_required
def update_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    in_count=workout.count
    in_workout=workout.workout

    if request.method == "POST":
        workout_name=request.form['workout']
        count=request.form['count']
        workout.workout = workout_name
        workout.count = count
        workout.comment = request.form['comment']
        db.session.commit()
        flash('Your workout has been updated!')

        goal = Target.query.filter_by(workout=in_workout).first()
        if goal:
            goal.count+=int(in_count)
            goal.comment=f"You still have {goal.count} no. of {workout_name} to complete the goal."
            db.session.commit()

        goal = Target.query.filter_by(workout=workout_name).first()
        
        if goal and goal.target.day>current_date.day:
            if goal.count>int(count):
                goal.count-=int(count)
                goal.comment=f"You still have {goal.count} no. of {workout_name} to complete the goal."
            else:
                goal.count=0
                goal.comment="You completed the goal"
        
            db.session.commit()

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

    goal = Target.query.filter_by(workout=workout.workout).first()
    if goal:
        goal.count+=int(workout.count)
        goal.comment=f"You still have {goal.count} no. of {workout.workout} to complete the goal."
    
        db.session.commit()

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