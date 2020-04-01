import environment_variables
import os

photos_path = os.environ["PHOTOS_PATH"]

def create_photos_path_if_none():
	if not os.path.isdir(photos_path):
		os.mkdir(photos_path)

create_photos_path_if_none()
		