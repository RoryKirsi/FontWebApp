import os
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def check_file_not_exist(file_path, filename):
    if os.path.exists(file_path):
        if os.path.isfile(file_path+filename):
            return False
        else:
            return True
    else:
        os.mkdir(file_path)
        return True