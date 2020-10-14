from flask import *
import sqlite3
from helper import login_required
import os.path

app=Flask(__name__)
app.secret_key="CapitalBank"

#landing page code
@app.route("/")
def landing_page():
    return render_template("landing_page.html")


#login page code
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="POST":
        username=request.form["username"].strip()
        password=request.form["password"].strip()

        if not username or not password:
            flash("Invalid Username or Password")
            return redirect(url_for('login'))

        table_data=None
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            table_data=list(db.execute("select * from data where username=?", (username,)))

        if len(table_data)<1 or username!= table_data[0][2] or password!=table_data[0][3]:
            flash("Invalid Username or Password")
            return redirect(url_for('login'))

        session['userno']=table_data[0][0]

        return render_template("index.html", name=table_data[0][1])

    else:
        return render_template("login.html")



#register page code
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="POST":
        name=request.form["name"].strip()
        username=request.form["username"].strip()
        email=request.form["email"].strip()
        password=request.form["password"].strip()
        repassword=request.form["repassword"].strip()

        if not name or not password or not repassword or not username or not email:
            flash("Invalid Entries: Kindly Check")
            return redirect(url_for("register"))

        if password!=repassword:
            flash("Passwords don't match!")
            return redirect(url_for("register"))

        table_data=None
        
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            table_data=list(db.execute("select * from data where username=?",(username,)))

        if len(table_data)>0:
            flash("Username Already Exists. Change Username")
            return redirect(url_for("register"))

        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            db.execute("insert into data(name, username, password, email) values(?,?,?,?)", (name, username, password,email))
            conn.commit()
            table_data=list(db.execute("select * from data where username=?",(username,)))
        
        session['userno']=table_data[0][0]

        return render_template("index.html", name=name)

    else:
        return render_template("register.html")



#deposit page coding
@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    if request.method=="POST":
        name=request.form["name"]
        account_no=request.form["account_no"]
        try:
            amount=round(float(request.form["amount"]), 2)
        except:
            amount=0

        description="Deposit by: "+name

        if not name or not account_no or not amount:
            flash("Entry Field Empty!")
            return redirect(url_for("deposit"))

        data=None
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            data=list(db.execute("Select * from actdat where account=?", (account_no,)))
            
        if len(data)!=1:
            flash("Account Number Invalid- Account doesn't exists")
            return redirect(url_for("deposit"))

        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            db.execute("insert into transactions(account, description, type, amount) values(?,?,?,?)", (data[0][1], description, "Deposit", amount))
            db.execute("update actdat set totamt=totamt + ? where account=?", (amount, data[0][1]))
            conn.commit()

        flash("Amount - Deposited")
        return redirect(url_for("deposit"))

    else:
        return render_template("deposit.html")


#withdraw page coding
@app.route("/withdraw", methods=["GET", "POST"])
@login_required
def withdraw():
    if request.method=="POST":
        name=request.form["name"]
        account_no=request.form["account_no"]
        try:
            amount=round(float(request.form["amount"]), 2)
        except:
            amount=0

        description="Withdrawn by: "+name

        if not name or not account_no or not amount:
            flash("Entries field empty")
            return redirect(url_for("withdraw"))

        data=None
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            data=list(db.execute("Select * from actdat where account=?", (account_no,)))
            
        if len(data)!=1:
            flash("Account Number Invalid- Account doesn't exists")
            return redirect(url_for("withdraw"))

        if data[0][4]<amount:
            flash("Amount Unavailable in account")
            return redirect(url_for("withdraw"))

        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            db.execute("insert into transactions(account, description, type, amount) values(?,?,?,?)", (data[0][1], description, "Withdraw", amount))
            db.execute("update actdat set totamt=totamt - ? where account=?", (amount, account_no))  
            conn.commit()

        flash("Amount Withdrawn: Rs"+str(amount))
        return redirect(url_for("withdraw"))

    else:
        return render_template("withdraw.html")


