import json
import os
from db import Asset, Post, Day, db
from flask import Flask, request

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(data, code = 200):
    return json.dumps(data), code

def failure_response(message, code = 404):
    return json.dumps({"error": message}), code


@app.route("/upload/", methods=["POST"])
def upload():
    """
    Endpoint for uploading an image to AWS given its base64 form,
    then storing/returning the URL of that image
    """
    body = json.loads(request.data)
    image_data= body.get("image_data")
    if image_data is None:
        failure_response("No base64 image fonud!")
    
    asset = Asset(image_data=image_data)
    db.session.add(asset)
    db.session.commit()

    return success_response(asset.serialize(), 201)


@app.route("/day/", methods=["POST"])
def create_day():
    """
    Endpoint for creating a new day
    """
    body = json.loads(request.data)
    date = body.get("date")
    overall_rating = body.get("overall_rating")
    if date is None or overall_rating is None:
        return failure_response("Information missing!", 400)
    new_day = Day(date=date, overall_rating=overall_rating)
    db.session.add(new_day)
    db.session.commit()
    return success_response(new_day.serialize(), 201)


@app.route("/day/posts/", methods=["POST"])
def create_post():

    body = json.loads(request.data)
    location=body.get("location")
    rating=body.get("rating")
    text=body.get("text")
    pic_url=body.get("pic")
    date_str=body.get("date_str")


    if date_str is None or body is None or location is None or rating is None or text is None or pic_url is None:
        return failure_response("Invalid response body!", 400)
    
    day = Day.query.filter_by(date=date_str).first()
    if day is None:
        day = Day(date=date_str, overall_rating=0)
        db.session.add(day)
        db.session.commit()


    post = Post(
        location=location,
        rating=rating,
        text=text,
        day_id=day.id,
        pic=pic_url
    )

    no_days = Day.query.count() + 1
    print(no_days)
    new_rating = (day.overall_rating + rating) / no_days
    print(new_rating)
    day.update_rating(new_rating)

    db.session.add(post)
    db.session.commit()
    return success_response(post.serialize(), 201)


@app.route("/posts/<int:user_id>/")
def get_post_by_id(user_id):
    """
    Get posts by id.
    """
    post = Post.query.filter_by(id=user_id).first()
    if post is None:
        return failure_response("Post not found!")
    return success_response(post.serialize())


@app.route("/posts/day/<int:day_id>/")
def get_post_by_day(day_id):
    """
    Get posts by day
    """
    day = Day.query.filter_by(id=day_id).first()
    if day is None:
        return failure_response("Invalid day was provided!")
    
    day_json = day.serialize()
    posts = day_json.get("posts")

    if posts is None:
        return failure_response("No posts!", 400)

    return success_response(posts)


@app.route("/posts/<int:id>/", methods=["DELETE"])
def delete_post(id):
    """
    Endpoint for deleting a post by its id
    """
    post = Post.query.filter_by(id=id).first()
    if post is None:
        return failure_response("Course not found")
    db.session.delete(post)
    db.session.commit()
    return success_response(post.serialize())



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)