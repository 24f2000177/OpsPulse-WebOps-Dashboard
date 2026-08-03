from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="admin",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<User {self.username}>"


class ServerLog(db.Model):

    __tablename__ = "server_logs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    cpu = db.Column(
        db.Float,
        nullable=False
    )

    memory = db.Column(
        db.Float,
        nullable=False
    )

    disk = db.Column(
        db.Float,
        nullable=False
    )

    hostname = db.Column(
        db.String(100),
        nullable=False
    )

    os_name = db.Column(
        db.String(100),
        nullable=False
    )

    uptime = db.Column(
        db.String(100),
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "cpu": self.cpu,
            "memory": self.memory,
            "disk": self.disk,
            "hostname": self.hostname,
            "os_name": self.os_name,
            "uptime": self.uptime,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def __repr__(self):
        return f"<ServerLog {self.id}>"