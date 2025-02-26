from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from flask_cors import CORS
import os  # 导入 os 模块
import time
import requests

import http.server
import socketserver
import ssl

app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@127.0.0.1:3306/test3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'images'  # 图片存储文件夹
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

CERT_FOLDER = '/tmp/ca/'
CERT_FILE = 'exmaple.crt'
KEY_FILE = 'example.key'

# Define the Information model (table)
class Information(db.Model):
    __tablename__ = 'Information'  
    id = db.Column(db.Integer, primary_key=True)
    companyName = db.Column(db.String(255), nullable=False)
    companyPhone = db.Column(db.String(20))
    companyFax = db.Column(db.String(20))
    companyAddress = db.Column(db.String(255))
    companyEmail = db.Column(db.String(120))
    companyUnifiedNumber = db.Column(db.String(120))

    def __repr__(self):
        return '<Information %r>' % self.companyName

# Define the ContactUs model (table)
class ContactUs(db.Model):
    __tablename__ = 'ContactUs'  
    id = db.Column(db.Integer,primary_key=True)
    contactUsMessage = db.Column(db.String(1000), nullable=False)

    def __repr__(self):
        return '<ContactUs %r>' % self.id

# Define the News model (table)
class News(db.Model):
    __tablename__ = 'News'  
    id = db.Column(db.Integer, primary_key=True)
    newsText = db.Column(db.String(1000), nullable=False)  # Adjust length as needed
    newsImage = db.Column(db.String(255))  # Adjust length as needed
    newsDate = db.Column(db.String(20))  # Adjust length as needed
    newsDetailText = db.Column(db.String(1000), nullable=False)  # Adjust length as needed

    def __repr__(self):
        return '<News %r>' % self.id

# Define the Product model (table)
class Product(db.Model):
    __tablename__ = 'Product'  
    id = db.Column(db.Integer, primary_key=True)
    productName = db.Column(db.String(255), nullable=False)
    productDesc = db.Column(db.String(255))
    productSort = db.relationship('ProductSort', backref='Product', lazy=True)
    isShow = db.Column(db.Integer, default=0)
    isInProduct = db.Column(db.Integer, default=0)
    isInNewProduct = db.Column(db.Integer, default=0)
    isInHome = db.Column(db.Integer, default=0)
    images = db.relationship('ProductImage', backref='Product', lazy=True)

    def __repr__(self):
        return '<Product %r>' % self.productName

# Define the ProductImage model (table)
class ProductImage(db.Model):
    __tablename__ = 'ProductImage'  
    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)
    imageUrl = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<ProductImage %r>' % self.imageUrl

# Define the ProductImage model (table)
class ProductSort(db.Model):
    __tablename__ = 'ProductSort'  
    id = db.Column(db.Integer, primary_key=True)
    productId = db.Column(db.Integer, db.ForeignKey('Product.id'), nullable=False)
    sortName = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<ProductSort %r>' % self.imageUrl        

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/images/<path:filename>')
def serve_image(filename):
    """提供 images 文件夹中的图片"""
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

# API Endpoint (POST /information)
@app.route('/information', methods=['POST'])
def handle_information():
    action = request.form.get('action')
    print(action)
    if not action:
        return jsonify({'message': 'Invalid data. "action" is required.'}), 400

    action = action.lower()

    if action == 'query':
        return query_information(request.form)
    elif action == 'new':
        return create_information(request.form)
    elif action == 'modify':
        return modify_information(request.form)
    else:
        return jsonify({'message': 'Invalid action. Must be "query", "new", or "modify".'}), 400

# Helper functions

def query_information(form_data):
    # Since there's only one record, we don't need to query by ID
    info = Information.query.first()  # Get the first (and only) record
    if info:
        return jsonify({
            'id': info.id,
            'companyName': info.companyName,
            'companyPhone': info.companyPhone,
            'companyFax': info.companyFax,
            'companyAddress': info.companyAddress,
            'companyEmail': info.companyEmail,
            'companyUnifiedNumber': info.companyUnifiedNumber
        })
    else:
        return jsonify({'message': 'Information not found'}), 404

