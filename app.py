import os
from flask import Flask,request,url_for,render_template,send_from_directory,redirect,flash,Markup,session
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' #disable TF warnings
from Object_detection_image import *
from flask_uploads import IMAGES,UploadSet, configure_uploads,patch_request_class
from flaskext.mysql import MySQL
from flask_mysqldb import MySQL,MySQLdb
import bcrypt

# from inventorymanagement.forms import RegistrationForm, LoginForm, AddProduct, AddLocation, ProductMovement


app = Flask(__name__)
api = Api(app)
cnt=0
detected=[1,]
visitors=0
customer_name=''
product_cnt=0
sales=0
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'amaclone'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
print("Connection done")

# Uploads settings
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/current_cart'
# app.config['UPLOADED_PROFILE_DEST'] = os.getcwd() + '/static/users'
photos = UploadSet('photos', ('png', 'jpg'))
# media = UploadSet('media', default_dest=lambda app: app.instance_path)
configure_uploads(app,photos)
patch_request_class(app)  # set maximum file size, default is 16MB

@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def home():
	global sales,visitors
	# conn = mysql.connect()
	# cursor = conn.cursor()
	cursor = mysql.connection.cursor()
    # cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
    # mysql.connection.commit()
	cursor.execute("SELECT * FROM products")
	import itertools
	desc = cursor.description
	column_names = [col[0] for col in desc]
	data = [dict(zip(column_names, row))  
        for row in cursor.fetchall()]
	return render_template('home.html',
		products=data)

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            # if bcrypt.hashpw(password, user["password"].encode('utf-8')) == user["password"].encode('utf-8'):
            print(password, user["password"])
            if password == user["password"]:
                session['name'] = user['name']
                session['email'] = user['email']
                session['profile_pic'] = user['profile_pic']
                return render_template("home.html")
            else:
                return "Error password and email not match"
        else:
            return "Error user not found"
    else:
        return render_template("login.html")

@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=["GET", "POST"])
def Register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        # hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,password,))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('home'))

@app.route('/reports')
def Reports():
	global sales,visitors
	# conn = mysql.connect()
	# cursor = conn.cursor()
	cursor = mysql.connection.cursor()
    # cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
    # mysql.connection.commit()
	cursor.execute("SELECT COUNT(DISTINCT(transaction_email)) FROM transactions")
	products = cursor.fetchone()
	cursor.execute("SELECT COUNT(transaction_id) FROM transactions")
	sales = cursor.fetchone()
	# sales = str(sales)
	# sales = sales[:-1]
	print(sales, products)
	return render_template('reports.html',
		sales=sales[0],
		products=products[0])

@app.route('/inventory', methods=["GET", "POST"])
def Inventory():
	if request.method == 'GET':
		global sales,visitors
		# conn = mysql.connect()
		# cursor = conn.cursor()
		cursor = mysql.connection.cursor()
	    # cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",(name,email,hash_password,))
	    # mysql.connection.commit()
		cursor.execute("SELECT * FROM products")
		products = cursor.fetchall()
		# sales = str(sales)
		# sales = sales[:-1]
		# print(products)
		return render_template('inventory.html',
			products=products)
	else:
		product_id = request.form['product_id']
		product_cat = request.form['product_cat']
		product_brand = request.form['product_brand']
		product_title = request.form['product_title']
		product_price = request.form['product_price']
		product_stock = request.form['product_stock']
		print(product_id,product_cat,product_title,product_price,product_stock)
		curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		print('Inventory update Started')
		curl.execute("UPDATE products SET product_price=%s, stock=%s WHERE product_id=%s and product_title=%s",(product_price,product_stock,product_id,product_title,))
		mysql.connection.commit()
		print('Inventory update finished')
		return redirect(url_for('Inventory'))

@app.route('/transactions')
def Transactions():
	cursor = mysql.connection.cursor()
	cursor.execute("SELECT * FROM transactions")
	import itertools
	desc = cursor.description
	column_names = [col[0] for col in desc]
	transactions = [dict(zip(column_names, row))  
        for row in cursor.fetchall()]
	return render_template('transactions.html',
	transactions=transactions)

