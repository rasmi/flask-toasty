from flask import Flask, flash, request, redirect, url_for, send_from_directory, send_file
import os
import shutil
import json
import healpy as hp
from toasty import toast, healpix_sampler
from werkzeug.utils import secure_filename
from pprint import pprint

app = Flask(__name__)
app.secret_key = 'secret'

UPLOAD_FOLDER = 'converted/'
ALLOWED_EXTENSIONS = set(['fits'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def convert_toast(filename):
    print "CONVERTING"
    data = hp.read_map(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    data_name = filename.rsplit('.', 1)[0]
    output_dir = os.path.join(app.config['UPLOAD_FOLDER'], data_name)
    sampler = healpix_sampler(data)
    depth = 4
    toast(sampler, depth, output_dir)

    shutil.make_archive(output_dir, 'zip', output_dir)  

    return data_name+'.zip'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    return send_from_directory('.', 'index.html')

@app.route('/convert', methods=['GET', 'POST'])
def convert():
    print "GOT CONVERT REQUEST"
    if request.method == 'POST':
        print 'GOT POST REQUEST'
        print request.files
        if 'file' not in request.files:
            return 'No file!'
        file = request.files['file']
        if file.filename == '':
            return 'No filename!'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            zip_file = convert_toast(filename)

            return redirect(url_for('uploaded_file', filename=zip_file))
        elif not allowed_file(file.filename):
            return 'Please upload a valid FITS file.'
    elif request.method == 'GET':
        return send_from_directory('.', 'index.html')
    else:
        return 'Something went wrong.'

@app.route('/converted/<filename>')
def uploaded_file(filename):
    return send_file(app.config['UPLOAD_FOLDER']+filename)

if __name__ == '__main__':
    app.run(debug=True)