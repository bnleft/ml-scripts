"""
Requirements
1. All images with the same tag must be stored in the same folder. This folder must be named like the tag name.
2. Inside each tag folder, there are 3 sub-folders: 'Relevant annotation', 'Irrelevant', and 'Relevant'. Images must be correctly downloaded to each subfolder
3. There are some original images which may have more than one bounding box, the region of interests inside these bounding boxes need to be extracted into sub images

Edge Cases
1. Long file names
2. File names with illegal characters

"""

import os
import json
import urllib.request
from urllib.error import URLError
import socket
import labelbox
from uuid import uuid4
from PIL import Image, ImageDraw


def download_image(url, filepath, timeout=30):
    try:
        response = urllib.request.urlopen(url, timeout=timeout)
        with open(filepath, 'wb') as f:
            f.write(response.read())
        print(f"Download successful: {filepath}")
    except URLError as e:
        print(f"Failed to download {url}. URLError: {e.reason}")
    except socket.timeout:
        print(f"Request timed out: {url}. Try increasing the timeout value.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def add_bounding_box_to_image(image_path, box, save_path):
    with Image.open(image_path) as img:
        print('downloading sub image:', image_path)

        draw = ImageDraw.Draw(img)

        top = box['top']
        left = box['left']
        height = box['height']
        width = box['width']

        bottom_right = (left + width, top + height)

        draw.rectangle([left, top, *bottom_right], width=2)

        img.save(save_path)


def parse_ndjson(filename):
    with open(filename, 'r') as file:
        return [json.loads(line) for line in file]


class GlomDatasetGenerator:

    def __init__(self, api_key):
        self.project_id = 'clspra3rw017b07xuf95ofdc0'
        self.task_id = 'clt9eyvlh0acx07wt3pk65rxy'
        self.client = labelbox.Client(api_key)
        self.dataset_folder = os.path.join("datasets", "glom")
        self.map_json = f"{self.dataset_folder}/map.json"

        os.makedirs(self.dataset_folder, exist_ok=True)
        with open(self.map_json, 'x') as file:
            json.dump({}, file)

    def generate_spec(self, data_file):
        try:
            export_task = labelbox.ExportTask.get_task(self.client, task_id=self.task_id)
            export_task.get_stream(converter=labelbox.FileConverter(file_path=data_file)).start()
        except Exception as e:
            print(f"Error downloading data, possibly due to invalid API key. Error: {e}")

    def process_data(self, data):
        for row in data:
            tag_value = None

            for field in row['metadata_fields']:
                if field['schema_name'] == 'tag':
                    tag_value = field['value']

            if tag_value is None:
                continue

            tag_value = tag_value.replace(" ", "_")

            tag_folder = os.path.join(self.dataset_folder, tag_value)
            os.makedirs(tag_folder, exist_ok=True)

            image_url = row['data_row']['row_data']

            for label in row['projects'][self.project_id]['labels']:
                file_extension = row['media_attributes']['mime_type'].split("/")[-1]
                image_name = os.path.splitext(row['data_row']['external_id'])[0]
                image_generated_id = self.generate_image_id(image_name)

                # original image
                classification = label['annotations']['classifications'][0]
                relevant_value = classification['radio_answer']['value']
                relevance_folder = os.path.join(tag_folder, relevant_value)
                os.makedirs(relevance_folder, exist_ok=True)

                image_filename = f"{image_generated_id}.{file_extension}"
                image_path = os.path.join(relevance_folder, image_filename)
                download_image(image_url, image_path)

                print('downloading image:', image_path)

                if not os.path.exists(image_path):
                    continue
                    
                # sub images with each bounding box
                for index, object in enumerate(label['annotations']['objects']):
                    sub_image_filename = f"{image_generated_id}-{index + 1}.{file_extension}"
                    sub_image_path = os.path.join(relevance_folder, sub_image_filename)
                    download_image(image_url, sub_image_path)

                    box = object['bounding_box']

                    add_bounding_box_to_image(sub_image_path, box, sub_image_path)

    def generate_image_id(self, image_name: str) -> str:
        image_id = str(uuid4())

        with open(self.map_json, 'r+') as file:
            data = json.load(file)
            data[image_id] = image_name
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

        return image_id

    def generate_dataset(self, data_file):
        data = parse_ndjson(data_file)
        self.process_data(data)