@app.route('/profile', methods=["GET", "POST"])
def profile():
    if request.method == 'GET':
        return render_template("profile.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        profile = curl.fetchone()
        curl.close()

        if len(profile) > 0:
        	curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        	curl.execute("UPDATE users SET name=%s, password=%s WHERE email=%s",(name,password,email,))
        	mysql.connection.commit()
        	curl.close()
        	CWD_PATH = os.getcwd()
        	profile_dir = os.path.join(CWD_PATH,"static/users")
        	file_obj = request.files['file']
        	import datetime
        	# customer_name=request.form['customer_name']
        	if file_obj.filename is not '':
        		suffix=datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        		rname="_".join([suffix,file_obj.filename])
        		filename = photos.save(file_obj,folder=profile_dir,name=str(rname))
        		curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	        	curl.execute("UPDATE users SET profile_pic=%s WHERE password=%s and email=%s",(rname,password,email,))
	        	mysql.connection.commit()
	        	curl.close()
	        	curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
		        user = curl.fetchone()
		        curl.close()
		        session['name'] = user['name']
		        session['email'] = user['email']
		        session['profile_pic'] = user['profile_pic']
		        print("Profile Picture Updated!")
        	else:
        		flash('Select/upload atleast 1 product image to continue.')
        		return render_template('profile.html')
        	print("Updated successfully")
        	flash("Profile Updated successfully")
        	return render_template('profile.html')


@app.route('/about')
def about():
    return render_template('about.html', title="About")


# background process happening without any refreshing
@app.route('/camscan')
def CamScan():
	global product_cnt
	from os import listdir
	CWD_PATH = os.getcwd()
	img_dir_path=os.path.join(CWD_PATH,"current_cart")

	#empty the contents in the last bill
	open('product_list.csv', 'w').close()

	image_list=listdir(img_dir_path)
	not_detected=[]
	for image in image_list:
		global cnt,detected
		if cnt==0:
			PATH_TO_IMAGE=os.path.join(img_dir_path,image)

			detected=load_tensorflow_to_memory(PATH_TO_IMAGE)
			cnt+=1
			if detected[0] != 1:
				detected[0]=image
				not_detected.append(image)
			else:
				product_cnt+=detected[1]

		else:
			PATH_TO_IMAGE=os.path.join(img_dir_path,image)
			detected=perform_product_detection(PATH_TO_IMAGE)
			if detected[0]!=1:
				detected[0]=image
				not_detected.append(image)
			else:
				product_cnt+=detected[1]

	if len(not_detected)!=0:
		not_detected_products=''
		for product in not_detected:
			not_detected_products+=str(product)+","

		flash("Could not detect image: "
		  +not_detected_products
		  +Markup(r"<a href='/show-bill'> click here</a>")
		  +" to generate bill without it or generate new bill with new images")
		return redirect('/generate-bill-page')

	return redirect('/show-bill')

@app.route('/store')
def Store():
    return render_template('mainLayout.html', title="About")

@app.route('/show-bill', methods=['GET','POST'])
def ShowBill():
	global customer_email, invoice_id,cart, final_cost
	import csv
	from datetime import datetime
	import random
	items_freq={}
	redundant_list=[]
	global visitors
	visitors+=1
	with open("product_list.csv",'r') as cart:
		csv_reader=csv.reader(cart)
		for line in csv_reader:
			redundant_list.append(int(line[0]))

	set_list=list(set(redundant_list))

	for i in range(len(set_list)):
		items_freq[set_list[i]]=redundant_list.count(set_list[i])

	print("set_list:",set_list)
	print(items_freq)
	print("red_list:",redundant_list)
	cart={}
	total_price=0
	for key,value in items_freq.items():
		tempy=product_details[key]
		tempy['qty']=value
		total_price+=tempy['price']*value
		cart[key]=tempy

	costs={}
	gst_amt=(total_price*5)/100

	costs['gst_amt']=gst_amt
	costs['cost_wo_gst']=total_price
	costs['cost_w_gst']=total_price+gst_amt
	final_cost= costs['cost_w_gst']

	# session['email'] = request.form['email']
	invoice_id=random.randint(10000, 99999)
	timestamp=datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
	# print(cart.values())

	if request.method == 'POST':
		print('Transaction Started')
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO transactions (transaction_id ,customer_name, transaction_email, contact_no , product_list , transaction_amount) VALUES (%s,%s,%s,%s,%s,%s)",(invoice_id,customer_name,customer_email,contact_no,cart,costs['cost_w_gst'],))
		mysql.connection.commit()
		print('Transaction Completed')
		return redirect('/')
	
	return render_template('showBillPage.html',
		cart=cart,
		costs=costs,
		timestamp=timestamp,
		invoice_id=invoice_id,
		customer_name=customer_name,
		customer_email=customer_email,
		contact_no=contact_no)


@app.route('/generate-bill-page', methods=['GET','POST'])
def BillingPage():
	if request.method == 'POST':

		#empty current_cart folder
		import glob
		files = glob.glob(os.getcwd() + '/current_cart/*')
		for f in files:
			os.remove(f)
		#empty current_cart folder
		# session['customer_name'] = request.form['customer_name']
		# session['customer_email'] = request.form['customer_email']
		# session['contact_no'] = request.form['contact_no']
		file_obj = request.files.getlist('file[]')
		global customer_name, customer_email, contact_no
		customer_name=request.form['customer_name']
		customer_email=request.form['customer_email']
		contact_no=request.form['contact_no']
		for f in file_obj:
			# file = request.files.get(f)
			file = f
			if file.filename is not '':
				filename = photos.save(file,name=file.filename)
			else:
				flash('Select/upload atleast 1 product image to continue.')
				return render_template('billingPage.html')
		return redirect('camscan')
	else:
		return render_template('billingPage.html')


@app.route('/update-sales')
def UpdateSales():
	global product_cnt,sales
	sales=product_cnt
	return redirect('/')



if __name__ == '__main__':
	app.secret_key = "^A%DJAJU^JJ123"
	app.config['SESSION_TYPE'] = 'filesystem'
	app.run(port=5002,debug=True,host='0.0.0.0')
