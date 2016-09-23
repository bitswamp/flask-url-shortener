from datetime import datetime, timedelta
from flask import Flask, Markup
from flask import flash, jsonify, redirect, render_template, request, url_for
from flask import abort, send_from_directory
from os import path
from peewee import SqliteDatabase, Model
from peewee import PrimaryKeyField, CharField, BooleanField, DateTimeField
import short_url

# routes

app = Flask(__name__)
app.config["PREFERRED_URL_SCHEME"] = "https"  # doesn't seem to affect url_for
app.config["SECRET_KEY"] = ";oisdhfaosigf"  # needed for flashing

URLS_PER_IP_PER_HOUR = 20
URLS_PER_TOKEN_PER_HOUR = 1000

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/shorten")
def shorten():
    long_url = request.args.get("url")
    token = request.args.get("token")
    format = request.args.get("format", "simple")
    ip = request.headers.get("X-Forwarded-For")

    if rate_limit_exceeded(ip, token):
        if format == "html":
            return redirect_and_flash(render_template("rate_limit_exceeded.html"))
        else:
            abort(429)

    url = Url(url=long_url)
    url.save()

    log_ip = Ip(ip=ip, token=token, time=datetime.now())
    log_ip.save()

    root_url = url_for("index", _external=True, _scheme="https")
    slug = short_url.encode_url(url.id)
    new_url = root_url + slug

    print(new_url)

    if format == "html":
        return redirect_and_flash(render_template("new_url.html", new_url=new_url))
    elif format == "json":
        return jsonify(url=new_url)

    return new_url


def rate_limit_exceeded(ip, token):
    Ip.delete().where(Ip.time < datetime.now() + timedelta(hours=-1))
    count = Ip.select().where(Ip.ip == ip).count()
    print(ip + " - " + str(count))
    return count >= URLS_PER_IP_PER_HOUR;


def redirect_and_flash(flash_template):
    template = Markup(flash_template)
    flash(template)
    return redirect(url_for("index", _external=True, _scheme="https"))


@app.route("/<slug>")
def unshorten(slug):
    if path.isfile(path.join("static", slug)):
        return send_from_directory("static", slug)

    try:
        id = short_url.decode_url(slug)
        url = Url.get(Url.id == id)
        return redirect(url.url)
    except:
        # invalid url or not found
        abort(404)

# database

urls = SqliteDatabase("urls.db")
auth = SqliteDatabase("auth.db")


class Url(Model):
    id = PrimaryKeyField()
    url = CharField()
    class Meta:
        database = urls


class Token(Model):
    token = CharField()
    valid = BooleanField()
    class Meta:
        database = auth


class Ip(Model):
    ip = CharField(index = True)
    token = CharField(index = True)
    time = DateTimeField(index = True)
    class Meta:
        database = auth


def init_db():
    print("Checking for databases ...")
    if path.isfile("urls.db") and path.isfile("auth.db"):
        print("Databases exist.")
        return

    print("Creating urls database ...")
    urls.connect()
    urls.create_tables([Url])

    print("Creating auth database ...")
    auth.connect()
    auth.create_tables([Token, Ip])

if __name__ == "__main__":
    init_db()
    app.run()
