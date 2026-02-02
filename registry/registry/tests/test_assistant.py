"""Tests for assistant endpoint."""

import os
import json
import sys
from datetime import datetime, timedelta
from hashlib import sha256

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, 'arxiv-auth'))
sys.path.append(os.path.join(ROOT, 'arxiv-auth', 'arxiv_auth'))

from arxiv import status  # type: ignore
from arxiv_auth.helpers import generate_token  # type: ignore

from registry.factory import create_web_app
from registry.services import datastore
from registry.domain import Client, ClientGrantType, ClientCredential, \
    ClientAuthorization, Scope


def setup_app():
    client = Client(
        owner_id='252',
        name='fooclient',
        url='http://asdf.com',
        description='a client',
        redirect_uri='https://foo.com/bar'
    )
    secret = 'foohashedsecret'
    os.environ['JWT_SECRET'] = secret
    hashed_secret = sha256(secret.encode('utf-8')).hexdigest()
    cred = ClientCredential(client_secret=hashed_secret)
    auths = [
        ClientAuthorization(
            scope='something:read',
            requested=datetime.now() - timedelta(seconds=30),
            authorized=datetime.now()
        )
    ]
    grant_types = [
        ClientGrantType(
            grant_type='client_credentials',
            requested=datetime.now() - timedelta(seconds=30),
            authorized=datetime.now()
        )
    ]
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = 'true'
    app = create_web_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite://'
    app.config['SERVER_NAME'] = 'local.host:5000'
    app.config['JWT_SECRET'] = secret
    app.config['REDIS_FAKE'] = True
    test_client = app.test_client()
    with app.app_context():
        datastore.create_all()
        client_id = datastore.save_client(
            client,
            cred,
            auths=auths,
            grant_types=grant_types
        )
    return app, test_client, client_id, secret


def test_assistant_endpoint_requires_auth():
    _, test_client, _, _ = setup_app()
    response = test_client.post('/assistant', json={'message': 'hi'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_assistant_endpoint_reply():
    app, user_agent, _, _ = setup_app()
    token = generate_token('1234', 'foo@bar.com', 'foouser')
    headers = {'Authorization': token}
    response = user_agent.post('/assistant', json={'message': 'hello'}, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.data)
    assert data['reply'] == 'AI assistant reply: hello'
