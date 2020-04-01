import requests
import os
import random
from PIL import Image

import environment_variables

pic_ext = ['.jpg','.png','.jpeg']
#photos_path = os.path.join(os.getcwd(), "photos")
photos_path = os.environ["PHOTOS_PATH"]

def save_image(url, filename=None):
	for ext in pic_ext:
		if url.endswith(ext):
			request = requests.get(url)

			if request.status_code == 200:
				if filename:
					with open(os.path.join(photos_path, filename), 'wb') as f:
						f.write(request.content)
				else:
					filename = str(get_last_image()  + 1)
					filename += ext
					with open(os.path.join(photos_path, filename), 'wb') as f:
						f.write(request.content)
				return filename

def delete_image(filename):
	full_image_path = os.path.join(photos_path, filename)
	os.remove(full_image_path)

def image_too_small(filename):
	image_path = os.path.join(photos_path, filename)
	image = Image.open(image_path)
	width, height = image.size
	return width <= 400 and height <= 400

def get_last_image():
	files = os.listdir(photos_path)
	file_names = []

	for file in files:
		for ext in pic_ext:
			if file.endswith(ext):
				file_names.append(int(file.strip(ext)))

	if len(file_names) > 0:
		file_names = sorted(file_names)
		return file_names[-1]
	else:
		return 0