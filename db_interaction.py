import sqlite3  # importing required modules
from datetime import date
import bcrypt  # module responsible for hashing


with sqlite3.connect("user.db") as db:  # connecting to the database
    c = db.cursor()
    db.execute("PRAGMA foreign_keys = 1")
    try:
        c.execute("""CREATE TABLE user_details(user_id INTEGER PRIMARY KEY, username text, password text,
         name text,join_date text""")  # provided that the table doesn't already exist
        c.execute("""CREATE TABLE projectile_results(
                    projectile_id INTEGER PRIMARY KEY, 
                    user_id integer,
                    range real,
                    max_height real
                    FOREIGN KEY (user_id) REFERENCES user_details (user_id)""")
        c.execute("""CREATE TABLE projectile_details(
                  projectile_id INTEGER PRIMARY KEY,"
                  projectile_name text,
                  FOREIGN KEY (projectile_id) REFERENCES projectile_results (projectile_id)""")
    except:
        pass


def signUp_validation(user_details):  # takes the user_details list containing: name, username, password
    date_today = date.today()
    with sqlite3.connect("user.db") as db:
        c = db.cursor()
    find_user = ("SELECT * FROM user_details WHERE username==?")  # creating the query to find user
    c.execute(find_user, [(user_details[1])])  # executing the query
    if c.fetchall():
        return False  # This will occur if the user already exists
    else:
        hashed_password = hash(user_details[2])
        insert_data = """insert into user_details (username,password,name_user,join_date) VALUES(?,?,?,?)"""
        # creating an SQL query to insert new users
        c.execute(insert_data,
                  [(user_details[1]), hashed_password, (user_details[0]), date_today])  # executing the query
        db.commit()  # Storing the information
        db.close()
        return True  # Returns true if the user is added


def login_validation(user_details):  # takes list of user details contains: username and password inputs
    find_user = ("SELECT password FROM user_details WHERE username == ?")  # An SQL query that finds user
    with sqlite3.connect("user.db") as db:
        c = db.cursor()
    c.execute(find_user, [(user_details[0])])  # executes the query
    details = c.fetchall()
    if details:
        for i in details:
            hashed_password = i[0]
    else:
        return False
    # Returns boolean based on whether the user has entered corrected password or not
    db.close()
    return False if hashed_password is None or not bcrypt.checkpw(user_details[1].encode(), hashed_password) else True


def get_id(username):
    with sqlite3.connect("user.db") as db:
        c = db.cursor()
    find_user = ("SELECT user_id FROM user_details WHERE username == ?")  # An SQL query that finds user
    c.execute(find_user, [(username)])  # executes the query
    id_number = c.fetchone()[0]
    return id_number


def store_values(projectile_values, user_id, projectile_name):
    x_displacement, max_height = projectile_values
    with sqlite3.connect("user.db") as db:
        c = db.cursor()
    insert_values = """insert into projectile_results (user_id,range,max_height) 
    VALUES(?,?,?) """
    c.execute(insert_values, [user_id, max_height, x_displacement])  # executing the query
    projectile_id = c.lastrowid
    insert_details = """insert into projectile_details (projectile_id,projectile_name)
                    VALUES(?,?)"""
    c.execute(insert_details, [projectile_id, projectile_name])
    db.commit()
    db.close()


def get_values(user_id):
    with sqlite3.connect("user.db") as db:
        c = db.cursor()
    select_values = """SELECT projectile_details.projectile_name, projectile_results.range, 
    projectile_results.max_height FROM projectile_details,projectile_results  
    WHERE user_id == ? AND projectile_results.projectile_id = projectile_details.projectile_id"""
    c.execute(select_values, [user_id])
    results = c.fetchall()
    names = [item[0] for item in results]
    ranges = [item[1] for item in results]
    max_heights = [item[2] for item in results]
    return names, ranges, max_heights

def hash(passwordToHash):
    password = passwordToHash.encode()  # bcrypt requires all strings to be encoded before hashing
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())  # generating hashed password
    return hashed_password

