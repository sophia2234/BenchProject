# DASHBOARD PAGE: This page starts an HTML INDEX page, has new REGISTRATION page [with validation], deals with SQL photo upload [success and fail]
# password UPDATE [with validation and error messages], deals with PREVIOUSLY OWNED properties with a WEB FORM [with validation], renders
# TABLE_2, uses ADD button to add properties to table, DELETES property from table [***BUT NOT FROM RECOMMENDED***], add PREVIOUSLY OWNED
# properties to a display table, and has the AI CODE [at the end]
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify, session, Flask
)
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.__init__ import create_app
import sqlite3
import json
from flask_uploads import UploadSet, configure_uploads, IMAGES
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mpl_toolkits
import re
import time
import uuid
import os
import datetime

bp = Blueprint('dashboard', __name__)


# Method that renders index.html and handles all POST requests from index.html
@bp.route('/updateProfile', methods=('GET', 'POST'))
@login_required
def index():
    if request.method == 'POST':
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        description = request.form['description']
        photoUploaded = False
        error = []
        try:
            file = request.files['photo']
            extension = os.path.splitext(file.filename)[1]
            ALLOWED_EXTENSIONS = set(['.jpe', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.bmp'])
            if extension not in ALLOWED_EXTENSIONS and extension != '':
                error.extend(['You submitted a ' + str(
                    type(extension)) + ' file which is invalid. Please Enter A Valid Photo Type ' + str(
                    ALLOWED_EXTENSIONS)])
            elif extension == '':
                print("Do nothing")
            else:
                f_name = str(uuid.uuid4()) + extension
                app = create_app(None)
                file.save(os.path.join(app.config['UPLOADED_PHOTOS_DEST'], f_name))
                location = "uploads/" + f_name
                photoUploaded = True
        except:
            photoUploaded = False

        db = get_db()
        if re.search("[a-zA-Z ]+", firstName) is None:
            error.extend(["Please Enter a Valid First Name"])
        if re.search(".+@.+", email) is None:
            error.extend(["Please Enter a Valid Email Address"])
        if re.search("[a-zA-Z ]+", lastName) is None:
            error.extend(["Please Enter a Valid Last Name"])
        elif db.execute(
                'SELECT email FROM user WHERE email = ? AND userId =?', (email, session.get('user_id'))
        ).fetchone():
            error is None
        #            error = []
        elif db.execute(
                'SELECT email FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error.extend(['User with email address {} is already registered.'.format(email)])

        # SQL statements when Photo is uploaded
        if not error and photoUploaded:

            destination = db.execute(
                'SELECT profilePicture FROM user WHERE firstName = ? AND email = ? AND userId = ?',
                (firstName, email, session.get('user_id'))
            ).fetchone()
            if str(destination[0]) != "uploads/stickfigure.png":
                os.remove('flaskr/static/' + str(destination[0]))

            db.execute(
                'UPDATE user SET email = ?, firstName = ? , lastName = ?, description = ?, profilePicture = ? WHERE userId =? ',
                (email, firstName, lastName, description, location, session.get('user_id'))
            )
            db.commit()
            print("successfully updated user")

        # SQL statements when Photo is not uploaded
        elif not error and not photoUploaded:
            db.execute(
                'UPDATE user SET email = ?, firstName = ? , lastName = ?, description = ? WHERE userId =? ',
                (email, firstName, lastName, description, session.get('user_id'))
            )
            db.commit()
            print("successfully updated user")
        else:
            for eror in error:
                flash(eror, 'success')

        return redirect(url_for('dashboard.index'))

        for eror in error:
            flash(eror, 'success')

    return render_template('dashboard/index.html')


# Method that is called when users want to change their password on index.html page
@bp.route('/changepassword', methods=('GET', 'POST'))
@login_required
def changePassword():
    if request.method == "POST":
        password = request.form['password']
        passwordConfirmation = request.form['password2']
        error = []
        db = get_db()

        if not re.search("((?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*\W).{8,})", password):
            error.extend([
                "Please enter a password at of least 8 characters containing an uppercase letter, lowercase letter, number, and special character."])

        if password != passwordConfirmation:
            error.extend(['Password must match.'])
        if not error:
            db.execute(
                'UPDATE user SET password = ? WHERE userId = ?',
                (generate_password_hash(password), session.get('user_id'))
            )
            db.commit()
            return redirect(url_for('dashboard.index'))

        for eror in error:
            flash(eror, 'error')

    return render_template('dashboard/index.html')


# Adds properties to previously owned through a form (manually) and renders tables.html
@bp.route('/table1', methods=('GET', 'POST'))
@login_required
def table1():
    if request.method == 'POST':
        address = request.form['address']
        beds = request.form['beds']
        baths = request.form['baths']
        halfBaths = request.form['halfBathrooms']
        sqft = request.form['sqft']
        zip = request.form['zip']
        yearBuilt = request.form['yearBuilt']
        landValue = request.form['landValue']
        buildingValue = request.form['buildingValue']
        yearPurchased = request.form['yearPurchased']
        yearSold = request.form['yearSold']
        soldAmount = request.form['soldAmount']
        renovationCost = request.form['renovationCost']
        buildingStyle = request.form['buildingStyle']
        currentYear = int(datetime.datetime.now().year)
        error = []
        db = get_db()

        if re.search("\d+\s.+", address) is None:
            error.extend(["Please Enter a Valid Address"])
        if re.search("[0-9]+", beds) is None:
            error.extend(["Please Enter a Valid Integer of Bedrooms"])
        if re.search("[0-9]+", baths) is None:
            error.extend(["Please Enter a Valid Integer of Bathrooms"])
        if re.search("[0-9]+", halfBaths) is None:
            error.extend(["Please Enter a Valid Integer of Half Bathrooms"])
        if re.search("[0-9]+", sqft) is None:
            error.extend(["Please Enter a Valid Integer of Square Feet"])
        if re.search("[0-9]+", zip) is None or len(zip) > 5 or len(zip) < 5:
            error.extend(["Please Enter a Valid Zip Code"])
        if re.search("[0-9]+", yearBuilt) is None or int(yearBuilt) > currentYear:
            error.extend(["Please Enter a Valid Year Built"])
        if re.search("[0-9]+", landValue) is None:
            error.extend(["Please Enter a Valid Integer of Land Value"])

        if yearSold is '':
            print('Do nothing')
        elif int(yearSold) > int(currentYear):
            error.extend(["Please Enter a Valid Year Sold"])
        if soldAmount is not None:
            print("do nothing")
        elif re.search("[0-9]+", soldAmount) is None:
            error.extend(["Please Enter a Valid Integer for Sold Amount"])
        if renovationCost is not None:
            print("do nothing")
        elif re.search("[0-9]+", renovationCost) is None:
            error.extend(["Please Enter a Valid Integer for Renovation Cost"])

        if re.search("[0-9]+", buildingValue) is None:
            error.extend(["Please Enter a Valid Integer of Building Value"])
        if re.search("[0-9]+", yearPurchased) is None or int(yearPurchased) > int(currentYear):
            error.extend(["Please Enter a Valid Year Purchased"])
        elif int(yearPurchased) < int(yearBuilt):
            error.extend(["The Year Built must be before the Year Purchased"])
        if db.execute(
                'SELECT address, zip_code FROM currentProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip, session.get('user_id'))
        ).fetchone() is not None:
            error.extend(["This property is already in the Previously Owned table."])

        # SQL to run if there is no error and the property doesn't already exist
        if not error:
            totalValue = int(landValue) + int(buildingValue)
            db.execute(
                'INSERT INTO currentProperties (address, total_beds, bath, half_bath, living_sq_ft, building_style, zip_code, year_built, land_value, bldg_value, total_value, year_purchased, year_sold, sold_price, renovation_cost, userId, like_dislike) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? , ?, ?, ?, ?, ?)',
                (address, beds, baths, halfBaths, sqft, buildingStyle, zip, yearBuilt, landValue, buildingValue,
                 totalValue,
                 yearPurchased, yearSold, soldAmount, renovationCost, session.get('user_id'), 1)
            )
            db.commit()
            print("successfully inserted into database")

        for eror in error:
            flash(eror, 'error')

    return render_template('dashboard/tables.html')


# Renders soldPropertiesTable.html
@bp.route('/soldProperties', methods=('GET', 'POST'))
@login_required
def soldProperties():
    if request.method == 'POST':
        address = request.form['address']
        beds = request.form['beds']
        baths = request.form['baths']
        halfBaths = request.form['halfBathrooms']
        sqft = request.form['sqft']
        zip = request.form['zip']
        yearBuilt = request.form['yearBuilt']
        landValue = request.form['landValue']
        buildingValue = request.form['buildingValue']
        yearPurchased = request.form['yearPurchased']
        yearSold = request.form['yearSold']
        soldAmount = request.form['soldAmount']
        renovationCost = request.form['renovationCost']
        buildingStyle = request.form['buildingStyle']
        currentYear = int(datetime.datetime.now().year)
        error = []
        db = get_db()

        if re.search("\d+\s.+", address) is None:
            error.extend(["Please Enter a Valid Address"])
        if re.search("[0-9]+", beds) is None:
            error.extend(["Please Enter a Valid Integer of Bedrooms"])
        if re.search("[0-9]+", baths) is None:
            error.extend(["Please Enter a Valid Integer of Bathrooms"])
        if re.search("[0-9]+", halfBaths) is None:
            error.extend(["Please Enter a Valid Integer of Half Bathrooms"])
        if re.search("[0-9]+", sqft) is None:
            error.extend(["Please Enter a Valid Integer of Square Feet"])
        if re.search("[0-9]+", zip) is None or len(zip) > 5 or len(zip) < 5:
            error.extend(["Please Enter a Valid Zip Code"])
        if re.search("[0-9]+", yearBuilt) is None or int(yearBuilt) > currentYear:
            error.extend(["Please Enter a Valid Year Built"])
        if re.search("[0-9]+", landValue) is None:
            error.extend(["Please Enter a Valid Integer of Land Value"])

        if re.search("[0-9]+", yearSold) is None or int(yearSold) > currentYear or int(yearSold) < int(yearBuilt):
            error.extend(["Please Enter a Valid Year Sold"])
        if re.search("[0-9]+", soldAmount) is None:
            error.extend(["Please Enter a Valid Integer for Sold Amount"])
        if renovationCost is None:
            error.extend(["Please Enter a Valid Integer for Renovation Cost or enter 0"])
        elif re.search("[0-9]+", renovationCost) is None:
            error.extend(["Please Enter a Valid Integer for Renovation Cost or enter 0"])
        if re.search("[0-9]+", buildingValue) is None:
            error.extend(["Please Enter a Valid Integer of Building Value"])
        if re.search("[0-9]+", yearPurchased) is None or int(yearPurchased) > int(currentYear):
            error.extend(["Please Enter a Valid Year Purchased"])
        elif int(yearPurchased) < int(yearBuilt):
            error.extend(["The Year Built must be before the Year Purchased"])
        if db.execute(
                'SELECT address, zip_code FROM formerProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip, session.get('user_id'))
        ).fetchone() is not None:
            error.extend(["This property is already in the Previously Owned table."])

        # SQL to run if there is no error and the property doesn't already exist
        if not error:
            totalValue = int(landValue) + int(buildingValue)
            db.execute(
                'INSERT INTO formerProperties (address, total_beds, bath, half_bath, living_sq_ft, building_style, zip_code, year_built, land_value, bldg_value, total_value, year_purchased, year_sold, sold_price, renovation_cost, userId, like_dislike) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? ,? , ?, ?, ?, ?, ?)',
                (address, beds, baths, halfBaths, sqft, buildingStyle, zip, yearBuilt, landValue, buildingValue,
                 totalValue,
                 yearPurchased, yearSold, soldAmount, renovationCost, session.get('user_id'), 1)
            )
            db.commit()
            print("successfully inserted into database")

        for eror in error:
            flash(eror)

    return render_template('dashboard/soldPropertiesTable.html')


# Deletes a property from sold properties when user presses delete button in soldPropertiesTable.html
@bp.route('/soldProperties/delete', methods=('GET', 'POST'))
def delete_soldPropertiess_row():
    db = get_db()
    if request.method == 'POST':
        jsonData = request.get_json()
        address = jsonData['address']
        zip_code = jsonData['zip_code']
        db.execute('DELETE FROM formerProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                   (address, zip_code, session.get('user_id')))
        db.commit()
        print("Deleted Successfully")

    return "Made it here in delete_table1_row()"


# Sends all Previously owned properties to soldPropertiesTable.html
@bp.route('/soldProperties/previousProperties', methods=('GET', 'POST'))
def sendSoldProperties():
    db = get_db()
    query = "SELECT * FROM soldProperityView WHERE userId = %s" % (session.get('user_id'))
    data = pd.read_sql_query(query, db)
    data.sort_values(by=["year_purchased"])
    jsonData = data.to_json(orient="records")
    return jsonData


# Renders tables_2.html
@bp.route('/table2')
@login_required
def table2():
    return render_template('dashboard/tables_2.html')


# Adds property to previously owned through the "Add" button on tables_2.html (Dashboard)
@bp.route('/table1/add', methods=('GET', 'POST'))
def addRow():
    db = get_db()
    if request.method == 'POST':
        jsonData = request.get_json()
        propertyId = jsonData['ID']
        class1 = jsonData['class']
        land_value = jsonData['land_value']
        bldg_value = jsonData['bldg_value']
        total_value = jsonData['total_value']
        address = jsonData['address']
        address_city = jsonData['address_city']
        zip_code = jsonData['zip_code']
        owner = jsonData['owner']
        school_dist = jsonData['school_dist']
        land_sq_ft = jsonData['land_sq_ft']
        year_built = jsonData['year_built']
        living_sq_ft = jsonData['living_sq_ft']
        condition = jsonData['condition']
        residence_type = jsonData['residence_type']
        building_style = jsonData['building_style']
        bath = jsonData['bath']
        half_bath = jsonData['half_bath']
        bedrooms = jsonData['bedrooms']
        basement_beds = jsonData['basement_beds']
        total_beds = jsonData['total_beds']
        attached_gar = jsonData['attached_gar']
        price = jsonData['price']
        grade = jsonData['grade']
        currentYear = int(datetime.datetime.now().year)

        if db.execute(
                'SELECT * FROM currentProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip_code, session.get('user_id'))
        ).fetchone() is not None:
            db.execute(
                'UPDATE currentProperties SET like_dislike = 1 WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip_code, session.get('user_id'))
            )
            db.commit()
            print("Updated Successfully")
        else:
            db.execute(
                'INSERT INTO currentProperties(class,land_value,bldg_value,total_value,address,address_city,zip_code,owner,school_dist,land_sq_ft,year_built,living_sq_ft,condition,residence_type,building_style,bath,half_bath,bedrooms,basement_beds,total_beds,attached_gar,price,grade, year_purchased, like_dislike,userID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);',
                (class1, land_value, bldg_value, total_value, address, address_city, zip_code, owner, school_dist,
                 land_sq_ft, year_built, living_sq_ft, condition, residence_type, building_style, bath, half_bath,
                 bedrooms, basement_beds, total_beds, attached_gar, price, grade, currentYear, 1,
                 session.get('user_id'))
            )
            db.commit()
            print("Inserted Successfully")
    deleteRow()
    return "Made it here in addRow()"


# Adds property to soldProperties owned through the "Sell" button on tables.html (ownedTable)
@bp.route('/table1/sellProperty', methods=('GET', 'POST'))
def addToSold():
    db = get_db()
    if request.method == 'POST':
        address = request.form['preAddress']
        zip_code = request.form['preZipCode']
        soldAmount = request.form['soldAmount']
        year_sold = request.form['year_sold']
        renovationCost = request.form['renovationCost']
        currentYear = int(datetime.datetime.now().year)
        error = []

        if re.search("[0-9]+", year_sold) is None or int(year_sold) < currentYear:
            error.extend(["Please Enter a Valid Year Sold"])
        if re.search("[0-9]+", soldAmount) is None:
            error.extend(["Please Enter a Valid Integer for Sold Amount"])
        if renovationCost is None:
            error.extend(["Please Enter a Valid Integer for Renovation Cost or enter 0"])
        elif re.search("[0-9]+", renovationCost) is None:
            error.extend(["Please Enter a Valid Integer for Renovation Cost or enter 0"])

        if db.execute(
                'SELECT * FROM currentProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip_code, session.get('user_id'))
        ).fetchone() is not None and not error:
            db.execute(
                'UPDATE currentProperties SET year_sold = ' + year_sold + ' , sold_price = ' + soldAmount + ' , renovation_cost =' + renovationCost + ' WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip_code, session.get('user_id'))
            )
            db.commit()
            print("Updated Successfully")
            db.execute('DELETE FROM currentProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                       (address, zip_code, session.get('user_id')))
            db.commit()
            print("Deleted Successfully")
        else:
            for eror in error:
                flash(eror, 'success')

    return redirect(url_for('dashboard.table1'))


# Deletes a property from previously owned when user presses delete button in tables.html
@bp.route('/table1/delete', methods=('GET', 'POST'))
def delete_table1_row():
    db = get_db()
    if request.method == 'POST':
        jsonData = request.get_json()
        address = jsonData['address']
        zip_code = jsonData['zip_code']
        db.execute('DELETE FROM currentProperties WHERE address = ? AND zip_code = ? AND userId = ?',
                   (address, zip_code, session.get('user_id')))
        db.commit()
        print("Deleted Successfully")

    return "Made it here in delete_table1_row()"


# Sends filtered Previously owned properties to tables.html (does update the SQL query....but not load it- delete later or find another solution)
@bp.route('/table1/filterOwnedProperty', methods=('GET', 'POST'))
def sendFilteredProperties():
    db = get_db()
    if request.method == 'POST':
        yearPurchase = request.form['yearPurchase']
        yearSold = request.form['yearSold']
        buildingStyle = request.form['buildingStyle']
        db.execute("DROP VIEW IF EXISTS soldProperityView;")
        if buildingStyle == "all" and yearPurchase == "" and yearSold == "":
            db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (session.get('user_id')))
        elif buildingStyle == "all" and yearPurchase != "" and yearSold == "":
            db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                session.get('user_id')) + " AND year_purchased == %s" % yearPurchase)
        elif buildingStyle == "all" and yearPurchase == "" and yearSold != "":
            db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                session.get('user_id')) + " AND year_sold == %s" % yearSold)
        elif buildingStyle == "all" and yearPurchase != "" and yearSold != "":
            db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                session.get('user_id')) + " AND year_sold == %s" % yearSold + " AND year_purchased == %s" % yearPurchase)
        elif buildingStyle != "all":
            buildingStyle = "'" + buildingStyle + "'"
            if yearPurchase == "" and yearSold == "":
                db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                    session.get('user_id')) + " AND building_style LIKE %s" % buildingStyle)
            elif yearPurchase != "" and yearSold == "":
                db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                    session.get('user_id')) + " AND year_purchased == %s" % yearPurchase + " AND building_style LIKE %s" % buildingStyle)
            elif yearPurchase == "" and yearSold != "":
                db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                    session.get('user_id')) + " AND year_sold == %s" % yearSold + " AND building_style LIKE %s" % buildingStyle)
            elif yearPurchase != "" and yearSold != "":
                db.execute("CREATE VIEW soldProperityView AS select * From formerProperties WHERE userId = %s" % (
                    session.get(
                        'user_id')) + " AND year_sold == %s" % yearSold + " AND year_purchased == %s" % yearPurchase + " AND building_style LIKE %s" % buildingStyle)

    return redirect(url_for('dashboard.table2'))



