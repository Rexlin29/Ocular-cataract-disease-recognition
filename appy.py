from datetime import datetime
from flask import Flask, flash, redirect, request, jsonify, session
from flask_cors import CORS
import cx_Oracle
import tensorflow as tf
from app import get_db_connection, get_user_id
from tensorflow_probability import layers as tfp_layers
from PIL import Image
import numpy as np
import io
import cv2

app = Flask(__name__)
CORS(app)

def get_db_connection():
    dsn = cx_Oracle.makedsn('localhost', 1521, service_name='XE')
    return cx_Oracle.connect(user='mp5', password='odc', dsn=dsn)

# Define the custom loss function
def negative_log_likelihood(y_true, y_pred):
    return -y_pred.log_prob(y_true)

# Register custom layers and loss function
custom_objects = {
    'Conv2DReparameterization': tfp_layers.Convolution2DReparameterization,
    'negative_log_likelihood': negative_log_likelihood
}

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

# Load the model
try:
    with tf.keras.utils.custom_object_scope(custom_objects):
        model = tf.keras.models.load_model(r"C:\Users\rexli\OneDrive\Desktop\ODC\ocular_disease_BCNN_model_saved")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Define labels for prediction
labels = ["Cataract", "Normal"]  # Replace with actual condition labels

# Define the probability estimation function
def import_and_predict_bayes_experiment3(image):
    # Preprocess the image
    img = np.array(image.resize((75, 75))) / 255.0  # Resize and normalize image
    img = img[np.newaxis, ...]  # Add batch dimension

    # Create an empty array to store probabilities for each prediction
    predicted_probabilities = np.empty((300, len(labels)))

    # Run multiple predictions for uncertainty estimation
    for i in range(300):
        prediction = model(img)  # Get model output
        if hasattr(prediction, 'mean'):
            predicted_probabilities[i] = prediction.mean().numpy()[0]  # Use mean if it's a distribution
        else:
            predicted_probabilities[i] = prediction.numpy()[0]  # Directly use numpy for non-distribution outputs

    # Calculate average probability and confidence intervals
    average_estimate = np.mean(predicted_probabilities, axis=0) * 100
    pct_2p5 = np.percentile(predicted_probabilities, 2.5, axis=0) * 100
    pct_97p5 = np.percentile(predicted_probabilities, 97.5, axis=0) * 100

    # Format output text
    result_text = f"Most likely Ocular Condition: {labels[np.argmax(average_estimate)]} - {round(average_estimate.max(), 2)}%\n"
    for i, label in enumerate(labels):
        result_text += f"\n{label}: Average estimate = {round(average_estimate[i], 2)}%, 97.5% CI = {round(pct_2p5[i], 2)} - {round(pct_97p5[i], 2)}%\n"
    
    return result_text

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    try:
        img = Image.open(io.BytesIO(file.read()))
        result_text = import_and_predict_bayes_experiment3(img)  # Predict result

        # Save the diagnosis result to the database
        user_id = get_user_id()  
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO diagnosis_history (user_id, diagnosis_result, diagnosis_date) VALUES (:user_id, :diagnosis_result, :diagnosis_date)',
                {'user_id': user_id, 'diagnosis_result': result_text, 'diagnosis_date': datetime.now()}
            )
            conn.commit()
        except Exception as e:
            print(f'Error saving diagnosis: {e}')
            return jsonify({'error': 'Database error'}),500
        finally:
            cursor.close()
            conn.close()

        return jsonify({'result': result_text})  # Return JSON response with the result

    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({'error': 'Prediction error'}),500

if __name__ == '__main__':
    app.run(host="127.0.0.1", port="5001", debug=True)
