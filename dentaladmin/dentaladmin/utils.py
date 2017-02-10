# List of common connections and functions
import datetime
import pymongo
import hashlib
import random
import string


client = pymongo.MongoClient('db', 27017)
database_connection = client.dentaladmin
database_errors = pymongo.errors


def make_pw_hash(password):
    password = password.encode('utf-8')
    return hashlib.sha256(password).hexdigest()


def get_random_str(num_chars):
    random_string = ""
    for i in range(num_chars):
        random_string = random_string + random.choice(string.ascii_letters)
    return random_string


def validate_form(request):
    for key in request:
        if 'file' in request:
            pass
        else:
            value = request[key]
            if value is None or value == "":
                return False
    if 'password' in request:
        if request['password'] != request['password2']:
            return False
    return True


def upload_file_verification(file, username):
    formats = ['image/jpg', 'image/jpeg', 'image/png', 'image/bmp']
    if file.content_type in formats:
        pic = 'img/avatars/{0}-{1}'.format(username, file.name)
        return pic
    else:
        return False


def upload_file(pic, file):
        path = 'static/{0}'.format(pic)
        with open(path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return True


def get_today_date(date_format="%m/%d/%Y"):
    return datetime.date.today().strftime(date_format)