# Sends all Previously owned properties to tables.html
@bp.route('/table1/previousProperties', methods=('GET', 'POST'))
def sendProperties():
    db = get_db()
    query = "SELECT * FROM currentProperties WHERE userId = %s" % (session.get('user_id'))
    data = pd.read_sql_query(query, db)
    data.sort_values(by=["year_purchased"])
    jsonData = data.to_json(orient="records")
    return jsonData


# This method is called when users press the "delete" button in tables_2.html. This 
# adds the deleted property to the user's model as a "disliked" property. NOTE: THIS DOES NOT GUARENTEE
# THE DELETED PROPERTY WILL BE WIPED FROM THE RECOMMENDED PROPERTIES TABLE
@bp.route('/table2/delete', methods=('GET', 'POST'))
def deleteRow():
    db = get_db()
    if request.method == 'POST':
        jsonData = request.get_json()
        propertyId = jsonData['ID']
        class1 = jsonData['class']
        land_value = jsonData['land_value']
        bldg_value = jsonData['bldg_value']
        total_value = jsonData['total_value']
        address = jsonData['address']
        address_city = jsonData['address_city']
        zip_code = jsonData['zip_code']
        owner = jsonData['owner']
        school_dist = jsonData['school_dist']
        land_sq_ft = jsonData['land_sq_ft']
        year_built = jsonData['year_built']

        living_sq_ft = jsonData['living_sq_ft']
        condition = jsonData['condition']
        residence_type = jsonData['residence_type']
        building_style = jsonData['building_style']
        bath = jsonData['bath']
        half_bath = jsonData['half_bath']
        bedrooms = jsonData['bedrooms']
        basement_beds = jsonData['basement_beds']
        total_beds = jsonData['total_beds']
        attached_gar = jsonData['attached_gar']
        price = jsonData['price']
        grade = jsonData['grade']

        # If property is already in model, set it to "disliked"
        if db.execute(
                'SELECT * FROM properties WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip_code, session.get('user_id'))
        ).fetchone() is not None:
            db.execute(
                'UPDATE properties SET like_dislike = 0 WHERE address = ? AND zip_code = ? AND userId = ?',
                (address, zip_code, session.get('user_id'))
            )
            db.commit()
            return "Updated Successfully"

        # If property is not in model, add it to model as a "disliked" property
        else:
            db.execute(
                'INSERT INTO properties(class,land_value,bldg_value,total_value,address,address_city,zip_code,owner,school_dist,land_sq_ft,year_built,living_sq_ft,condition,residence_type,building_style,bath,half_bath,bedrooms,basement_beds,total_beds,attached_gar,price,grade,like_dislike,userID) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);',
                (class1, land_value, bldg_value, total_value, address, address_city, zip_code, owner, school_dist,
                 land_sq_ft, year_built, living_sq_ft, condition, residence_type, building_style, bath, half_bath,
                 bedrooms, basement_beds, total_beds, attached_gar, price, grade, 0, session.get('user_id'))
            )
            db.commit()
            return "Inserted Successfully"

    return "Made it here in deleteRow()"


