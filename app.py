from flask import Flask, request, jsonify, session, redirect, render_template, send_file, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import cx_Oracle
import io
import random
import string
import re
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = '71d6eeec8496bac46d945c6cbdbb9a27'

# Folder to save uploaded images
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions for uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database connection
def get_db_connection():
    dsn = cx_Oracle.makedsn('localhost', 1521, service_name='XE')
    return cx_Oracle.connect(user='mp5', password='odc', dsn=dsn)

# Helper function to generate captcha text
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_id FROM user_login_details WHERE username = :username', {'username': session['username']})
        user = cursor.fetchone()
        return user[0] if user else None
    except Exception:
        return None
    finally:
        cursor.close()
        conn.close()

# HTML Template Routes
@app.route('/')
def index():
    return redirect('/login')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('/login')
    return render_template('home.html', username=session['username'], profile_picture=session.get('profile_picture'))

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Explicitly print column names for debugging
        print("Attempting to fetch full diagnosis history for username", "rexlin29")
        
        # Fetch full diagnosis history
        cursor.execute(
            """
            SELECT diagnosis_result, diagnosis_date 
            FROM diagnosis_history 
            WHERE username = 'rexlin29'
            ORDER BY diagnosis_date DESC
            """ 
        )
        full_diagnosis_history = cursor.fetchall()
        
        # Debugging: print fetched results to ensure data is correct
        print("Fetched Diagnosis History:", full_diagnosis_history)
        
    except cx_Oracle.DatabaseError as e:
        error_message = str(e)
        print("Error fetching history data:", error_message)
        flash(f'Error fetching history data: {error_message}')
        full_diagnosis_history = []
    finally:
        cursor.close()
        conn.close()
    
    return render_template(
        'history.html', 
        username=session['username'], 
        profile_picture=session.get('profile_picture'), 
        full_diagnosis_history=full_diagnosis_history
    )

