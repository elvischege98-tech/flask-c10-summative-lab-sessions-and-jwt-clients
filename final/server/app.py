from flask import Flask
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from models import db


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


@app.route("/")
def index():
    return {"message": "Productivity API is running"}


if __name__ == "__main__":
    app.run(port=5555, debug=True)