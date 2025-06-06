from models import db, Documents, User, Projects, Tasks
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Recipients, Tabs, RecipientViewRequest

from flask_migrate import Migrate
from docusign_esign.client.api_exception import ApiException
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from dotenv import load_dotenv
from urllib.parse import urlencode
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = True 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config ['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Ensure sensitive information is loaded from environment variables for security
INTEGRATION_KEY = "eecfce85-a5eb-4490-b1b9-19caadca2e91"
PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAwkRj7bI0eV4hITxGZqOKVq6zCMlbJRb4y+e/Nc82TXYVA2gR
ZWWsOLommSfZ7SkNXkjU3QlyVcaLF49p3fb4rKGSXEq2L23BmUxbO7enVdocAR7J
jvSOdFjzpRcF8rluMblpvyi/RSBNHuYpkEVreR/NcHDheJjjHbvKO25teh570Y2Z
hjqC5mT6e6zJpGod1ZeWYO2KFwIm9xeACZyX3Vo6tf4JWjfcT+Vwo8SFIxhJhfRt
2d10qzDkdXsVSymza6VAwac9icaxiofzHkJKZREiLW8O0M1B/TkyNGDLyTgM4n7q
U5w6indWoD3msGqtS2bEhZWvZ5/ItYlE3YuZEQIDAQABAoIBAFAjvWNzldERgzI+
Nr6lrW5n4CR6SDbLPLSFNCyDACBBW5bNqgt9v2ehZ0XcGjsLKeAgxGswt/Fpl7yO
5XnzJY+1kXawPWrgaLKQPLysXQP+F3pg1H48Jb4aadxLXKFOXIZ3ugdpTEo8coQS
J8hD0vujInFFp8XDsEF2VA1jVxc+Xw627kUK3JuYPcSGRYuYmmguriLiYCGUg2Ei
Ry0/lpcvliuFgXV25vMKojO1il434zB+WJJze1Xm8XNmTldXwjg5KLtHcPVDiIdn
qTPAy08jAyNBDb0z4ZeNyhQReLq//w/2hC6qaFGYsTXP5Yl9d6BIFvawL/z4ckBi
5o2LGlcCgYEA4NQukHpDWg6WtXeEB0rwXVDeQXYeCilYWh9iZDy2K/obraaaU6En
svKmbufuF4OdjJ4zWvpW6usywdAVKXcXkRXU2tPgGMY0kH2OqYSwjbi9E6bZP3jx
uQOWAhwS5RnZAS3P4Xpd2uw5QJjF+Sx+p+0NlEtAjg3snE5eXfywlJsCgYEA3TN8
orvulXtKPU0btwVk2CjwlweGeDw2VwSfUAunUQzCdyg/r2NuZyZz6aVhJ02xaIJJ
2ALGBAi9mvOdWIznx09Az2jg35rdEHKDXSiyzpgNVuPpAAtzZ/PX8X3lpiRb6JSv
54LbWLXfVM8OQnLpKjqoVnOjP4RpG/w7fMmwJcMCgYEAlvOfd/2+7t5QrfJawRK9
o8nCEC2gKa5s1cWwqCBjJ8+7ebIcd/4By5JD0L8ECuGhjGJDlNf0N7JG1/4/1yFQ
v2brDSmokrmxXToP6R1f9SeOO32Q657mnRQdSblTrmLWYoZBxuAD2BM2tXpdodkQ
COuObHzCER6kOKYdkfkxDfUCgYBCwUEB03li/zweV+DfUO9oFKLW0VyReIplpG13
uKyb1x/w2eKuSXGOC5q7jj9NnzLE+VzTpbKgkQq3coGvsYZZLd+/OEV09cV1Kznd
qWSc2GJeMJWmf84qNvqaVIYzp5FdFVIoqeMMWIa3j20cPJWFOwKGZIuFpa4a1foV
5MAWBQKBgQCiWbiqxeQLzKtXDVJv8DJl5aWfaCGDMIxEUTSybGXx2WR0m9XOdZ/s
eBrPloQG1QM66/iR9fA5laHadU4ScxZdHYxyyGuxt7z3nZBOHXP9LW1QCK8ya+v+
NICxYDcUM3KzYYIvTcWftY5UPR7MrF38VwM79cqiriIxFed2eqDynw==
-----END RSA PRIVATE KEY-----"""

USER_ID = "03b9ea64-6bb7-44f7-8e3e-e72a488fc263"

SIGNER_EMAIL = "hosea.mungai@student.moringaschool.com"
SIGNER_NAME = "Hosea Mungai"
ACCOUNT_ID = "42bbd9e3-c44f-4856-9656-fd02cdde6cd7"
RETURN_URL = "http://localhost:4200/"
AUTH_SERVER = "account-d.docusign.com"
CLIENT_USER_ID = "03b9ea64-6bb7-44f7-8e3e-e72a488fc263"
TOKEN_EXPIRATION_IN_SECONDS = 3600
print("Private Key:", PRIVATE_KEY) 
# Step 1: Generate Consent URL
from urllib.parse import urlencode

def generate_consent_url():
    base_url = f"https://{AUTH_SERVER}/oauth/auth"
    params = {
        "response_type": "code",
        "scope": "signature impersonation",
        "client_id": INTEGRATION_KEY,
        "redirect_uri": RETURN_URL
    }
    return f"{base_url}?{urlencode(params)}"

# Step 2: Get Access Token (if consent is granted)
def get_access_token():
    api_client = ApiClient()
    try:
        token_response = api_client.request_jwt_user_token(
            client_id=INTEGRATION_KEY,
            user_id=USER_ID,
            oauth_host_name=AUTH_SERVER,
            private_key_bytes=PRIVATE_KEY.encode("utf-8"),
            expires_in=TOKEN_EXPIRATION_IN_SECONDS,
            scopes=["signature", "impersonation"]
        )
        return token_response.access_token
    except ApiException as e:
        if "consent_required" in str(e.body):
            consent_url = generate_consent_url()
            raise Exception(f"Consent required. Visit this URL: {consent_url}")
        else:
            raise
        
@app.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    if request.method == 'GET':
        tasks = Tasks.query.all()
        return jsonify([task.to_dict() for task in tasks]), 200
    if request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        assigned_to = request.json.get('assigned_to')
        project_id = request.json.get('project_id')
        task = Tasks(name=name, description=description, assigned_to=assigned_to, project_id=project_id)        
        db.session.add(task)
        db.session.commit()
        return jsonify({"message": "Task created successfully"}), 201
   
@app.route('/projects', methods=['GET', 'POST'])
def get_projects():
    if request.method == 'GET':
        projects = Projects.query.all()
        return jsonify([project.to_dict() for project in projects]), 200
    if request.method == 'POST':
        name = request.json.get('name')
        description = request.json.get('description')
        assigned_to = request.json.get('assigned_to')
        project = Projects(name=name, description=description, assigned_to=assigned_to)
        db.session.add(project)
        db.session.commit()
        return jsonify({"message": "Project created successfully"}), 201
    
@app.route('/project/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Projects.query.get(project_id)
    return jsonify(project.to_dict()), 200       
@app.route('/toggleFavorite/<int:task_id>', methods=['POST'])
def toggle_favorite(task_id):
    project = Projects.query.get(task_id)
    project.favorite = not project.favorite
    db.session.commit()
    return jsonify({"message": "Favorite status toggled successfully"}), 200
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
@app.route('/document/<int:document_id>', methods=['GET'])
def get_document(document_id):
    document = Documents.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found"}), 404
    return jsonify(document.to_dict()), 200

@app.route("/create-envelope", methods=["POST"])
def create_envelope_route():
    return create_envelope()
def authenticate_docusign():
    access_token = get_access_token()
    api_client = ApiClient()
    api_client.set_default_header("Authorization", f"Bearer {access_token}")
    user_info = api_client.get_user_info(access_token)
    account_info = next((acc for acc in user_info.accounts if acc.is_default), None)

    return {
        "access_token": access_token,
        "account_id": account_info.account_id,
        "base_path": account_info.base_uri + "/restapi"
    }

def create_envelope():
    try:
        
        token_info = authenticate_docusign()
        access_token = token_info["access_token"]
        account_id = token_info["account_id"]

        
        api_client = ApiClient()
        api_client.host = token_info["base_path"]
        api_client.set_default_header("Authorization", f"Bearer {access_token}")

        envelopes_api = EnvelopesApi(api_client)

       
        data = request.get_json()
        base64_content = data.get("base64Content")
        filename = data.get("filename", "document.pdf")

        if not base64_content:
            return jsonify({"error": "Missing base64Content"}), 400

       
        document = Document(
            document_base64=base64_content,
            name=filename,
            file_extension="pdf",
            document_id="1",
        )

        signer = Signer(
            email=SIGNER_EMAIL,
            name=SIGNER_NAME,
            recipient_id="1",
            routing_order="1",
            client_user_id=CLIENT_USER_ID
        )

        sign_here = SignHere(
            anchor_string="/sn1/",
            anchor_units="pixels",
            anchor_x_offset="20",
            anchor_y_offset="10",
        )

        tabs = Tabs(sign_here_tabs=[sign_here])
        signer.tabs = tabs

        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign this document",
            documents=[document],
            recipients=Recipients(signers=[signer]),
            status="sent",
        )

       
        envelope_summary = envelopes_api.create_envelope(account_id, envelope_definition=envelope_definition)
        app.logger.debug("Envelope Summary:", envelope_summary)

        
        recipient_view_request = RecipientViewRequest(
            return_url=RETURN_URL,
            authentication_method="email",
            email=SIGNER_EMAIL,
            user_name=SIGNER_NAME,
            client_user_id=CLIENT_USER_ID,
        )

        
        view_url = envelopes_api.create_recipient_view(
    account_id=account_id,
    envelope_id=envelope_summary.envelope_id,
    recipient_view_request=recipient_view_request
)

        print("Recipient View URL:", view_url)

        
        return jsonify({
            "envelope_id": envelope_summary.envelope_id,
            "url": view_url.url  
        })
    
    except ApiException as e:
        print("Error:", e)
        return jsonify({"error": "DocuSign API error", "details": e.body}), e.status
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    contact = data.get('contact')
    password = data.get('password')
    user = User(name=name, email=email, contact=contact, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        return jsonify({"error": "Invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user.email))
    return jsonify({"access_token": access_token}),200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])
@app.route('/api/docusign/view', methods=['POST'])
def create_docusign_view():
    file = request.files.get('file')
    name = request.form.get('name')

    if not file or not name:
        return jsonify({"error": "Missing file or name"}), 400

    file_bytes = file.read()
    file_base64 = base64.b64encode(file_bytes).decode('utf-8')

    
    token_info = authenticate_docusign()
    access_token = token_info["access_token"]
    account_id = token_info["account_id"]
    base_path = token_info["base_path"]

    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header("Authorization", f"Bearer {access_token}")

    envelopes_api = EnvelopesApi(api_client)

    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document",
        documents=[
            Document(
                document_base64=file_base64,
                name=name,
                file_extension="pdf",
                document_id="1"
            )
        ],
        recipients=Recipients(signers=[
            Signer(
                email="signer@example.com", 
                name="John Doe",
                recipient_id="1",
                client_user_id="1234",
                tabs=Tabs(sign_here_tabs=[
                    SignHere(anchor_string="/sn1/", anchor_units="pixels", anchor_x_offset="0", anchor_y_offset="0")
                ])
            )
        ]),
        status="sent"
    )

    envelope = envelopes_api.create_envelope(account_id, envelope_definition=envelope_definition)

    view_request = RecipientViewRequest(
        authentication_method="none",
        client_user_id="1234",
        recipient_id="1",
        return_url="http://localhost:4200/docusign-return",
        user_name="John Doe",
        email="signer@example.com"
    )

    try:
        view_url = envelopes_api.create_recipient_view(
            account_id=account_id,
            envelope_id=envelope.envelope_id,  # envelope.envelope_id is correct here
            recipient_view_request=view_request
        )
        return jsonify({"url": view_url.url})
    except ApiException as e:
        return jsonify({"error": "Error creating recipient view", "details": e.body}), e.status

from docusign_esign import RecipientViewRequest


@app.route("/create-sender-view", methods=["POST"])
def create_sender_view():
    try:
        token_info = authenticate_docusign()
        access_token = token_info["access_token"]
        account_id = token_info["account_id"]
        base_path = token_info["base_path"]

        api_client = ApiClient()
        api_client.host = base_path
        api_client.set_default_header("Authorization", f"Bearer {access_token}")
        envelopes_api = EnvelopesApi(api_client)

        
        file = request.files.get('file')
        filename = request.form.get('name') or "document.pdf"
        file_bytes = file.read()
        file_base64 = base64.b64encode(file_bytes).decode('utf-8')

        
        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign this document",
            documents=[Document(
                document_base64=file_base64,
                name=filename,
                file_extension="pdf",
                document_id="1"
            )],
            status="created"
        )

        
        envelope_summary = envelopes_api.create_envelope(account_id, envelope_definition=envelope_definition)
        envelope_id = envelope_summary.envelope_id

        

        
        view_url = envelopes_api.create_sender_view(account_id, envelope_id=envelope_id)

        return jsonify({"url": view_url.url})

    except ApiException as e:
        return jsonify({"error": "DocuSign API error", "details": e.body}), e.status

if __name__ == '__main__':
    app.run(debug=True)