def create_information(form_data):
    company_name = form_data.get('companyName')
    if not company_name:
        return jsonify({'message': 'Invalid data. "companyName" is required for "new" action.'}), 400
    
    # Check if a record already exists
    existing_info = Information.query.first()
    if existing_info:
        return jsonify({'message': 'Information already exists. Use "modify" to update.'}), 409

    new_info = Information(
        companyName=form_data.get('companyName'),
        companyPhone=form_data.get('companyPhone'),
        companyFax=form_data.get('companyFax'),
        companyAddress=form_data.get('companyAddress'),
        companyEmail=form_data.get('companyEmail'),
        companyUnifiedNumber=form_data.get('companyUnifiedNumber')
    )
    db.session.add(new_info)
    db.session.commit()
    return jsonify({'message': 'Information created', 'id': new_info.id}), 201

def modify_information(form_data):
    # Since there's only one record, we don't need to query by ID
    info = Information.query.first()  # Get the first (and only) record
    if not info:
        return jsonify({'message': 'Information not found'}), 404

    info.companyName = form_data.get('companyName', info.companyName)
    info.companyPhone = form_data.get('companyPhone', info.companyPhone)
    info.companyFax = form_data.get('companyFax', info.companyFax)
    info.companyAddress = form_data.get('companyAddress', info.companyAddress)
    info.companyEmail = form_data.get('companyEmail', info.companyEmail)
    info.companyUnifiedNumber=form_data.get('companyUnifiedNumber')

    db.session.commit()
    return jsonify({'message': 'Information updated'})


# API Endpoint (POST /contactUs)
@app.route('/contactUs', methods=['POST'])
def handle_contactUs():

    action = request.form.get('action')
    if not action:
        return jsonify({'message': 'Invalid data. "action" is required.'}), 400

    action = action.lower()

    if action == 'query':
        return query_contactUs(request.form)
    elif action == 'modify':
        return modify_contactUs(request.form)
    else:
        return jsonify({'message': 'Invalid action. Must be "query"or "modify".'}), 400

# Helper functions

def query_contactUs(form_data):
    

    contactUs = ContactUs.query.first()  # Get the first (and only) record
    if contactUs:
        return jsonify({
            'id': contactUs.id,
            'contactUsMessage': contactUs.contactUsMessage,
        })
    else:
        return jsonify({'message': 'contactUs not found'}), 404
    
    return jsonify(result)

def modify_contactUs(form_data):
    contact_id = form_data.get('id')
    if not contact_id:
        return jsonify({'message': 'Invalid data. "id" is required for "modify" action.'}), 400

    contact = ContactUs.query.get(contact_id)
    if not contact:
        return jsonify({'message': 'ContactUs not found'}), 404

    contact.contactUsMessage = form_data.get('contactUsMessage', contact.contactUsMessage)

    db.session.commit()
    return jsonify({'message': 'ContactUs updated'})

@app.route('/news', methods=['POST'])
def handle_news():
    action = request.form.get('action')
    if not action:
        return jsonify({'message': 'Invalid data. "action" is required.'}), 400

    action = action.lower()

    if action == 'query':
        return query_news()
    elif action == 'new':
        return create_news(request.form)
    elif action == 'modify':
        return modify_news(request.form)
    else:
        return jsonify({'message': 'Invalid action. Must be "query", "new", or "modify".'}), 400

# Helper function to query all news
def query_news():
    all_news = News.query.all()
    news_list = []
    for news in all_news:
        news_list.append({
            'id': news.id,
            'newsText': news.newsText,
            'newsImage': news.newsImage,
            'newsDate': news.newsDate,
            'newsDetailText':news.newsDetailText
        })
    return jsonify(news_list)

# Helper function to create new news
def create_news(form_data):
    news_text = form_data.get('newsText')
    if not news_text:
        return jsonify({'message': 'Invalid data. "newsText" is required for "new" action.'}), 400

    new_news = News(
        newsText=news_text,
        newsImage=form_data.get('newsImage'),
        newsDate=form_data.get('newsDate'),
        newsDetailText=form_data.get('newsDetailText')
    )
    db.session.add(new_news)
    db.session.commit()

    return jsonify({'message': 'News created successfully'}), 201

