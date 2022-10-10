from unicodedata import name
from flask import Flask, render_template, request,  flash, abort, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, UserMixin, logout_user, LoginManager
from forms import LoginForm, RegisterForm
from admin.admin import admin, menu
from datetime import datetime


SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)


app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"
login_manager.init_app(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(100), default='По запросу')
    product_category = db.Column(db.String(150))

    def __repr__(self):
        return f'<Product {self.id}>'


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    pr = db.relationship('Profiles', backref='users', uselist=False)

    def __repr__(self):
        return f"<users {self.id}>"


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(100), nullable=False)   

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return Users.query.get(int(user_id))


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/delivery')
def delivery():
    return render_template('delivery.html')    


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/sale')
def sale():
    return render_template('sale.html')


@app.route('/listusers')
def listusers_admin():
    profiles = db.session.query(Profiles).all()
    list_users = []
    for i in range(len(profiles)):
        email = Users.query.order_by(Users.id).all()[i].email 
        name = Profiles.query.order_by(Profiles.id).all()[i].name
        date = Users.query.order_by(Users.id).all()[i].date
        city = Profiles.query.order_by(Profiles.id).all()[i].city
        list_users.append([name, email, date, city])
    return render_template('/listusers.html', profiles=profiles, list_users=list_users)


@app.route('/listgoods')
def listgoods_admin():
    products = db.session.query(Product).all()
    for i in range(len(products)):
        product_name = Product.query.order_by(Product.id).all()[i].product_name 
        product_description = Product.query.order_by(Product.id).all()[i].product_description
        price = Product.query.order_by(Product.id).all()[i].price
        product_category = Product.query.order_by(Product.id).all()[i].product_category
    return render_template('/listgoods.html', product_name=product_name, 
    product_category=product_category, price=price, product_description=product_description, products=products)


@app.route('/store')
def store():
    products = Product.query.order_by(Product.product_category).all()
    return render_template('/store.html', products=products)


@app.route('/admin/store')
def store_admin():
    products = Product.query.order_by(Product.id).all()
    return render_template('/admin/store.html', products=products)


@app.route('/.store/<int:id>')
def store_detail_admin(id):
    product = Product.query.get(id)
    return render_template('/admin/store_detail.html', product=product)


@app.route('/store/<int:id>')
def store_detail(id):
    product = Product.query.get(id)
    return render_template('store_detail.html', product=product)


@app.route('/.store/<int:id>/delete')
def store_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect('/admin/store')


@app.route('/admin/create_product', methods=['POST', 'GET'])
def create_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        price = request.form['price']
        product_category = request.form['product_category']
        product = Product(product_name=product_name, product_description=product_description, price=price,
                          product_category=product_category)
#        try:
        db.session.add(product)
        db.session.commit()
        return redirect('/admin/')
#        except:
#            return 'При добавлении товара произошла ошибка'

    else:
        return render_template('/admin/create_product.html')


@app.route('/.store/<int:id>/update', methods=['POST', 'GET'])
def store_update(id):
    product = Product.query.get(id)
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.product_description = request.form['product_description']
        product.price = request.form['price']
        product.product_category = request.form['product_category']
        db.session.commit()
        return redirect('/admin/store')
    else:

        return render_template('/admin/store_update.html', product=product)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page404.html', title='Страница не найдена')


@app.route('/profile/<username>')
def profile_err(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=request.form.get('email')).first()
        password = request.form.get('psw')
        remember = True if request.form.get('remember') else False
        if not user or not check_password_hash(user.psw, password):
            flash('Неверная пара логин/пароль')
        login_user(user,remember=remember)
    return render_template("login.html", form=form)



@app.route("/register", methods=("POST", "GET"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        
        try:
            hash = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], user_id = u.id)
            db.session.add(p)
            db.session.commit()
            return redirect(url_for('login'))
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

            return redirect(url_for('index'))

    return render_template("register.html", form=form)


if __name__ == '__main__':
    app.run(debug=True)



