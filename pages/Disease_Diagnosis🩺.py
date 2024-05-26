import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import io
import time
import requests

# FOR FASTAPI SUPPORT
def predict(image):
    if image.mode == 'RGBA':
        image = image.convert('RGB')
        
    try:
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        img_byte_arr = img_byte_arr.getvalue()

        # Send image to FastAPI endpoint
        files = {'file': img_byte_arr}
        response = requests.post('http://localhost:8000/predict', files=files)

        if response.status_code == 200:
            data = response.json()
            return data['class'], data['confidence'], data['causes'], data['countermeasures']
        
        else:
            return None, None, None, None
    
    except Exception as e:
        st.error(f"An error has occurred: {str(e)}")


# Define class labels
classnames_file = 'class_names.txt'

# Read class names from the text file using list comprehension
with open(classnames_file, 'r') as file:
    class_labels = [line.strip() for line in file]


# Create Streamlit interface
def main():
    st.set_page_config(page_title="Disease Diagnosis🩺", layout="wide")

    # Define sidebar options
    st.sidebar.title('Disease Diagnosis🩺')
    st.sidebar.markdown('''
    This page is designed to help you detect diseases in plants. Simply upload an image of a plant and the model will predict whether it is healthy or diseased. It provides valuable information about the

    - **Predicted Class:** The predicted class of the plant (healthy or diseased).
    - **Confidence:** The confidence level of the prediction.
    - **Countermeasures:** Countermeasures to take if the plant is diseased.

    Feel free to explore and get gardening advice!
    ''')
    st.title('Disease Diagnosis🩺')
    st.subheader('Upload an image of a plant to check if it is healthy or diseased.')

    # File uploader for image
    uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', width=500)

        # Make predictions when a button is clicked
        if st.button('Predict'):
            # Call prediction function
            predicted_class, confidence, causes, countermeasures = predict(image)

            # Display prediction
            st.success(f'Predicted Class: {predicted_class}')
            st.success(f'Confidence🎯: {confidence}%')

            if 'healthy' in predicted_class:
                st.markdown(f"## Your plant is diagnosed as {predicted_class}. It is healthy!")
            else:
                st.markdown(f"## Your plant is diagnosed as {predicted_class} 😷")

            st.write("")

            with st.container(border=True):
                st.subheader(f"The causes for this are🔍: ")
                for cause in causes:
                    st.write(f"- {cause}")

            st.write("")

            with st.container(border=True):
                st.subheader(f"Countermeasures for {predicted_class}🛑:")
                for countermeasure in countermeasures:
                    st.write(f"- {countermeasure}")

    st.divider()

    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None

    # Selectbox and Button for Countermeasures
    selected_class = st.selectbox('Select a class:', class_labels, key='class_selector')
    find_countermeasures = st.button('Find Countermeasures for a Specific Class🔍')

    if find_countermeasures:
        st.session_state.selected_class = selected_class

    if st.session_state.selected_class:
        selected_class = st.session_state.selected_class

        # READ CAUSES OF DISEASE AND PRINT IT
        with open('./data/causes_of_disease.json', 'r') as f:
            causes_of_disease = json.load(f)
        
        with st.container(border=True):
            st.subheader(f"The causes for this are🔍: ")
            causes = causes_of_disease.get(selected_class, ["No information available."])
            for cause in causes:
                st.write(f"- {cause}")

        # READ COUNTERMEASURES AND PRINT IT
        with open('./data/counter_measures.json', 'r') as file:
            countermeasures_dict = json.load(file)

        with st.container(border=True):
            st.subheader(f"Countermeasures for {selected_class}🛑:")
            countermeasures = countermeasures_dict.get(selected_class, ["No countermeasure information available."])
            for countermeasure in countermeasures:
                st.write(f"- {countermeasure}")

if __name__ == '__main__':
    main()
