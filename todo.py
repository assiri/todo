#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask import Flask,request,  Response, json
sys.path.append('pydal')
from pydal import DAL, Field
class JSONDateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)

def model():
    db = DAL('sqlite://todo.db',pool_size=1,folder='./') #,migrate=False)
    Todos=db.define_table('todos',Field('title'),Field('isCompleted','boolean',default=False))
    if not db(db.todos).count():
      for i in range(1,16):
        db.todos.insert(title='الموعد '+str(i))
        db.commit()

    return (db)

#app = Flask(__name__, static_url_path='')
app = Flask(__name__, static_url_path='/dist')
@app.route('/')
def index():
    return app.send_static_file("index.html")

@app.route('/api/<tablename>',methods=['GET',"POST"])
@app.route('/api/<tablename>/<mid>',methods=["PUT","DELETE"])
def api(tablename,mid=None):
    db=model()
    if request.method=="GET":
        table = db[tablename]
        query = table.id>0
        rows = db(query).select().as_list()
        return Response(json.dumps({'todo':rows},cls=JSONDateTimeEncoder), mimetype='application/json')
    elif request.method=="POST":
        data=request.json.get('todo') #request.get_data()
        id=db[tablename].insert(**data)
        db.commit()
        data[id]=id
        return Response(json.dumps(data,cls=JSONDateTimeEncoder), mimetype='application/json')

    elif request.method=="PUT":
        data=request.json.get('todo') #request.get_data()
        db(db[tablename]._id==int(mid)).update(**data)
        db.commit()
        data['id']=mid
        return Response(json.dumps({'todo':data},cls=JSONDateTimeEncoder), mimetype='application/json')

    elif request.method=="DELETE":
        db(db[tablename]._id==int(mid)).delete()
        db.commit()
        return Response(json.dumps({}))


app.debug = True

if __name__ == "__main__":
  app.run()
