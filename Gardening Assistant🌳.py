import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
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
            return data['class'], data['plant_care']
        else:
            return None, None

    except Exception as e:
        st.error(f"An error has occurred: {str(e)}")
        return None, None

# Define class labels
classnames_file = 'class_names.txt'

# Read class names from the text file using list comprehension
with open(classnames_file, 'r') as file:
    class_labels = [line.strip() for line in file]


# Create Streamlit interface
def main():

    st.set_page_config(page_title="Plantify", page_icon=":seedling:", layout="wide")
    # Add a header with a logo or image
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="font-size: 49px;">🌿Plantify🌱</h1>
        </div>
    """, unsafe_allow_html=True)

    
    # Add a sidebar
    st.sidebar.title('Welcome to Your Gardening Companion! 🌼')
    container = st.sidebar.container(border=True)
    container.text("📸 Snap & Detect Plant")
    container.text("🌞 Sunlight Suggestions")
    container.text("💧 Watering Wisdom")
    container.text("🌱 Soil Secrets")
    container.text("🌿 Fertilization Info")
    st.sidebar.write("")
    st.sidebar.subheader("Some good websites to refer for gardening:")
    st.sidebar.page_link("https://www.rhs.org.uk/", label="Royal Horticultural Society", icon = "🏛️", help="Click to visit the RHS website")
    st.sidebar.page_link("https://www.gardeningknowhow.com/", label="Gardening Know How", icon = "🌱", help="Click to visit the Gardening Know How website")
    st.sidebar.page_link("https://www.growveg.com/", label="Grow Veg", icon = "🥕", help="Click to visit the Grow Vegetables website")
    st.sidebar.page_link("https://www.thespruce.com/plants-a-to-z-5116344", label="The Spruce", icon = "🌿", help="Click to visit The Spruce website")


    # Main content area
    st.markdown("""
        <div style="text-align: center;">
            <h2>Welcome to Plantify, your one-stop-shop for all things gardening!</h2>
            <p style="font-size: 16px; color: #666666;">Whether you're a seasoned green thumb or a budding plant enthusiast, our app is designed to help you nurture your leafy friends with the utmost care and attention. With our cutting-edge plant recognition technology and extensive knowledge base, we provide personalized guidance to ensure your plants thrive and flourish. From watering schedules to soil recommendations, sunlight requirements to fertilization tips, we've got you covered.</p>
            <br>        
        </div>
    """, unsafe_allow_html=True)


    # Add a header for the plant recognition section
    st.subheader('Take a photo of your plant and upload it here to see how to take care of it!')

    # File uploader for image
    uploaded_file = st.file_uploader("Upload a photo of just the leaf for accurate predictions.", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:

        # Display the image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', width=400)

        # Make predictions when a button is clicked
        if st.button('Predict'):
            # Add a progress bar
            text = "Analyzing image..."
            progress_bar = st.progress(0, text=text)
            for percent_complete in range(100):
                time.sleep(0.01)  # Simulate waiting time
                progress_bar.progress(percent_complete + 1, text=text)

            # Call prediction function
            predicted_class, plant_care = predict(image)

            # Clear progress bar after completion
            progress_bar.empty()

            if predicted_class and plant_care:
                plant_name = predicted_class.split('__')[0]
                # Display plant care information
                st.markdown(f"## The plant you have uploaded is {plant_name}! Here's how you can take care of your plant!")
                st.write("")  # Add an empty line for better spacing

                # Use columns for a better layout
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Watering Frequency 💧")
                    st.write(f"- {plant_care['water_frequency']}")
                    st.write("")  # Add an empty line for better spacing

                    st.subheader("Sunlight ☀️")
                    st.write(f"- {plant_care['sunlight_requirements']}")
                    st.write("")  # Add an empty line for better spacing

                with col2:
                    st.subheader("Soil Type 🌱")
                    st.write(f"- {plant_care['soil_type']}")
                    st.write("")  # Add an empty line for better spacing

                    st.subheader("Fertilizer 🧪")
                    st.write(f"- {plant_care['fertilization']}")

                st.write("")  # Add an empty line for better spacing 

                if "healthy" in predicted_class:
                    st.header("Your plant looks healthy! Keep up the good work!🌟")
                
                else:
                    st.header("Your plant looks diseased! Please go to the Disease Detection page, to know how to nurse it back to health.😷")
                    c1,c2,c3 = st.columns(3)
                    with c2:
                        st.page_link("./pages/Disease_Diagnosis🩺.py", label = "**Click to diagnose your plant**", icon = "🩺", help = "go to the disease detection page")

            else:
                st.error("An error occurred while predicting the plant type and care instructions. Please try again.")

if __name__ == '__main__':
    main()


# #FOR WITHOUT FASTAPI
# # Load your Keras model
# model = tf.keras.models.load_model('./saved_models/model.h5')

# # Define prediction function
# @st.cache_resource
# def predict(image_data):
#     img = Image.open(image_data)
#     if img.mode == 'RGBA':
#         img = img.convert('RGB')
#     img = img.resize((256, 256))  # Resize image to match input size of the model
#     img_array = tf.keras.preprocessing.image.img_to_array(img)
#     img_array = tf.expand_dims(img_array, axis=0)  # Expand dimensions to match model input shape
#     img_array = img_array / 255.0  # Normalize pixel values
    
#     # Make predictions using your model
#     predictions = model.predict(img_array)
    
#     predicted_class = class_labels[np.argmax(predictions[0])]
#     confidence = round(100 * np.max(predictions[0]), 2)

#     return predicted_class, confidence