# Helper function to modify news
def modify_news(form_data):
    news_id = form_data.get('id')
    if not news_id:
        return jsonify({'message': 'Invalid data. "id" is required for "modify" action.'}), 400

    existing_news = News.query.get(news_id)
    if not existing_news:
        return jsonify({'message': 'News not found.'}), 404

    existing_news.newsText = form_data.get('newsText', existing_news.newsText)
    existing_news.newsImage = form_data.get('newsImage', existing_news.newsImage)
    existing_news.newsDate = form_data.get('newsDate', existing_news.newsDate)
    existing_news.newsDetailText = form_data.get('newsDetailText', existing_news.newsDetailText)

    db.session.commit()

    return jsonify({'message': 'News modified successfully'}), 200    

@app.route('/products', methods=['POST'])
def handle_products():
    action = request.form.get('action')
    if not action:
        return jsonify({'message': 'Invalid data. "action" is required.'}), 400

    action = action.lower()

    if action == 'query':
        return query_products()
    elif action == 'new':
        return create_product()
    elif action == 'new_image':
        return create_product_image(request.form)  
    elif action == 'modify_image':
        return modify_product_image(request.form) 
    elif action == 'delete_image':
        return delete_product_image(request.form)            
    elif action == 'modify':
        return modify_product(request.form)
    elif action == 'delete':
        return delete_product(request.form)    
    else:
        return jsonify({'message': 'Invalid action. Must be "query", "new", or "modify".'}), 400

# Helper function to query all products with images
def query_products():
    all_products = Product.query.all()
    product_list = []
    for product in all_products:
        product_data = {
            'id': product.id,
            'productName': product.productName,
            'productDesc': product.productDesc,
            'productSort': [{'id': sort.id, 'sortName': sort.sortName} for sort in product.productSort],
            'isShow': product.isShow,
            'isInHome': product.isInHome,
            'isInProduct': product.isInProduct,
            'isInNewProduct': product.isInNewProduct,
            'images': [{'id':image.id,'imageUrl': image.imageUrl} for image in product.images]
        }
        product_list.append(product_data)
    return jsonify(product_list)

# Helper function to create a new product
def create_product():

    new_product = Product(
        productName= "測試",
        productDesc= "測試",
        isShow= 1,  # Default to True if not provided
        isInProduct= 1,  # Default to True if not provided
        isInNewProduct= 1,  # Default to True if not provided
        isInHome=1  # Default to True if not provided
    )
    db.session.add(new_product)
    db.session.commit()

    default_sort = "全部"
    new_sort = ProductSort(productId=new_product.id, sortName=default_sort)
    db.session.add(new_sort)
    db.session.commit()

    default_image_url = "https://editor.leonh.space/2021/rediscover-pixel-dpi-ppi-and-pixel-density/Ax1000.png"
    new_image = ProductImage(productId=new_product.id, imageUrl=default_image_url)
    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Product created successfully', 'id': new_product.id}), 201

# Helper function to create a new product
def create_product_image(form_data):

    product_id = form_data.get('id')
    default_image_url = "https://editor.leonh.space/2021/rediscover-pixel-dpi-ppi-and-pixel-density/Ax1000.png"
    new_image = ProductImage(productId=product_id, imageUrl=default_image_url)
    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Product created successfully', 'id': product_id}), 201    

