# Ocular Cataract Disease Recognition (ODC)

This project is a Flask-based web application for the classification and recognition of ocular cataract diseases using deep learning (CNN). It provides an easy-to-use interface for users to log in, upload eye images, and receive predictions. The application is designed to assist medical professionals and researchers in identifying cataract-affected eyes.

---

## Features

* User Authentication: Login and signup with validation and CAPTCHA.
* Profile Management: Users can manage profile details and upload profile pictures.
* Disease Diagnosis: Upload ocular images to classify and detect cataract.
* History Tracking: View past diagnoses and reports.
* Database Integration: Stores user information and medical history.
* Deep Learning Model: Uses a CNN-based trained model for cataract recognition.
* Interactive UI: Built with HTML, CSS, and JavaScript for a smooth user experience.

---

## Project Structure

```
ODC/
│-- app.py                # Main Flask app
│-- appy.py, xyz.py       # Helper/test scripts
│-- secret.py             # Secret keys/config (should be hidden in .gitignore)
│-- ocular_disease_BCNN_model_saved/  # Trained deep learning model
│-- static/
│   ├── css/style.css
│   ├── js/captcha.js
│   ├── images/
│   └── profile_pictures/
│-- templates/
│   ├── login.html
│   ├── signup.html
│   ├── home.html
│   ├── dashboard.html
│   ├── diagnose.html
│   ├── profile.html
│   └── history.html
│-- database_ODC.png     
```

---

## Tech Stack

* Frontend: HTML5, CSS3, JavaScript
* Backend: Flask (Python)
* Database: Oracle / SQL
* Machine Learning: Convolutional Neural Network (CNN) with TensorFlow/Keras
* Others: Bootstrap, CAPTCHA validation

---

## Installation & Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/ODC.git
   cd ODC
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # On Windows
   ```

3. Install the required Python packages:

   ```bash
   pip install Flask==2.3.5
   pip install Werkzeug==2.3.7
   pip install Jinja2==3.1.4
   pip install itsdangerous==2.1.2
   pip install click==8.1.7
   pip install gunicorn==21.2.0

   pip install numpy==1.26.5
   pip install pandas==2.1.1
   pip install tensorflow==2.13.0
   pip install keras==2.13.1

   pip install cx_Oracle==8.4.1

   pip install scikit-learn==1.3.2
   pip install Pillow==10.1.0
   pip install opencv-python==4.8.1.78
   ```

4. Run the Flask app:

   ```bash
   python app.py
   ```

5. Open your browser and visit:

   ```
   http://127.0.0.1:5000/
   ```

---

## Database

The application uses an Oracle/SQL database to store:

* User login details
* User profile information
* Diagnosis history

Refer to `database_ODC.png` for the database schema.

---

## Dataset & Model

* Model: CNN trained on ocular cataract dataset
* Saved in: `ocular_disease_BCNN_model_saved/`

---

## Future Improvements

* Deploy application on cloud (Heroku/AWS)
* Enhance model with more eye disease categories
* Add role-based access (Doctor vs Patient)
* Improve UI with modern frontend frameworks

---

## Contributors

* Rexlin Nadar
* Jenica Kodankandath
* Jasmitkaur Mukhtiar
* Tanvi Mhasal

---

## License

This project is for educational purposes (college project).
