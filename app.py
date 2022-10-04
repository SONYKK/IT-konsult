from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///product.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    product_description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(100), default='По запросу')
    product_category = db.Column(db.String(150))

    def __repr__(self):
        return '<Product %r>' % self.id


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


@app.route('/store')
def store():
    products = Product.query.order_by(Product.product_category).all()
    return render_template('store.html', products=products)


@app.route('/store/<int:id>')
def store_detail(id):
    product = Product.query.get(id)
    return render_template('store_detail.html', product=product)


@app.route('/store/<int:id>/delete')
def store_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect('/store')


@app.route('/create_product', methods=['POST', 'GET'])
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
        return redirect('/')
#        except:
#            return 'При добавлении товара произошла ошибка'

    else:
        return render_template('create_product.html')


@app.route('/store/<int:id>/update', methods=['POST', 'GET'])
def store_update(id):
    product = Product.query.get(id)
    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.product_description = request.form['product_description']
        product.price = request.form['price']
        product.product_category = request.form['product_category']
        db.session.commit()
        return redirect('/store')
    else:

        return render_template('store_update.html', product=product)

if __name__ == '__main__':
    app.run(debug=False)
