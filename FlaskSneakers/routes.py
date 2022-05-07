from fileinput import filename
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from FlaskSneakers import app, db, bcrypt
from FlaskSneakers.forms import RegistrationForm, LoginForm, UpdateAccountForm
from FlaskSneakers.models import User, Item, Market
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/index", methods=['get', 'post', 'GET', 'POST'])
def index():
    items = db.session.query(Item).all()
    if request.method == 'POST':
        if current_user.is_authenticated:
            id = tuple(request.form.keys())[0]
            if len(db.session.query(Market).filter(Market.username.like(current_user.username)).all()) == 0:
                db.session.add(Market(username=current_user.username, cart_items=id, item_image=f'img/market-lots/lot{id}.png')) 
                db.session.commit()
            else:
                cart = db.session.query(Market).filter(Market.username.like(current_user.username)).first()
                cart.cart_items = cart.cart_items + ',' + id
                db.session.commit()
        else:
            return redirect(url_for('login'))

    return render_template('index.html', items=items)


@app.route("/cart", methods=['get', 'post', 'GET', 'POST'])
def cart():
    if current_user.is_authenticated:
        if request.method == 'POST':
            id = tuple(request.form.keys())[0]
            if id in '1234567890':
                item = db.session.query(Market).filter(Market.username.like(current_user.username)).first()
                new_item = item.cart_items.split(',')
                new_item.remove(id)
                item.cart_items = ','.join(new_item)
                db.session.commit()
            if id == 'offer':
                db.session.query(Market).filter(Market.username.like(current_user.username)).delete(synchronize_session=False)
                db.session.commit()
                return render_template('cart.html', flag=True)
        items = db.session.query(Market).filter(Market.username.like(current_user.username)).first()
        if items:
            ids = items.cart_items.split(',')
            if ids[0] == '': ids = ids[1::]
            items = db.session.query(Item).filter(Item.id.in_(ids)).all()
            temp = list(set(ids))
            count_cart_items = []
            for itm in sorted(temp):
                count_cart_items.append(ids.count(itm))
        return render_template('cart.html', flag=False, items=items, count_cart_items=count_cart_items)
    else:
        return redirect(url_for('login'))


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/img/header-items/')
    if os.path.exists(image_path + current_user.image_file):
        os.remove(image_path + current_user.image_file)

    img = Image.open(form_image)
    img.save(image_path + image_fn)

    return image_fn


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_image(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect('/profile')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    # image_file = url_for('static', filename='img/header-items/' + current_user.image_file)

    return render_template('profile.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/api', methods=['GET'])
def get_lots():
    response = {}
    for item in db.session.query(Item).all():
        response[item.id] = [{'item-description': item.title,
                              'item-cost': item.cost}]
    return jsonify({'response': response})
