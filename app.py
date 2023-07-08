from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/login')
def index():
    return render_template('userLogin.html')

@app.route('/signup')
def signup():
	return render_template('userSignup.html')

@app.route('/forgetpsw')
def forgetpsw():
	return render_template('userForget.html')

@app.route('/reset')
def resetpsw():
	return render_template('resetPassword.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)