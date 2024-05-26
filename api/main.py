from fastapi import FastAPI, File, UploadFile
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
import json
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)


MODEL = tf.keras.models.load_model('saved_models/model.h5')

classnames_file = '../class_names.txt'

# Read class names from the text file using list comprehension
with open(classnames_file, 'r') as file:
    CLASS_NAMES = [line.strip() for line in file]

with open('../data/counter_measures.json', 'r') as file:
    countermeasures_dict = json.load(file)

with open('../data/plant_care_data.json', 'r') as f:
    plant_care_instructions = json.load(f)

with open('../data/causes_of_disease.json', 'r') as f:
    causes_of_disease = json.load(f)


def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

def preprocess_image(image: Image.Image) -> np.ndarray:
    if image.mode == 'RGBA':
        image = image.convert('RGB')

    image = image.resize((256, 256))                                    # Resize image to match input size of the model
    image_array = tf.keras.preprocessing.image.img_to_array(image)      # Convert to array
    image_array = tf.expand_dims(image_array, axis=0)                   # Expand dimensions to match model input shape
    image_array = image_array / 255.0                                   # Normalize pixel values

    return image_array
     

@app.get("/ping")
async def ping():
    return "Hello, I am here!"

@app.post("/predict")
async def predict(
    file : UploadFile = File(...)
):
    image = Image.open(BytesIO(await file.read()))
    image_array = preprocess_image(image)

    predictions = MODEL.predict(image_array)

    predicted_class = CLASS_NAMES[np.argmax(predictions[0])]
    confidence = np.max(predictions[0])

    plant_name = predicted_class.split('__')[0]

    countermeasures = countermeasures_dict.get(predicted_class, ["No countermeasure information available."])
    plant_care = plant_care_instructions.get(plant_name, ["No plant care information available."])
    causes = causes_of_disease.get(predicted_class, ["No information available."])


    return {
        'class': predicted_class,
        'confidence': float(confidence),
        'countermeasures': countermeasures,
        'plant_care': plant_care,
        'causes': causes,

    }

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port = 8000)