#transactions page code
@app.route("/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    if request.method=="POST":
        account_no=request.form["account_no"]

        if not account_no:
            flash("Entries Field Empty")
            return redirect(url_for("transactions"))

        data=None
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            data=list(db.execute("select * from actdat where account=?", (account_no,)))

        if len(data) != 1:
            flash("Invalid Account Number/ or No Entries Available")
            return redirect(url_for("transactions"))
        
        lable=None
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            data=list(db.execute("select * from transactions where account=? order by datetime(date) desc", (account_no,)))
            lable=list(db.execute("Select * from actdat where account=?", (account_no,)))
        
        return render_template("transactions_post.html", data=data, lable=lable)
    else:
        return render_template("transactions_get.html")



#create account page code
@app.route("/create_account", methods=["GET", "POST"])
@login_required
def create_account():
    if request.method=="POST":
        name=request.form["name"]
        address=request.form["address"]
        contact=request.form["contact"]
        account=request.form["account"]
        try:
            amount=round(float(request.form["amount"]), 2)
        except:
            flash("Entries Field Empty")
            return redirect(url_for("create_account"))

        description="Amount Deposit by: "+name

        rows=None
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            rows=list(db.execute("Select * from actdat where account=?",(account,)))

        if len(rows)>0:
            flash("Account Number already exists. Try Again with new Account number")
            return redirect(url_for("create_account"))
        
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            db.execute("insert into actdat(name, account, totamt, address, contact) values(?,?,?,?,?)", (name, account, amount, address, contact))
            db.execute("insert into transactions(account, description, amount, type) values(?,?,?,?)", (account, description, amount, "Deposit"))
            conn.commit()

        flash("Account Created! Account Number: "+account)
        return render_template("create_account.html")

    else:
        return render_template("create_account.html")



#logout code
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("User Logout Successful")
    return redirect(url_for("landing_page"))



#change password code
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method=="POST":
        oldpassword=request.form["oldpassword"]
        password=request.form["password"]
        repassword=request.form["repassword"]

        if not password or not repassword or not oldpassword:
            flash("Entries Field Empty")
            return redirect(url_for("change_password"))

        if password!=repassword:
            flash("Passwords don't match")
            return redirect(url_for("change_password"))

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()

            data=list(db.execute("select password from data where userno=?", (session["userno"],)))
            if data[0][0] != oldpassword:
                flash("Oldpassword doesnot match. Kindly Check.")
                return redirect(url_for("change_password"))

            db.execute("update data set password=? where userno=?", (password, session['userno']))
            conn.commit()

        flash("Password Changed! Login again")
        return redirect(url_for("change_password"))

    else:
        return render_template("change_password.html")



#laon code
@app.route("/loan", methods=["GET", "POST"])
@login_required
def loan():
    if request.method=="POST":
        account=request.form["account"]
        str_type=request.form["type"]
        try:
            amount=round(float(request.form["amount"]), 2)
        except:
            flash("Entries Field Empty")
            return redirect(url_for("loan"))

        if not account or not str_type:
            flash("Entries Field Empty")
            return redirect(url_for("loan"))

        description="Loan: "+str_type

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            data=list(db.execute("select * from actdat where account=?", (account,)))

            if len(data)<1:
                flash("Account doesnot Exists")
                return redirect(url_for("loan"))

        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            db.execute("insert into transactions(account, description, type, amount) values(?,?,?,?)", (account, description, "Loan", amount))
            db.execute("update actdat set totamt=totamt+? where account=?", (amount, account))
            conn.commit()

        flash("Loan Sanctioned!")
        return redirect(url_for("loan"))

    else:
        return render_template("loan.html")



#shows account details
@app.route("/details")
@login_required
def details():
    rows=None
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "CapitalBank.db")
    with sqlite3.connect(db_path) as conn:
        db=conn.cursor()
        rows=list(db.execute("select * from actdat"))

    return render_template("details.html", rows=rows)



#deletes the account
@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    if request.method=="POST":
        account=request.form["account"]

        if not account:
            flash("Entry Field Empty!")
            return redirect(url_for("delete_account"))

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, "CapitalBank.db")
        with sqlite3.connect(db_path) as conn:
            db=conn.cursor()
            data=list(db.execute("Select * from actdat where account=?", (account,)))

            if len(data)<1:
                flash("Account doesnot Exist. Unable to delete.")
                return redirect(url_for("delete_account"))

            db.execute("delete from transactions where account=?",(account,))
            db.execute("delete from actdat where account=?",(account,))
            conn.commit()

        flash("Account Number: "+str(account)+" Deleted!")
        return redirect(url_for("delete_account"))

    else:
        return render_template("delete_account.html")

if __name__=="__main__":
    app.run(debug=True)

"""
Name:- Deepanshu Narang
Roll Number:- 1802328
Class:- ECE Y1
Project Name:- Capital Bank
"""