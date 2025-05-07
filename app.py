from models import db, Documents
from flask_migrate import Migrate
from flask import Flask, request, jsonify
import os
app=Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
db.init_app(app)
migrate = Migrate(app, db)
@app.route('/documents', methods=['GET', 'POST'])
def get_documents():
    if request.method == 'GET':
        documents = Documents.query.all()
        return jsonify([document.to_dict() for document in documents]), 200
    if request.method == 'POST':
        
        name = request.form.get('name')
        document = request.files.get('document')
        type = request.form.get('type')
        description = request.form.get('description')
        if not document:
            return jsonify({"message": "No file provided"}), 400
        document = Documents(name=name, description=description, document=document.read(), type=type)
        
        db.session.add(document)
        db.session.commit()
        return jsonify({"message": "Document created successfully"}), 201
    
    
    
    
if __name__ == '__main__':
    app.run(debug=True)