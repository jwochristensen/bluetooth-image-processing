#http://127.0.0.1:5000
#http://127.0.0.1:5000/send_ble/
#http://127.0.0.1:5000/print_console/
#installing flask in virtual env
#https://stackoverflow.com/questions/24525588/how-to-install-flask-on-python3-using-pip
#https://www.geeksforgeeks.org/flask-creating-first-simple-application/
#https://www.baeldung.com/linux/pip-fix-externally-managed-environment-error

#bluetooth messenger w/ socket
#https://stackoverflow.com/questions/62652901/how-do-i-broadcast-bluetooth-inquiry-with-python-sockets-af-bluetooth-socket
#https://www.youtube.com/watch?v=8pMaR-WUc6U

#from top directory:
#source myvirtualenv/bin/activate
#get dependencies from venv: https://stackoverflow.com/questions/15961926/how-can-i-make-a-list-of-installed-packages-in-a-certain-virtualenv

# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, request
#import sys

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Hello World'

@app.route('/send_ble/', methods=['POST'])
# ‘/’ URL is bound with hello_world() function.
def ble_message_send():
    if request.method == 'POST':
        msg = request.json['msg']
        msg_str = str(msg)

        return_msg = 'We received your message: ' + msg_str

        return return_msg

# @app.route('/print_console/')
# # ‘/’ URL is bound with hello_world() function.
# def print_console():
#     print('this message will print to console', file=sys.stderr)
#     return redirect('/')

# main driver function
if __name__ == '__main__':

    # run() method of Flask class runs the application 
    # on the local development server.
    app.run()
