from flask import render_template, redirect, url_for, request, flash
from werkzeug.utils import redirect
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from todo import db, app
from todo.models import Task, User
import json
import os

path_json = os.path.abspath(r"todo\state_sort.json")

@app.before_first_request
def create_tables():
    db.create_all()
    user = User(
        name='admin',
        password=generate_password_hash('123'))
    db.session.add(user)
    db.session.commit()
    print(user.password)


@app.route("/")
@app.route("/tasks/", methods=['GET', 'POST'])
def tasks():
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1

    dict_sort_data = {'username': Task.username, 'email': Task.email, 'status': Task.status}
    if request.method == "POST":
        sort_data = request.form.get('type_data')
        sort_order = request.form.get('type_order')

        with open(path_json) as f:
            data = json.load(f)
        data['sorting']['sort_data'] = sort_data
        data['sorting']['sort_order'] = sort_order
        with open(path_json, 'w') as f:
            f.write(json.dumps(data))

        if sort_order == 'increase':
            tasks = Task.query.order_by(dict_sort_data[sort_data])

        else:
            tasks = Task.query.order_by(dict_sort_data[sort_data].desc())


    else:
        with open(path_json) as f:
            data = json.load(f)

        if data['sorting']['sort_order'] == 'increase':
            tasks = Task.query.order_by(dict_sort_data[data['sorting']['sort_data']])

        else:
            tasks = Task.query.order_by(dict_sort_data[data['sorting']['sort_data']].desc())

    pages = tasks.paginate(page=page, per_page=3)

    return render_template('tasks.html', pages=pages)


@app.route("/add-todo", methods=["POST", "GET"])
def add_todo():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        text = request.form['text']
        status = 'Выполнено' if request.form.get('status') == 'on' else 'Не выполнено'

        task = Task(username=username, email=email, text=text, status=status)

        try:
            db.session.add(task)
            db.session.commit()
            return redirect('/tasks')
        except:
            return 'При добавлении задачи произошло ошибка'

    else:
        return render_template('add_task.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    name = request.form.get('name')
    password = request.form.get('password')
    if request.method == "POST":
        if name and password:
            user = User.query.filter_by(name=name).first()

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash('Неправильные реквизиты доступа')
        else:
            flash('Поля обязательны для заполнения или введенные данные не верные')

    return render_template('login.html')


@app.route('/tasks/<int:id>/edit/', methods=['POST', 'GET'])
@login_required
def edit_post(id):
    task = Task.query.get(id)
    if request.method == "POST":
        task.username = request.form['username']
        task.email = request.form['email']
        task.text = request.form['text']
        task.status = 'Выполнено' if request.form.get('status') == 'on' else 'Не выполнено'
        task.state_edit = 'отредактировано администратором'

        try:
            db.session.commit()
            return redirect('/tasks')
        except:
            return 'При редактировании задачи произошла ошибка'

    else:
        return render_template('edit_task.html', task=task)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response

