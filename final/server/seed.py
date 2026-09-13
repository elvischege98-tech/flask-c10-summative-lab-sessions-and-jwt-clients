from faker import Faker
from flask_bcrypt import Bcrypt

from app import app
from models import db, User, Note


fake = Faker()
bcrypt = Bcrypt(app)


with app.app_context():

    print("Clearing existing data...")

    Note.query.delete()
    User.query.delete()

    db.session.commit()

    print("Creating users...")

    users = []

    for _ in range(5):
        password = bcrypt.generate_password_hash("password123").decode("utf-8")

        user = User(
            username=fake.unique.user_name(),
            password=password
        )

        users.append(user)
        db.session.add(user)

    db.session.commit()

    print("Creating notes...")

    for user in users:
        for _ in range(3):
            note = Note(
                title=fake.sentence(nb_words=4),
                content=fake.paragraph(),
                user_id=user.id
            )

            db.session.add(note)

    db.session.commit()

    print("Database seeded successfully!")