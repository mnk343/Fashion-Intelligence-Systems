from flask import Flask
from flask import request
import pymongo
from pymongo import MongoClient
from datetime import datetime
import json
from flask import jsonify
app = Flask(__name__)

from keras.preprocessing import image
from keras.layers import GlobalAveragePooling2D, Dense, Dropout
from keras.models import Model
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
import numpy as np
import tensorflow as tf
import shutil
import requests

base_model = tf.keras.applications.MobileNet(
    include_top=False,
    weights="imagenet",
    input_tensor=None,
    input_shape=None,
    pooling=None,
    classes=2,
    classifier_activation="softmax",
)

img_size = 224
filepath = 'MobileNet_pretrained_model_full.h5'

x = base_model.output
x = Dense(128)(x)
x = GlobalAveragePooling2D()(x)
predictions = Dense(2, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)
model.load_weights(filepath)
inputShape = (img_size,img_size) # Assumes 3 channel image

@app.route('/')
def classify():
    args = request.args
    image_url = ""
    data = {}
    if ( len(args.getlist('image_url')) > 0 ):
        image_url = args.getlist('image_url')[0]
        data["image_url"] = image_url
    else :
        return jsonify({"status": "Image URL missing"}), 400    
    
    # test that url here
    url = "https://images-na.ssl-images-amazon.com/images/I/916q4pTEEaL._UY695_.jpg"

    response = requests.get(url, stream=True)
    with open('img.png', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

    image = load_img('img.png', target_size=inputShape)
    image = img_to_array(image)   # shape is (224,224,3)
    image = np.expand_dims(image, axis=0)  # Now shape is (1,224,224,3)
    image = image/255.0
    preds = model.predict(image)
    print(preds)

    return jsonify({"status": "Added successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)