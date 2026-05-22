from flask import Flask,render_template,redirect,url_for,request
from flask import session
from collections import *

from pymongo import MongoClient 

app=Flask("__main__")
app.secret_key="aarthi"

def MongoDB():
    client = MongoClient("mongodb+srv://deepasriselladurai25:Library-Management-System-Password@library-management-syst.m38td.mongodb.net/")
    db = client.get_database('Library-Management-System-Database')
    collections = {
        'books': db.Books,
        'register': db.Register
    }
    return collections

collections=MongoDB()
register_collections=collections['register']
books_collections=collections['books']


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    query = request.args.get('query')
    result = books_collections.find_one({"title": {"$regex": query, "$options": "i"}})
    return render_template('search_results.html', book=result)

@app.route("/books.html", methods=['POST','GET'])
def books():
    books_collection = collections['books']
    documents = books_collection.find()
    books_data = []

    for document in documents:
        
        books_data.append({
                'book_id': document['book_id'],
                'title': document['title'],
                'author': document['author'],
                'release_date': document['release_date'],
                'image': document['image']
            })
  
    return render_template('books.html', books=books_data)

@app.route("/book.html", methods=['POST','GET'])
def book():
    books_collection = collections['books']
    documents = books_collection.find()
    books_data = []

    for document in documents:
        
        books_data.append({
                'book_id': document['book_id'],
                'title': document['title'],
                'author': document['author'],
                'release_date': document['release_date'],
                'image': document['image']
            })
  
    return render_template('book.html', books=books_data)


@app.route("/book_list.html", methods=['POST','GET'])
def book_list():
    books_collection = collections['books']
    documents = books_collection.find()
    books_data = []

    for document in documents:
        
        books_data.append({
                'book_id': document['book_id'],
                'title': document['title'],
                'author': document['author'],
                'release_date': document['release_date']
            })
  
    return render_template('book_list.html', books=books_data)

@app.route('/view_book/<title>')
def view_book(title):
    result = books_collections.find_one({"title": title})
    return render_template('search_results.html', book=result)


@app.route("/members.html")
def members():
    members_collection = collections['register']
    documents = members_collection.find() 
    members_data = []

    # Iterate over all documents in the collection to extract member data
    for document in documents:
        members_data.append({
            'id': document.get('id'),
            'name': document.get('name'),
            'email': document.get('email'),
            'expiry_date': document.get('expiry_date')
        })
    return render_template('members.html', members_data=members_data)
'''
@app.route("/login_form",methods=["GET","POST"])
def login_form():
    return render_template("login.html")

@app.route("/login",methods=["GET","POST"])
def login():
    form_email=request.form.get('email')
    user=register_collections.find_one({'email':form_email})
    if user:
        session["email"]=form_email
        return redirect("/logged_in")
    else:
        return render_template("/login_form")

@app.route("/logged_in")
def logged_in():
    email=session["email"]
    user=register_collections.find_one({"email":email})
    return render_template("profile.html",member=user)
'''
@app.route("/profile.html/<int:member_id>", methods=["GET", "POST"])
def profile(member_id):
    current_user = register_collections.find_one({'id': member_id})
    return render_template("profile.html", member=current_user)

@app.route("/extend_membership_form/<int:member_id>",methods=["GET","POST"])
def extend_membership_form(member_id):
    user=register_collections.find_one({"id":member_id})
    return render_template("extend_membership.html",user=user)

@app.route("/extend_membership", methods=["GET", "POST"])
def extend_membership():
    if request.method == "POST":
        username = request.form['username']
        membership_type = request.form['membership_type']

        # Determine expiry_date and payment amount based on membership type
        if membership_type == "annual":
            expiry_date = "31-12-2026"
            payment = 1000
        elif membership_type == "half-year":
            expiry_date = "31-06-2026"
            payment = 500
        elif membership_type == "quarter":
            expiry_date = "31-03-2026"
            payment = 250
        else:
            expiry_date = None
            payment = 0

        # Update the expiry_date and payment for the user in the register collection
        register_collections.update_one(
            {'name': username},
            {'$set': {'expiry_date': expiry_date, 'membership_type': membership_type, 'payment': payment}}
        )

        return redirect("/")

    member_id = request.args.get('member_id')
    current_user = register_collections.find_one({'id': member_id})

    return render_template("profile.html", member=current_user)

@app.route("/addmember",methods=['POST'])
def addmember():
    register_collection=collections['register']
    name=request.form['name']
    email=request.form['email']
    exp="2025-12-31"
    new_id = register_collection.count_documents({}) + 1
    register_collection.insert_one({'name': name, 'email': email, 'expiry_date':exp, 'id':new_id})
    return redirect(url_for('members'))

@app.route('/remove/<int:member_id>')
def remove_member(member_id):
    members_collection = collections['register']
    members_collection.delete_one({'id': member_id})
    return redirect(url_for('members'))

@app.route("/login.html")
def log():
    return render_template("login.html")

@app.route("/login", methods=["GET","POST"])
def login():
    email = request.args.get("email")
    # Find the document with the matching ID
    member_document = register_collections.find_one({'email':email})
    if member_document:
        session["email"]=email
        return render_template("profile.html",member=member_document)
    return  render_template("login.html")

@app.route("/reserve_book/<book_title>", methods=["GET", "POST"])
def reserve_book(book_title):
    try:
        email = session["email"]
    except KeyError:
        return render_template("login.html")
    
    user = register_collections.find_one({"email": email})
    book = books_collections.find_one({"title": book_title})
    
    if "reserved_books" not in user:
        user["reserved_books"] = []

    # Add the book details to the user's reserved books
    reserved_book = {"book_id":book["book_id"],"publisher" :book["publisher"],"edition":book["edition"],"title": book["title"], "author": book["author"],"release_date": book["release_date"]}
    register_collections.update_one(
        {"email": email},
        {"$push": {"reserved_books": reserved_book}}
    )
    
    # Refresh user data after update
    user = register_collections.find_one({"email": email})

    return redirect("/")


@app.route("/about.html")
def about():
    return render_template('about.html')

@app.route('/contact.html')
def contact():
    return render_template('contact.html')

if __name__=="__main__":
    app.run(debug=True,port=3000)
