from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from os import path
from peewee import *
import sqlite3
import short_url

# routes

app = Flask(__name__)
app.config["PREFERRED_URL_SCHEME"] = "https" # doesn't seem to affect url_for
app.config["SECRET_KEY"] = ";oisdhfaosigf" # needed for flashing

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/shorten")
def shorten():
    long_url = request.args.get("url", "")
    token = request.args.get("token", "")
    format = request.args.get("format", "")

    url = Url(url = long_url)
    url.save()

    root_url = url_for("index", _external = True, _scheme = "https")
    slug = short_url.encode_url(url.id)
    new_url = root_url + slug

    print(new_url)

    if format == "html":
        flash(new_url)
        return redirect(url_for("index", _external = True, _scheme = "https"))
    elif format == "json":
        return jsonify(url = new_url)

    return new_url

@app.route("/<slug>")
def unshorten(slug):
    id = short_url.decode_url(slug)
    url = Url.get(Url.id == id)
    return redirect(url.url)

# database

db = SqliteDatabase("urls.db")

class Url(Model):
    id = PrimaryKeyField()
    url = CharField()

    class Meta:
        database = db

def init_db():
    print("Checking for database ...")
    if path.isfile("urls.db"):
        print("Database exists.")
        return;

    print("Creating database ...")
    db.connect()
    db.create_tables([Url])

if __name__ == "__main__":
    init_db()
    app.run()

