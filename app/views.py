from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user 
import aiml
import os
from models import db
from flask_sqlalchemy import SQLAlchemy 
from main import app
from models import *
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import random 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import uuid
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

otp=uuid.uuid4()

k = aiml.Kernel()

BRAIN_FILE="brain.dump"
if os.path.exists(BRAIN_FILE):
	print("loading brain")
	k.loadBrain(BRAIN_FILE)
else:
	print("Parsing aiml files")
	k.bootstrap(learnFiles="std-startup.aiml", commands="load aiml b")
	print("Saving brain file: " + BRAIN_FILE)
	k.saveBrain(BRAIN_FILE)
mail =Mail(app)
s = URLSafeTimedSerializer("jkhfkjsjksfkjhhfdkjhfdskjfkd")



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "signin"
db.init_app(app)


admin = Admin(app,name='Control Panel')
admin.add_view(LoadView(User,db.session))




@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))




@app.route('/')
def homepage():
	return render_template('./home.html')
def main():
	return redirect(url_for('index'))
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
	if request.method =='POST':
		user_input = request.form['chat']
		response = k.respond(user_input)
	

		return render_template('index.html',response=response,
			user_input=user_input)
	return render_template('index.html')


@app.route('/signup',methods=['GET','POST'])
def signup():
	if request.method =='POST':

		name = request.form['name']
		email = request.form['email']
		username = request.form['username']
		password = request.form['password']
		con_password = request.form['con_password']
		#otp = random.randint(4264624624,57337377637637)
		if con_password == password:
			token = s.dumps(email,salt='confirm-email')
			msg = Message('Confirm Account', sender='noreply@admin.com', recipients=[email])
			link = url_for('confirm_email',token=token,_external=True)
			onetp = otp
			msg.body = str(onetp)+" Here is your registration code click the clink to validate it "+str(link)
			mail.send(msg)
			hashed_password =generate_password_hash(password,method='sha256')
			new_user = User(name=name,username=username,
				email=email,password=hashed_password,registration_code=onetp)
			db.session.add(new_user)
			db.session.commit()
			flash("you hava succefully sign up")
			return redirect(url_for('homepage'))
		else:
			flash("sorry your password did not match")
			return redirect(url_for('signup'))
		

	return render_template('signup.html')

@app.route('/confirm_email/<token>')
def confirm_email(token):
	try:
		email = s.loads(token,salt='confirm-email',max_age=600)
		return redirect(url_for('validate'))
	except SignatureExpired:
		flash("sorry the verification link is expired!!!!")
		return redirect(url_for('home'))
@app.route('/validate',methods=['GET','POST'])
def validate():
	if request.method=='POST':
		code = request.form['code']
		valdate = User.query.filter_by(registration_code=code).first()
		if valdate:
			valdate.confirm = True
			valdate.confirm_at = datetime.now()
			db.session.commit()
			flash("Your email is confirmed you can now login")
			return redirect(url_for('signin'))
		else:
			flash("sorry incorrect key")
			return redirect(url_for('homepage'))	

	return render_template('./confirm.html')

@app.route('/signin',methods=['GET','POST'])
def signin():
	if request.method == 'POST':
		username = request.form['name']
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user and user.confirm:
			if check_password_hash(user.password,password):
				login_user(user)
				current_user.active = True
				db.session.commit()
				return redirect(url_for('index'))
			else:
				flash("invalid password")
				return redirect(url_for('signin'))
		else:
			flash("sorry invalid username or you have not confirm your email address please check your email to verify")
			return redirect(url_for('signin'))
	return render_template('signin.html')




@app.route('/logout')
@login_required
def logout():
	current_user.active=False
	db.session.commit()
	logout_user()
	flash("you have succefully logout man!!!!")
	return(redirect(url_for('index')))


@app.route("/database")
def database():
	db.create_all()
	return("database table is created")
@app.route('/delete')
def deleetall():
	db.drop_all()
	return("database droped succefully")