@app.route('/diagnose', methods=['GET', 'POST'])
def diagnose():
    if 'username' not in session:
        return redirect('/login')

    diagnosis_result = None
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Mock diagnosis logic
            diagnosis_result = 'Glaucoma detected' if 'glaucoma' in filename.lower() else 'Cataract detected'

            # Save the diagnosis result to the database
            user_id = get_user_id()
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO diagnosis_history (user_id, diagnosis_result, diagnosis_date) VALUES (:user_id, :diagnosis_result, :diagnosis_date)',
                    {'user_id': user_id, 'diagnosis_result': diagnosis_result, 'diagnosis_date': datetime.now()}
                )
                conn.commit()
                flash('Diagnosis saved successfully!')
            except Exception as e:
                flash(f'Error saving diagnosis: {str(e)}')
            finally:
                cursor.close()
                conn.close()
            return render_template('diagnose.html', diagnosis=diagnosis_result, username=session['username'])
        else:
            flash('Invalid file type')
            return redirect(request.url)
    return render_template('diagnose.html', username=session['username'], profile_picture=session.get('profile_picture'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect('/login')

    user_id = get_user_id()
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        age = request.form.get('age')
        address = request.form.get('address')
        gender = request.form.get('gender')
        profile_picture = request.files.get('profile_picture')

        if not full_name or not age or not address or not gender:
            return jsonify({"message": "All fields are required!"}), 400

        try:
            if profile_picture and allowed_file(profile_picture.filename):
                filename = secure_filename(profile_picture.filename)
                file_path = os.path.join('static/profile_pictures', filename)
                profile_picture.save(file_path)

                cursor.execute(''' 
                    MERGE INTO user_profile_details USING dual
                    ON (user_id = :user_id)
                    WHEN MATCHED THEN
                        UPDATE SET full_name = :full_name, age = :age, address = :address, gender = :gender, profile_picture = :profile_picture
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, full_name, age, address, gender, profile_picture)
                        VALUES (:user_id, :full_name, :age, :address, :gender, :profile_picture)
                ''', {
                    'user_id': user_id,
                    'full_name': full_name,
                    'age': age,
                    'address': address,
                    'gender': gender,
                    'profile_picture': file_path
                })
            else:
                cursor.execute(''' 
                    MERGE INTO user_profile_details USING dual
                    ON (user_id = :user_id)
                    WHEN MATCHED THEN
                        UPDATE SET full_name = :full_name, age = :age, address = :address, gender = :gender
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, full_name, age, address, gender)
                        VALUES (:user_id, :full_name, :age, :address, :gender)
                ''', {
                    'user_id': user_id,
                    'full_name': full_name,
                    'age': age,
                    'address': address,
                    'gender': gender
                })
            conn.commit()

            # Return JSON response
            return jsonify({"message": "Profile updated successfully!", "profilePictureUrl": file_path}), 200

        except Exception as e:
            return jsonify({"message": f"Error updating profile: {str(e)}"}), 500

        finally:
            cursor.close()
            conn.close()

    else:
        try:
            cursor.execute('SELECT full_name, age, address, gender, profile_picture FROM user_profile_details WHERE user_id = :user_id', {'user_id': user_id})
            profile_data = cursor.fetchone()
            full_name, age, address, gender, profile_picture = profile_data if profile_data else (None, None, None, None, None)
        except Exception as e:
            flash(f'Error fetching profile: {str(e)}')
            full_name = age = address = gender = profile_picture = None
        finally:
            cursor.close()
            conn.close()

        return render_template('profile.html', username=session['username'], full_name=full_name, age=age, address=address, gender=gender, profile_picture=profile_picture)

@app.route('/profile_picture/<int:user_id>')
def profile_picture(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT profile_picture FROM user_profile_details WHERE user_id = :user_id', {'user_id': user_id})
        profile_picture = cursor.fetchone()[0]
        
        # Check if the profile picture exists, otherwise use the default image
        if profile_picture and os.path.exists(profile_picture):
            return send_file(profile_picture)
        else:
            return send_file('static/images/default-profile.jpg')

    except Exception:
        flash('Error fetching profile picture')
        return send_file('static/images/default-profile.jpg')

    finally:
        cursor.close()
        conn.close()

def get_user_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT full_name, profile_picture FROM user_profile_details WHERE username = :username', {'username': username})
        return cursor.fetchone()
    except Exception as e:
        return None
    finally:
        cursor.close()
        conn.close()



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        captcha_input = request.form.get('captcha')

        # Check captcha
        if 'captcha' not in session or session['captcha'] != captcha_input:
            flash('Invalid captcha, please try again.')
            return redirect('/login')

        # Check for empty username and password
        if not username or not password:
            flash('Username and password are required!')
            return redirect('/login')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Fetch password from the database
            cursor.execute('SELECT password FROM user_login_details WHERE username = :username', {'username': username})
            user = cursor.fetchone()

            # Check if user exists and password matches
            if user and check_password_hash(user[0], password):
                session['username'] = username

                # Fetch user profile details
                cursor.execute('SELECT full_name, profile_picture FROM user_profile_details WHERE user_id = (SELECT user_id FROM user_login_details WHERE username = :username)', {'username': username})
                profile = cursor.fetchone()
                
                # Store profile information in the session
                if profile:
                    session['full_name'] = profile[0]
                    session['profile_picture'] = profile[1] if profile[1] else 'static/images/default-profile.jpg'
                else:
                    session['full_name'] = username  # Fallback to username if no profile is found
                    session['profile_picture'] = 'static/images/default-profile.jpg'  # Default picture

                return redirect('/home')  # Redirect to home after successful login
            else:
                flash('Invalid username or password!')
                return redirect('/login')

        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect('/login')
        finally:
            cursor.close()
            conn.close()
    
    # Generate and display captcha
    session['captcha'] = generate_captcha()
    return render_template('login.html', captcha=session['captcha'])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        if not username or not password or not confirm_password:
            flash('All fields are required!')
            return redirect('/signup')

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect('/signup')

        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
        if not re.match(password_regex, password):
            flash('Password must contain at least one uppercase, one lowercase, one digit, and one special character, and be at least 8 characters long!')
            return redirect('/signup')

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO user_login_details (username, password) VALUES (:username, :password)', 
                           {'username': username, 'password': hashed_password})
            conn.commit()
            flash('Signup successful! Please log in.')
            return redirect('/login')
        except cx_Oracle.IntegrityError:
            flash('Username already exists!')
            return redirect('/signup')
        except Exception as e:
            flash(f'Error: {str(e)}')
            return redirect('/signup')
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
