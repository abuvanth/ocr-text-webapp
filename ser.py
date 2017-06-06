import os
import glob
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))#
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        os.system("sudo rm -rf "+os.getcwd()+"/uploads/*.txt")#delete old text files
	os.system("sudo rm -rf "+os.getcwd()+"/uploads/*.jpg")
        files = []
        if filename.lower().endswith('.pdf'):
           os.system("convert -density 300 "+os.getcwd()+"/uploads/"+filename+" -quality 100 "+os.getcwd()+"/uploads/output-%03d.jpg")
           for filename in glob.glob(os.getcwd()+"/uploads/"+'*.jpg'):
                       files.append(filename)
        else:
             filename=os.getcwd()+'/uploads/'+filename
             files.append(filename)

        for image in sorted(files):
	#print "uploading " + image
	        command = "gdput.py -t ocr "+image+" > result.log"
	#print "running " + command
	        os.system(command)
	
	        resultfile = open("result.log","r").readlines()
	
	        for line in resultfile:
		        if "id:" in line:
			        fileid = line.split(":")[1].strip()
			        filename = image.split(".")[0] + ".txt"
			        get_command = "gdget.py -f txt -s " + filename + " " + fileid
			#print "running "+ get_command
			        os.system(get_command)


#print "Merging all text files into ocr-result.txt"
	
        files = glob.glob(os.getcwd()+'/uploads/'+'*.txt')

        with open(os.getcwd()+'/uploads/ocr-result.txt', 'w' ) as result:
            for textfile in files:
                for line in open( textfile, 'r' ):
                    result.write( line )
        return redirect(url_for('uploaded_file',
                                filename='ocr-result.txt'))


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')#/uploads
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("80"),
        debug=True
    )
