"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', url_signer, db, auth.user)
def index():
    rows = db(db.product.created_by == get_user_email()).select()
    return dict(rows=rows, url_signer=url_signer)

@action('add', method=["GET", "POST"])
@action.uses('add.html', url_signer, db, session, auth.user)
def add():
    # Insert form: no record= in it.
    form = Form(db.product, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # We simply redirect; the insertion already happened.
        redirect(URL('index'))
    # Either this is a GET request, or this is a POST but not accepted = with errors.
    return dict(form=form)

# This endpoint will be used for URLs of the form /edit/k where k is the product id.
@action('edit/<product_id:int>', method=["GET", "POST"])
@action.uses('edit.html', url_signer.verify(), db, session, auth.user)
def edit(product_id=None):
    assert product_id is not None
    # We read the product being edited from the db.
    # p = db(db.product.id == product_id).select().first()
    p = db.product[product_id]
    if p is None:
        # Nothing found to be edited!
        redirect(URL('index'))
    # Edit form: it has record=
    form = Form(db.product, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # The update already happened!
        redirect(URL('index'))
    return dict(form=form)

@action('delete/<product_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete(product_id=None):
    assert product_id is not None
    db(db.product.id == product_id).delete()
    redirect(URL('index'))