# Helper function to modify an existing product
def modify_product(form_data):
    product_id = form_data.get('id')
    if not product_id:
        return jsonify({'message': 'Invalid data. "id" is required for "modify" action.'}), 400

    existing_product = Product.query.get(product_id)
    if not existing_product:
        return jsonify({'message': 'Product not found.'}), 404

    existing_product.productName = form_data.get('productName', existing_product.productName)
    existing_product.productDesc = form_data.get('productDesc', existing_product.productDesc)
    existing_product.productSort = form_data.get('productSort', existing_product.productSort)
    existing_product.isShow = form_data.get('isShow', existing_product.isShow)
    existing_product.isInHome = form_data.get('isInHome', existing_product.isInHome)
    existing_product.isInProduct = form_data.get('isInProduct', existing_product.isInProduct)
    existing_product.isInNewProduct = form_data.get('isInNewProduct', existing_product.isInNewProduct)

    # Handle images
    sort_list = form_data.getlist('sortList')  # Get a list of image URLs
    # Delete existing images
    for sort in existing_product.productSort:
        db.session.delete(sort)

    # Add new images
    for sortName in sort_list:
        new_sort = ProductSort(productId=existing_product.id, sortName=sortName)
        db.session.add(new_sort)

    # Handle images
    image_urls = form_data.getlist('imageUrls')  # Get a list of image URLs
    # Delete existing images
    for image in existing_product.images:
        db.session.delete(image)
    # Add new images
    for image_url in image_urls:
        new_image = ProductImage(productId=existing_product.id, imageUrl=image_url)
        db.session.add(new_image)

    db.session.commit()

    return jsonify({'message': 'Product modified successfully'}), 200

# Helper function to modify an existing product
def modify_product_image(form_data):
    product_id = form_data.get('id')
    if not product_id:
        return jsonify({'message': 'Invalid data. "id" is required for "modify" action.'}), 400

    existing_product = ProductImage.query.get(product_id)
    if not existing_product:
        return jsonify({'message': 'Product not found.'}), 404

    existing_product.imageUrl = form_data.get('imageUrl', existing_product.imageUrl)

    db.session.commit()

    return jsonify({'message': 'Product modified successfully'}), 200

def delete_product(form_data):
    product_id = form_data.get('id')
    if not product_id:
        return jsonify({'message': 'Invalid data. "id" is required for "delete" action.'}), 400

    try:
        product_id = int(product_id)  # 确保 product_id 是整数
    except ValueError:
        return jsonify({'message': 'Invalid data. "id" must be an integer.'}), 400

    existing_product = Product.query.get(product_id)
    if not existing_product:
        return jsonify({'message': 'Product not found.'}), 404

    # 删除关联数据（例如，产品图片、产品分类等）
    for image in existing_product.images:
        db.session.delete(image)
    for sort in existing_product.productSort:
        db.session.delete(sort)

    # 删除产品
    db.session.delete(existing_product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200

def delete_product_image(form_data):
    product_id = form_data.get('id')
    if not product_id:
        return jsonify({'message': 'Invalid data. "id" is required for "delete" action.'}), 400

    try:
        product_id = int(product_id)  # 确保 product_id 是整数
    except ValueError:
        return jsonify({'message': 'Invalid data. "id" must be an integer.'}), 400

    existing_product = ProductImage.query.get(product_id)
    if not existing_product:
        return jsonify({'message': 'Product not found.'}), 404

    # 删除产品
    db.session.delete(existing_product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200


@app.route('/upload', methods=['POST'])
def upload_file():
    print('bbbb')
    print('aaaa'+str(request.files))
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # 获取当前时间戳作为文件名
        timestamp = int(time.time())
        filename = f'{timestamp}.png'

        # 保存文件到 images 文件夹
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 获取当前 IP 地址（需要安装 `requests` 库）
        try:
            # ip_address = requests.get('https://api.ipify.org').text
            ip_address = '10.42.16.50'
        except requests.exceptions.RequestException:
            ip_address = 'unknown'  # 如果获取 IP 失败，则使用 'unknown'

        # 构建绝对路径
        absolute_path = f'https://{ip_address}:8000/{UPLOAD_FOLDER}/{filename}'  # 假设 Flask 应用运行在端口 5000

        return jsonify({'absolute_path': absolute_path}), 200

if __name__ == '__main__':
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 创建 images 文件夹（如果不存在）

    # Create an SSL context using the CA-issued certificate
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(os.path.join(CERT_FOLDER, CERT_FILE), os.path.join(CERT_FOLDER, KEY_FILE))

    app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=context)