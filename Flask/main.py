from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
import os
from uuid import uuid1
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "TommyShelby"

# ====================================== UPLOAD IMAGES DIRECTORY ===================================== #
UPLOAD_FOLDER = "static/files"
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_img(filename):
    control_point = str(filename.lower())
    if control_point[control_point.rfind(".") + 1:] in ALLOWED_EXTENSIONS:
        return True
    else:
        return False


# ====================================== PREPARE SQL DATABASE ===================================== #
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myList.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    img_name = db.Column(db.String, nullable=False)


class Lists(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String, nullable=False)
    list_type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Tasks(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String, nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"))


# ====================================== TRACK CURRENT USER ===================================== #
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).filter_by(id=user_id).first()


# ====================================== ROUTING PAGES SECTION ===================================== #
@app.route("/")
def index_page():
    return redirect(url_for("login_page"))


@app.route("/personal", methods=["GET", "POST"])
@login_required
def personal_page():
    if request.method == "POST":
        if "hidden_list" in request.form:
            check_list = db.session.query(Lists).filter(
                Lists.list_name == request.form.get("my_list"),
                Lists.user_id == current_user.id
            ).first()
            if check_list is not None:
                flash("List with that name already exists!")
                return redirect(url_for("personal_page"))
            else:
                new_list = Lists(
                    list_name=request.form.get("my_list"),
                    list_type="progress",
                    user_id=current_user.id
                )
                db.session.add(new_list)
                db.session.commit()
                return redirect(url_for("personal_page"))

        if "hidden_task" in request.form:
            active_list = db.session.query(Lists).filter_by(list_name=request.form.get("hidden_list_name")).first()
            check_task = db.session.query(Tasks).filter(
                Tasks.task_name == request.form.get("my_task"),
                Tasks.list_id == active_list.id
            ).first()
            if check_task is not None:
                flash("Task with that name already exists!")
                return redirect(url_for("personal_page"))
            else:
                new_task = Tasks(
                    task_name=request.form.get("my_task"),
                    list_id=active_list.id
                )
                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for("personal_page"))

    completed_lists = db.session.query(Lists).filter_by(list_type="completed").all()
    progress_lists = db.session.query(Lists).filter_by(list_type="progress").all()
    personal_tasks = db.session.query(Tasks).filter_by(list_id=request.args.get("personal_list_id")).all()
    chosen_list_name = request.args.get("chosen_list_name")
    return render_template(
        "personal.html",
        logged_in=current_user.is_authenticated,
        present_user=current_user,
        profile_image=f"files/{current_user.img_name}",
        completed_lists=completed_lists,
        progress_lists=progress_lists,
        personal_tasks=personal_tasks,
        chosen_list_name=chosen_list_name
    )


@app.route("/action", methods=["GET", "POST"])
@login_required
def action_page():
    if request.method == "POST":
        chosen_task = db.session.query(Tasks).filter_by(id=request.form.get("hidden_task_id")).first()
        chosen_task.task_name = request.form.get("task")
        db.session.commit()
        return redirect(url_for("personal_page"))

    task_id = request.args.get("task_id")
    chosen_task = db.session.query(Tasks).filter_by(id=task_id).first()
    return render_template(
        "action.html",
        logged_in=current_user.is_authenticated,
        present_user=current_user,
        chosen_task=chosen_task
    )


@app.route("/delete-task")
@login_required
def delete_task_page():
    task_id = request.args.get("task_id")
    chosen_task = db.session.query(Tasks).filter_by(id=task_id).first()
    db.session.delete(chosen_task)
    db.session.commit()
    return redirect(url_for("personal_page"))


@app.route("/delete-list")
@login_required
def delete_list_page():
    list_id = request.args.get("list_id")
    chosen_list = db.session.query(Lists).filter_by(id=list_id).first()
    db.session.delete(chosen_list)
    db.session.commit()
    return redirect(url_for("personal_page"))


@app.route("/complete-list")
@login_required
def complete_list_page():
    list_id = request.args.get("list_id")
    chosen_list = db.session.query(Lists).filter_by(id=list_id).first()
    chosen_list.list_type = "completed"
    db.session.commit()
    return redirect(url_for("personal_page"))


@app.route("/progress-list")
@login_required
def progress_list_page():
    list_id = request.args.get("list_id")
    chosen_list = db.session.query(Lists).filter_by(id=list_id).first()
    chosen_list.list_type = "progress"
    db.session.commit()
    return redirect(url_for("personal_page"))


# =========================== LOGIN - REGISTER - LOGOUT - SECTION ================================ #
@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        file = request.files["img"]
        if file.filename == "":
            flash("Upload Image - It's Necessary!")
            return redirect(url_for("register_page"))

        check_email = db.session.query(Users).filter_by(email=request.form.get("email")).first()
        if check_email is not None:
            flash("User with that Email - Already Exists!")
            return redirect(url_for("register_page"))
        else:
            if allowed_img(file.filename):
                img_file = secure_filename(file.filename)
                img_random_name = str(uuid1()) + "_" + img_file
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], img_random_name))
                new_user = Users(
                    first_name=request.form.get("first_name"),
                    last_name=request.form.get("last_name"),
                    email=request.form.get("email"),
                    password=generate_password_hash(
                        password=request.form.get("password"),
                        method="pbkdf2:sha256",
                        salt_length=8
                    ),
                    img_name=img_random_name
                )
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for("personal_page"))
            else:
                flash("Only Images are Allowed!")
                return redirect(url_for("register_page"))
    return render_template(
        "register.html",
        logged_in=current_user.is_authenticated
    )


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        check_user = db.session.query(Users).filter_by(email=request.form.get("email")).first()
        if check_user is None:
            flash("Wrong Email")
            return redirect(url_for("login_page"))
        else:
            if not check_password_hash(pwhash=check_user.password, password=request.form.get("password")):
                flash("Wrong Password")
                return redirect(url_for("login_page"))
            else:
                login_user(check_user)
                return redirect(url_for("personal_page"))
    return render_template(
        "login.html",
        logged_in=current_user.is_authenticated
    )


@app.route("/logout")
def logout_page():
    logout_user()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
