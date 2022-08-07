from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/todo'
db = SQLAlchemy(app)



class Todo(db.Model):
   __tablename__ = "todos"
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(20))
   todo_description = db.Column(db.String(100))

   def to_json(self):
        return {
            'title': self.title,
            'todo_description': self.todo_description
        }


   def __init__(self, title, todo_description):
       self.title = title
       self.todo_description = todo_description

   def __repr__(self):
       return f"{self.id}"

db.create_all()

@app.before_first_request
def create_table():
    db.create_all()

class TodoSchema(SQLAlchemyAutoSchema):
   class Meta:
       model = Todo
       sqla_session = db.session
       include_relationships = True
       load_instance = True
   id = fields.Number(dump_only=True)
   title = fields.String(required=True)
   todo_description = fields.String(required=True)


from flask import request
@app.route('/api-objects', methods=['POST'])
def create_obj():
    book = Todo(
        title=request.json.get('title'),
        todo_description=request.json.get('todo_description'),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_json()), 201

@app.route('/api-objects', methods=['GET'])
def index():
   get_todos = Todo.query.all()
   todo_schema = TodoSchema(many=True)
   todos = todo_schema.dump(get_todos)
   return make_response(jsonify({"todos": todos}))


@app.route('/api-objects/<id>', methods=['GET'])
def get_todo_by_id(id):
   get_todo = Todo.query.get(id)
   todo_schema = TodoSchema()
   todo = todo_schema.dump(get_todo)
   return make_response(jsonify({"todo": todo}))


   
@app.route('/api-objects/<id>', methods=['PUT'])
def update_todo_by_id(id):
   data = request.get_json()
   get_todo = Todo.query.get(id)
   if data.get('title'):
       get_todo.title = data['title']
   if data.get('todo_description'):
       get_todo.todo_description = data['todo_description']
   db.session.add(get_todo)
   db.session.commit()
   todo_schema = TodoSchema(only=['id', 'title', 'todo_description'])
   todo = todo_schema.dump(get_todo)

   return make_response(jsonify({"todo": todo}))


   
@app.route('/api-objects/<id>', methods=['DELETE'])
def delete_todo_by_id(id):
   get_todo = Todo.query.get(id)
   db.session.delete(get_todo)
   db.session.commit()
   return make_response("", 204)