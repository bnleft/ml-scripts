"""
Requirements
1. All images with the same tag must be stored in the same folder. This folder must be named like the tag name.
2. Inside each tag folder, there are 3 sub-folders: 'Relevant annotation', 'Irrelevant', and 'Relevant'. Images must be correctly downloaded to each subfolder
3. There are some original images which may have more than one bounding box, the region of interests inside these bounding boxes need to be extracted into sub images
"""

import os
import json
import urllib.request
from PIL import Image

class GlomDatasetGenerator:
    PROJECT_ID = 'clspra3rw017b07xuf95ofdc0'

    def __init__(self, filename):
        self.filename = filename

    def parse_ndjson(self):
        with open(self.filename, 'r') as file:
            return [json.loads(line) for line in file]

    def download_image(self, url, filepath):
        urllib.request.urlretrieve(url, filepath)

    def process_data(self, data):
        for row in data:
            dataset_folder = os.path.join("datasets", "glom")
            tag_folder = os.path.join(dataset_folder, "mesangial_matrix_expansion")
            os.makedirs(tag_folder, exist_ok=True)

            for label in row['projects'][self.PROJECT_ID]['labels']:
                classifications = label['annotations']['classifications']
                for classification in classifications:
                    relevant_value = classification['radio_answer']['value']
                    relevance_folder = os.path.join(tag_folder, relevant_value)
                    os.makedirs(relevance_folder, exist_ok=True)

                    image_filename = row['data_row']['id']
                    image_url = row['data_row']['row_data']
                    image_path = os.path.join(relevance_folder, image_filename)
                    self.download_image(image_url, image_path)

    def generate_dataset(self):
        data = self.parse_ndjson()
        self.process_data(data)
