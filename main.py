from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float
import os

app = Flask(__name__)

db_path = os.path.abspath("instance/cafes.db")
if not os.path.exists(db_path):
    raise FileNotFoundError(f"Database not found at: {db_path}")

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"

db = SQLAlchemy(app)

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    return render_template("index.html", cafes=all_cafes)

@app.route("/all", methods=["GET"])
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search", methods=["GET"])
def get_cafes():
    query_location = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

@app.route("/add", methods=["POST"])
def post_new_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = db.session.get(Cafe, cafe_id)
    if cafe is None:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    db.session.delete(cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200

if __name__ == '__main__':
    app.run(debug=True)