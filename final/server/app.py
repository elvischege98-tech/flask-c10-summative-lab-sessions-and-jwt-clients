from flask import Flask, request
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from models import db, User, Note


app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT configuration
app.config["JWT_SECRET_KEY"] = "super-secret-key-change-this-later"

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# ---------------------------------------------------
# HOME
# ---------------------------------------------------

@app.route("/")
def index():
    return {"message": "Productivity API is running"}


# ---------------------------------------------------
# SIGNUP
# ---------------------------------------------------

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    username = data.get("username")
    password = data.get("password")
    password_confirmation = data.get("password_confirmation")

    if not username or not password or not password_confirmation:
        return {
            "error": "Username, password and password confirmation are required"
        }, 400

    if password != password_confirmation:
        return {"error": "Passwords do not match"}, 400

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return {"error": "Username already exists"}, 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        username=username,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }, 201


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "error": "Username and password are required"
        }, 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return {"error": "Invalid username or password"}, 401

    if not bcrypt.check_password_hash(user.password, password):
        return {"error": "Invalid username or password"}, 401

    token = create_access_token(identity=str(user.id))

    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username
        }
    }, 200


# ---------------------------------------------------
# CURRENT USER
# ---------------------------------------------------

@app.route("/me", methods=["GET"])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()

    user = db.session.get(User, int(current_user_id))

    if not user:
        return {"error": "User not found"}, 404

    return {
        "id": user.id,
        "username": user.username
    }, 200


# ---------------------------------------------------
# GET ALL NOTES - PAGINATED
# ---------------------------------------------------

@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    current_user_id = int(get_jwt_identity())

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 10

    pagination = (
        Note.query
        .filter_by(user_id=current_user_id)
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    notes = []

    for note in pagination.items:
        notes.append({
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id
        })

    return {
        "notes": notes,
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages
        }
    }, 200


# ---------------------------------------------------
# GET ONE NOTE
# ---------------------------------------------------

@app.route("/notes/<int:note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id):
    current_user_id = int(get_jwt_identity())

    note = Note.query.filter_by(
        id=note_id,
        user_id=current_user_id
    ).first()

    if not note:
        return {"error": "Note not found"}, 404

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "user_id": note.user_id
    }, 200


# ---------------------------------------------------
# CREATE NOTE
# ---------------------------------------------------

@app.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    current_user_id = int(get_jwt_identity())

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return {
            "error": "Title and content are required"
        }, 400

    note = Note(
        title=title,
        content=content,
        user_id=current_user_id
    )

    db.session.add(note)
    db.session.commit()

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "user_id": note.user_id
    }, 201


# ---------------------------------------------------
# UPDATE NOTE
# ---------------------------------------------------

@app.route("/notes/<int:note_id>", methods=["PATCH"])
@jwt_required()
def update_note(note_id):
    current_user_id = int(get_jwt_identity())

    note = Note.query.filter_by(
        id=note_id,
        user_id=current_user_id
    ).first()

    if not note:
        return {"error": "Note not found"}, 404

    data = request.get_json()

    if not data:
        return {"error": "Request body is required"}, 400

    if "title" in data:
        note.title = data["title"]

    if "content" in data:
        note.content = data["content"]

    db.session.commit()

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "user_id": note.user_id
    }, 200


# ---------------------------------------------------
# DELETE NOTE
# ---------------------------------------------------

@app.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    current_user_id = int(get_jwt_identity())

    note = Note.query.filter_by(
        id=note_id,
        user_id=current_user_id
    ).first()

    if not note:
        return {"error": "Note not found"}, 404

    db.session.delete(note)
    db.session.commit()

    return {}, 204


if __name__ == "__main__":
    app.run(port=5555, debug=True)