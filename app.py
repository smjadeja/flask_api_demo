from flask import Flask, jsonify, request,json,Response
from flask.views import MethodView
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_sqlalchemy import sqlalchemy
import re
#app configurations
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def getuser_by_id(id):
    user = Users.query.filter_by(id=id).first()
    return user

def get_user(id):
    user = Users.query.filter_by(id=id).first()
    if user:
        return {"id":user.id,"firstname":user.First_Name, "email":user.Email, "mobile":user.Mobile,"date_of_brith":user.Date_of_Birth}
    return False

def get_all_user():
    users = Users.query.all()
    data = [{"id":i.id,"firstname":i.First_Name, "email":i.Email, "mobile":i.Mobile,"date_of_brith":i.Date_of_Birth} for i in users]
    return data

def handle_error(k):
    return k.to_resp()

def handle_404_error(k):
    return ResultApi('', message = 'bad request', success=False, status=400)




class NewResponse(Flask):
    def make_response(self, r):
        if isinstance(r,ResultApi):
            return r.to_json()
        return Flask.make_response(self, r)

app = NewResponse(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class ApiException(Exception):
    def __init__(self, message, success=False):
        self.message = message
        self.success = success
    
    def to_resp(self):
        return ResultApi({},message=self.message,success=self.success)


class ResultApi:
    def __init__(self, result, message="",success=True,status=200):
        self.result = result
        self.success = success
        self.status = status
        self.message = message

    def to_json(self):
        return Response(json.dumps({"success":self.success,"result":self.result, "status":self.status,"message":self.message}), status=self.status)

#model for user
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    First_Name = db.Column(db.String(80), nullable=False)
    Email = db.Column(db.String(80), unique= True, nullable=False)
    Mobile = db.Column(db.Integer, nullable=False)
    Password =  db.Column(db.String(80), nullable = False)
    Date_of_Birth = db.Column(db.String(10), nullable = False)

#class view for user related opration

class UserApi(MethodView):
    def get(self, id):
            if id:
                if get_user(id):
                    return ResultApi(get_user(id))
                return ResultApi({}, success=False, status=404, message='user not found')
            return ResultApi(get_all_user(), message="list of all users")

    def post(self,id):
        try:
            firstname = request.json["firstname"]
            email = request.json["email"]
            mobile = request.json['mobile']
            password = request.json["password"]
            date_of_birth = request.json["date_of_birth"]
            if firstname == "":
                return ResultApi({},'please enter first name',success=False)
            if email == "":
                return ResultApi('', "please enter email",success=False)
            if not (re.fullmatch(regex, email)):
                return ResultApi({},'please enter a valid email address',success=False)
            if Users.query.filter_by(Email=email).first():
                return ResultApi({}, message='email already exists',success=False)
            if mobile== "":
                return ResultApi({},'mobile number is incorrect',success=False)
            if len(str(mobile)) > 10:
                return ResultApi({},'please enter only 10 digit',success=False)
            if password == "":
                return ResultApi({},'please enter password',success=False)
            if date_of_birth == "":
                return ResultApi('', "please enter birthdate",success=False)
            newuser = Users(First_Name=firstname,Email=email,Mobile=mobile,Password=password, Date_of_Birth=date_of_birth)
            db.session.add(newuser)
            db.session.commit()
            return ResultApi(get_user(newuser.id), message='user created successfully')

        except KeyError:
            raise ApiException('you didnt entered all keys or values')
        except Exception:
            raise ApiException('something went wrong')

    def put(self,id):
        try:
            if Users.query.filter_by(id=id).first():
                user = Users.query.filter_by(id=id).first()
                user.First_Name = request.json['firstname']
                if Users.query.filter_by(Email=request.json['email']).first():
                    return ResultApi({},'email already exists',success=False)
                if not (re.fullmatch(regex, request.json['email'])):
                    return ResultApi({},'please enter a valid email address,success=False')
                user.Email = request.json['email']
                user.Mobile = request.json['mobile']
                user.Date_of_Birth = request.json['date_of_birth']
                if user.First_Name == "":
                    return ResultApi({},'please enter firstname',success=False)
                if user.Mobile == "":
                    return ResultApi({},'mobile number is incorrect',success=False)
                if len(str(user.Mobile)) > 10:
                    return ResultApi({},'please enter only 10 digit',success=False)
                if user.Date_of_Birth == "":
                    return ResultApi({},'please enter date of birth',success=False)
                db.session.commit()
                return ResultApi(get_user(id), message='profile updated successfully',success=False)
            return ResultApi({}, message='please enter valid id',success=False)
        except KeyError:
            raise ApiException('you didnt entered all keys or values')
        except Exception:
            raise ApiException('something went wrong')

    def delete(self,id):
        try:
            if id:
                if Users.query.filter_by(id=id).first():
                    user = Users.query.get(id)
                    db.session.delete(user)
                    db.session.commit()
                    return ResultApi({}, message='deleted successfully')
                return ResultApi({},'no user exists with this id',success=False)
            return ResultApi({},'please enter valid id',success=False)
        except KeyError:
            raise ApiException('you didnt entered all keys or values')
        except Exception:
            raise ApiException('something went wrong')


user_api = UserApi.as_view('user_api')

class Userlogin(MethodView):
    def post(self):
        try:
            id = request.json['id']
            if id:
                a = Users.query.filter_by(id=id).first()
                if a:
                    if a.Email == request.json['email'] and a.Password == request.json['password']:
                        return ResultApi({}, message="logged in successfully")
                    return ResultApi({}, message="email or password is incorrect",success=False)
                return ResultApi({},'please enter valid id',success=False)
            return ResultApi('id should not be empty',success=False)   
        except KeyError:
            raise ApiException('something went wrong')
        except Exception:
            raise ApiException('something went wrong')

user_login = Userlogin.as_view('user_login')

class ChangePassword(MethodView):
    def post(self):
        try:
            id = request.json["id"]
            if id:
                a = getuser_by_id(id)
                if a:
                    if request.json['oldpassword'] == "" or request.json['newpassword'] == "": 
                        return ResultApi('',"passwrods should not be empty",success=False)
                    if not a.Password == request.json['oldpassword']:
                        return ResultApi('', "you have entered wrong old password",success=False)
                    if request.json['oldpassword'] == request.json['newpassword']:
                        return ResultApi('', 'new password should not be same as old',success=False)
                    a.Password = request.json['newpassword']
                    db.session.commit()
                    return ResultApi('', 'password changed succesfully')
        except KeyError:
            raise ApiException('all keys are required')
        except Exception:
            raise ApiException('something went wrong')
    
        
             
change_password = ChangePassword.as_view('change_password')

class ForgotPassword(MethodView):
    def post(self):
        try:
            a = request.json['email']
            if a:
                if (re.fullmatch(regex,a)):
                    if Users.query.filter_by(Email=a).first():
                        return ResultApi({}, message="Check your inbox we have sent reset link on your email")
                    return ResultApi({}, message="no user found with this email",success=False)
                return ResultApi('','please enter valid email',success=False)
            return ResultApi('', 'please enter email',success=False)
        except KeyError:
            raise ApiException('all keys are required')
        except Exception:
            raise ApiException('something went wrong')
        


forgot_password = ForgotPassword.as_view('forgot_password')


#url end points
app.add_url_rule('/api/users/', methods=['GET','POST'], defaults={'id':None}, view_func=user_api)
# app.add_url_rule('/api/users/', methods=[], defaults={'id':None}, view_func=user_api)
app.add_url_rule('/api/users/<int:id>', methods=['GET', 'PUT', 'DELETE'], view_func=user_api)
app.add_url_rule('/api/users/login/', methods=['POST'], view_func=user_login)
app.add_url_rule('/api/changepassword/', methods=['POST'], view_func = change_password)
app.add_url_rule('/api/forgotpassword/', methods=['POST'], view_func=forgot_password)


app.register_error_handler(ApiException, handle_error)
app.register_error_handler(404 , handle_404_error)

if __name__=='__main__':
    app.run(debug=True)
