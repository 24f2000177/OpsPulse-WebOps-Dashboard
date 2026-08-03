from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    flash
)

from config import Config
from model import db, User, ServerLog

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from functools import wraps

import psutil
import socket
import platform
import time

# Flask App

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

# Create Database

with app.app_context():

    db.create_all()

    # Create Default Admin User
    admin = User.query.filter_by(username="admin").first()

    if not admin:

        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()


# Boot Time

BOOT_TIME = psutil.boot_time()


# Login Required Decorator

def login_required(func):

    @wraps(func)

    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper

# Home
@app.route("/")
def home():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))

# Login

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            flash("Login Successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid Username or Password", "danger")

    return render_template("login.html")


# Logout

@app.route("/logout")
@login_required
def logout():

    session.clear()

    flash("Logged Out Successfully!", "success")

    return redirect(url_for("login"))


# Dashboard

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        username=session.get("username"),
        role=session.get("role")
    )


# Logs Page

@app.route("/logs")
@login_required
def logs():

    logs = (
        ServerLog.query
        .order_by(ServerLog.created_at.desc())
        .limit(100)
        .all()
    )

    return render_template(
        "logs.html",
        logs=logs
    )


# Profile


@app.route("/profile")
@login_required
def profile():

    user = User.query.get(session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )


# Change Password

@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():

    if request.method == "POST":

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")

        user = User.query.get(session["user_id"])

        if not check_password_hash(user.password, old_password):

            flash("Old password is incorrect.", "danger")
            return redirect(url_for("change_password"))

        user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password updated successfully.", "success")

        return redirect(url_for("dashboard"))

    return render_template("change_password.html")

# System Monitoring API


@app.route("/api/system")
@login_required
def api_system():

    cpu = round(psutil.cpu_percent(interval=1), 2)

    memory = round(psutil.virtual_memory().percent, 2)

    disk = round(psutil.disk_usage("/").percent, 2)

    hostname = socket.gethostname()

    os_name = platform.system() + " " + platform.release()

    uptime_seconds = int(time.time() - BOOT_TIME)

    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60

    uptime = f"{days}d {hours}h {minutes}m"

    if cpu >= 90 or memory >= 90 or disk >= 90:
        status = "Critical"

    elif cpu >= 70 or memory >= 70 or disk >= 70:
        status = "Warning"

    else:
        status = "Healthy"

    log = ServerLog(
        cpu=cpu,
        memory=memory,
        disk=disk,
        hostname=hostname,
        os_name=os_name,
        uptime=uptime,
        status=status
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({

        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "hostname": hostname,
        "os": os_name,
        "uptime": uptime,
        "status": status,
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")

    })


# Health Check API

@app.route("/health")
def health():

    return jsonify({

        "application": "OpsPulse",

        "status": "healthy",

        "version": "1.0.0"

    })


# Latest Log API


@app.route("/api/logs/latest")
@login_required
def latest_log():

    log = (
        ServerLog.query
        .order_by(ServerLog.created_at.desc())
        .first()
    )

    if log is None:

        return jsonify({
            "message": "No logs found"
        }), 404

    return jsonify({

        "cpu": log.cpu,

        "memory": log.memory,

        "disk": log.disk,

        "hostname": log.hostname,

        "os": log.os_name,

        "uptime": log.uptime,

        "status": log.status,

        "created_at": log.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    })


# Delete All Logs

@app.route("/logs/clear", methods=["POST"])
@login_required
def clear_logs():

    if session.get("role") != "admin":

        flash("Access Denied", "danger")

        return redirect(url_for("dashboard"))

    ServerLog.query.delete()

    db.session.commit()

    flash("All logs deleted successfully.", "success")

    return redirect(url_for("logs"))


# Error Handlers


@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html",
        title="404 - Page Not Found"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    db.session.rollback()

    return render_template(
        "500.html",
        title="500 - Internal Server Error"
    ), 500



# Before Request


@app.before_request
def before_request():

    # Skip static files
    if request.endpoint == "static":
        return

    # Future enhancement:
    # Add request logging or authentication checks here
    pass


# Context Processor

@app.context_processor
def inject_user():

    return {
        "username": session.get("username"),
        "role": session.get("role"),
        "app_name": "OpsPulse"
    }



# CLI Command

@app.cli.command("create-admin")
def create_admin():

    """
    Create default admin account
    """

    admin = User.query.filter_by(username="admin").first()

    if admin:

        print("Admin already exists.")
        return

    admin = User(
        username="admin",
        password=generate_password_hash("admin123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully.")



# Main


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )