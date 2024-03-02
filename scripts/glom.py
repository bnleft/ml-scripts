"""
Requirements
1. All images with the same tag must be stored in the same folder. This folder must be named like the tag name.
2. Inside each tag folder, there are 3 sub-folders: 'Relevant annotation', 'Irrelevant', and 'Relevant'. Images must be correctly downloaded to each subfolder
3. There are some original images which may have more than one bounding box, the region of interests inside these bounding boxes need to be extracted into sub images
"""

import os
import json
import urllib.request
import labelbox


def download_image(url, filepath):
    urllib.request.urlretrieve(url, filepath)


def parse_ndjson(filename):
    with open(filename, 'r') as file:
        return [json.loads(line) for line in file]


class GlomDatasetGenerator:
    PROJECT_ID = 'clspra3rw017b07xuf95ofdc0'
    TASK_ID = 'clt9eyvlh0acx07wt3pk65rxy'

    def __init__(self, api_key):
        self.client = labelbox.Client(api_key)

    def generate_spec(self, data_file):
        try:
            export_task = labelbox.ExportTask.get_task(self.client, task_id=self.TASK_ID)
            export_task.get_stream(converter=labelbox.FileConverter(file_path=data_file)).start()
        except:
            print("Error downloading data, possibly due to invalid API key.")

    def process_data(self, data):
        for row in data:
            dataset_folder = os.path.join("datasets", "glom")

            tag_value = None

            for field in row['metadata_fields']:
                if field['schema_name'] == 'tag':
                    tag_value = field['value']

            print(tag_value)
            if tag_value is None:
                continue

            tag_value = tag_value.replace(" ", "_")

            tag_folder = os.path.join(dataset_folder, tag_value)
            os.makedirs(tag_folder, exist_ok=True)

            for label in row['projects'][self.PROJECT_ID]['labels']:
                classifications = label['annotations']['classifications']
                for classification in classifications:
                    relevant_value = classification['radio_answer']['value']
                    relevance_folder = os.path.join(tag_folder, relevant_value)
                    os.makedirs(relevance_folder, exist_ok=True)

                    file_extension = row['media_attributes']['mime_type'].split("/")[-1]
                    image_name = os.path.splitext(row['data_row']['external_id'])[0]
                    image_filename = image_name + '-' + row['data_row']['id'] + '.' + file_extension
                    image_url = row['data_row']['row_data']

                    image_path = os.path.join(relevance_folder, image_filename)
                    download_image(image_url, image_path)

    def generate_dataset(self, data_file):
        data = parse_ndjson(data_file)
        self.process_data(data)
