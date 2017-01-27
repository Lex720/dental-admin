# List of common functions


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
