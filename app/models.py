from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from main import app 
from flask_admin.contrib.sqla import ModelView
from flask import flash,redirect,abort,url_for

db = SQLAlchemy()

class User(db.Model,UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255))
	username = db.Column(db.String(255), unique=True)
	email = db.Column(db.String(255),unique=True)
	password = db.Column(db.String(255))
	confirm_at = db.Column(db.DateTime)
	confirm = db.Column(db.Boolean(),default=False)
	registration_code = db.Column(db.Integer, unique=True)
	active=db.Column(db.Boolean(),default=False)
	role=db.Column(db.Boolean(),default=False)


class LoadView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated == False:
			return self.inaccessible_callback(abort(404))
		elif current_user.is_authenticated and current_user.role == True:
			return current_user.is_authenticated
		else:
			return("error") #redirect(url_for('index'))
			
		
		


		
	def inaccessible_callback(self, name, **kwargs):
		return("sorry you cant access this")
	can_create = True
	can_edit = True
	can_delete = True


