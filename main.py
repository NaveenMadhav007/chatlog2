from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatLog.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    userId = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Log(db.Model):
    __tablename__ = 'logs'
    logId = db.Column(db.Integer, primary_key=True)
    chatLog = db.Column(db.String(1000), nullable=False)
    fromUserId = db.Column(db.Integer, nullable=False)
    toUserId = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return """  <h1> Welcome to chat log api </h1> <br> 
                <a href="https://documenter.getpostman.com/view/15835142/2s9YRDzVuL">View documentation</a>
            """

@app.route('/all_users', methods=['GET'])
def get_all_users():
    all_users = db.session.query(User).all()

    return jsonify(users=[user.to_dict() for user in all_users]), 200

@app.route('/all_chatLogs', methods=['GET'])
def get_all_logs():
    all_logs = db.session.query(Log).all()

    return jsonify(logs=[log.to_dict() for log in all_logs]), 200

@app.route('/new_user', methods=['POST'])
def post_new_user():
    newUserName = request.form.get('userName')
    newUserId = 0
    if len(db.session.query(User).all()) != 0:
        newUserId = db.session.query(User).order_by(User.userId.desc()).first().userId + 1

    newUser = User(userId=newUserId,
                   userName=newUserName)
    
    db.session.add(newUser)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new user."}), 200

@app.route('/new_chatLog', methods=['POST'])
def post_new_log():
    new_chat_log = request.form.get('log')
    fromUserId = request.form.get('fromUserId')
    toUserId = request.form.get('toUserId')
    newChatLogId = 0

    if len(db.session.query(Log).all()) != 0:
        newChatLogId = db.session.query(Log).order_by(Log.logId.desc()).first().logId + 1

    new_log = Log(logId=newChatLogId,
                  chatLog=new_chat_log,
                  fromUserId=fromUserId,
                  toUserId=toUserId)
    
    db.session.add(new_log)
    db.session.commit()

    return jsonify(response={"success": "Successfully added the new chat to Log."}), 200

@app.route('/update_userName', methods=['PATCH'])
def update_userName():
    userId = request.form.get('userId')
    newUserName = request.form.get('newUserName')
    
    user = db.session.query(User).get(userId)

    if user != None:
        user.userName = newUserName
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the userName."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry user with that id was not found in the database."}), 404

@app.route('/update_chatLog', methods=['PATCH'])
def update_chatLog():
    logId = request.form.get('logId')
    newChatLog = request.form.get('newChatLog')

    chatLog = db.session.query(Log).get(logId)

    if chatLog != None:
        chatLog.chatLog = newChatLog
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the chatLog."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry chatLog with that id was not found in the database."}), 400


@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    userId = request.form.get('userId')

    user = db.session.query(User).get(userId)

    if user != None:

        logs = list(db.session.query(Log).filter(Log.fromUserId == user.userId))

        logs.extend(list(db.session.query(Log).filter(Log.toUserId == user.userId)))

        
        for log in logs: 
            db.session.delete(log)
        
        db.session.delete(user)
        db.session.commit()

        return jsonify(response={"success": "Successfully deleted user from the database."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry user with that id was not found in the database."}), 404
    

@app.route('/delete_chatLog', methods=['DELETE'])
def delete_chatLog():
    logId = request.form.get('logId')

    chatLog = db.session.query(Log).get(logId)

    if chatLog != None:
        db.session.delete(chatLog)

        db.session.commit()

        return jsonify(response={"success": "Successfully deleted chatLog from the database."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry chatLog with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int('3000'), debug=True)

