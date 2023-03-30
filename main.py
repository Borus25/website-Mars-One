from flask import Flask, render_template, redirect, request, abort, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.jobs import Jobs
from forms.job import JobForm
from forms.user import RegisterForm, LoginForm
from data.users import User
from data import db_session

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/mars_explorer.db")
    app.run()


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.job = form.job_title.data
        job.team_leader = int(form.team_leader_id.data)
        job.work_size = int(form.work_size.data)
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished_job.data
        db_sess.add(job)
        db_sess.commit()
        return redirect('/')
    return render_template('add_job.html', title='Adding a Job', form=form)


@app.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id: int):
    form = JobForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id, (Jobs.user == current_user) | (Jobs.user == current_user == 1)).first()
        if job:
            form.job_title.data = job.job
            form.team_leader_id.data = job.team_leader
            form.work_size.data = job.work_size
            form.collaborators.data = job.collaborators
            form.is_finished_job.data = job.is_finished
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = db_sess.query(Jobs).filter(Jobs.id == id, (Jobs.team_leader == current_user) | (Jobs.team_leader == current_user == 1)).first()
        if job:
            job.job = form.job_title.data
            job.team_leader = int(form.team_leader_id.data)
            job.work_size = int(form.work_size.data)
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished_job.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html', title='Редактирование работы', form=form)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter((Jobs.is_finished == 0) | (Jobs.is_finished == 1))
    return render_template("index.html", jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User()
        user.email = form.email.data
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = int(form.age.data)
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            global USER_ID
            USER_ID = user.id
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


if __name__ == '__main__':
    main()
