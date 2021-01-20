from flask import Flask, send_file, jsonify, flash, request, redirect, url_for, send_from_directory
import txt2img, functions, os
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

UPLOAD_FOLDER = './Fonts/'
ALLOWED_EXTENSIONS = {'otf', 'ttf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

@app.route('/')
def hello():
    return 'hello wow'

@app.route('/get_image/<string:text>/<int:width_size>/<int:height_size>/<string:align>/<int:spacing>/<string:font>/<string:color>/<string:size_change_code>', methods=['GET'])
def get_image(text, width_size, height_size, align, spacing, font, color, size_change_code):
    str_spacing = str(spacing)
    font_path = '../Fonts/'
    font_name = font.split('.')[0]
    font_format = '.'+font.split('.')[1]
    print("calling font:"+font)
    img_str, font_size = txt2img.make_test_img(text, align, str_spacing, font_path, font_name, font_format, color)
    print("font size: (" + str(font_size[0]) + "," + str(font_size[1]) + ")")
    new_font_size = txt2img.adjust_font_size(size_change_code, width_size, height_size, font_size[0], font_size[1])
    print("new font size: (" + str(new_font_size[0]) + "," + str(new_font_size[1]) + ")")
    print("returning image")

    return jsonify(img_str, new_font_size)

@app.route('/get_fonts', methods=['GET'])
def get_font():
    font_path = 'Fonts/'
    fonts = txt2img.read_dic(font_path)
    return jsonify(fonts)

@app.route('/upload_fonts', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and functions.allowed_file(file.filename, ALLOWED_EXTENSIONS):
            filename = secure_filename(file.filename)
            print('uploaded ' + filename)
            if functions.check_file_not_exist(app.config['UPLOAD_FOLDER'], filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('uploaded_file', filename=filename))
            else:
                return redirect(url_for('uploaded_existed_file', filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return 'Success uploaded ' + filename + '.'

@app.route('/uploads_existed/<filename>')
def uploaded_existed_file(filename):
    return 'Font type file ' + filename + ' already existed.'

# @app.route('/sample/<filename>')
# def loading_sample(filename):
#     return send_from_directory('html_temp', filename)

if __name__ == '__main__':
    sys.stdout.flush()
    app.run(debug=True, host="0.0.0.0", port="5000")