# Method that renders homepage.html
@bp.route('/')
def homepage():
    return render_template('dashboard/homepage.html')


# Method that renders faq.html
@bp.route('/faq')
def faq():
    return render_template('dashboard/faq.html')


# AI Function that sends Recommended Properties to tables_2.html
@bp.route('/table2/recommended', methods=('GET', 'POST'))
def sendRecommended():
    db = get_db()
    query = "SELECT * FROM properties WHERE userId = %s" % (session.get('user_id'))
    # import the training data- houses that have previously been liked or disliked by the user in properties tables
    train_data = pd.read_sql_query(query, db)

    train_data.head()

    # set up the data to train the system
    labels = train_data['like_dislike']
    train1 = train_data.drop(
        ['ID', 'class', 'address', 'address_city', 'zip_code', 'owner', 'school_dist', 'land_sq_ft', 'residence_type',
         'building_style', 'condition', 'bedrooms', 'basement_beds', 'attached_gar', 'grade', 'like_dislike', 'price',
         'userId'], axis=1)
    train1.head()
    from sklearn.model_selection import train_test_split

    # Configuring the machine to learn
    x_train, x_test, y_train, y_test = train_test_split(train1, labels, test_size=0.10, random_state=1)

    from sklearn import ensemble
    clf = ensemble.GradientBoostingClassifier(n_estimators=1000, max_depth=10, min_samples_split=2,
                                              learning_rate=0.2)

    # train the model
    clf.fit(x_train, y_train)

    # test how well the model learned
    clf.score(x_test, y_test)

    # read in the dataset of houses
    data = pd.read_csv("flaskr/house_data.csv")
    x_predict = data.drop(
        ['ID', 'class', 'address', 'address_city', 'zip_code', 'owner', 'school_dist', 'land_sq_ft', 'residence_type',
         'building_style', 'condition', 'bedrooms', 'basement_beds', 'attached_gar', 'grade', 'like_dislike', 'price'],
        axis=1)

    # predict if dataset houses should be liked or disliked
    prediction = clf.predict(x_predict)

    # put predictions into the dataset
    prediction.tolist()
    data['like_dislike'] = prediction

    # create new dataset with only liked houses
    output_data = data[data.like_dislike != 0]

    # Sort the output data
    output_data.sort_values(by=["ID"])

    # convert new dataset to json
    json_file = output_data.to_json(orient="records")

    return json_file
