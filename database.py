import os
import psycopg2
from datetime import datetime
from pytz import timezone

import environment_variables

pic_ext = ['.jpg','.png','.jpeg']
ssl_cert_path = "client-cert.pem"
ssl_key_path = "client-key.pem"
ssl_root_cert_path = "server-ca.pem"

def add_image_to_db(image_filename, message):
	if not ssl_certs_exist():
		create_ssl_certs()

	conn = psycopg2.connect(database=str(os.environ["DB_NAME"]),
							user=str(os.environ["DB_USERNAME"]),
							password=str(os.environ["DB_PASSWORD"]),
							host=str(os.environ["DB_HOSTNAME"]),
							port=str(os.environ["DB_PORT"]),
							sslcert=ssl_cert_path,
							sslmode=str(os.environ["SSL_MODE"]),
							sslrootcert=ssl_root_cert_path,
							sslkey=ssl_key_path)
	c = conn.cursor()
	c.execute("""CREATE TABLE IF NOT EXISTS images(staticID TEXT, 
													 staticName TEXT,
													 url TEXT,
													 author TEXT
													 insertDate DATE, 
													 insertTime TIMESTAMP)""")
	static_id = "test1"
	static_name = "test2"
	url = "test3"
	author = "test4"
	today_date = datetime.now(timezone('US/Hawaii')).date().strftime("%m-%d-%Y")
	last_updated = datetime.now(timezone('US/Hawaii')).strftime("%m-%d-%Y %I:%M:%S")

	params = (static_id, static_name, url, author, today_date, last_updated)
	query = ("""INSERT INTO images (staticID, staticName, url, author, insertDate, insertTime)
				VALUES (%s, %s, %s , %s, %s, %s)""")
	c.execute(query, params)
	conn.commit()
	conn.close()

def create_ssl_certs():
	with open(ssl_cert_path, 'w+') as f:
		f.write(os.environ["SSL_CERT"])

	print(os.environ["SSL_CERT"])

	with open(ssl_key_path, 'w+') as f:
		f.write(os.environ["SSL_KEY"])

	print(os.environ["SSL_KEY"])

	with open(ssl_root_cert_path, 'w+') as f:
		f.write(os.environ["SSL_ROOT_CERT"])

	print(os.environ["SSL_ROOT_CERT"])

def ssl_certs_exist():
	return os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path) and os.path.exists(ssl_root_cert_path)