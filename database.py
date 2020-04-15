import os
import psycopg2
from datetime import datetime
from pytz import timezone
import discord

import environment_variables
import images
import helpers

photos_path = os.environ["PHOTOS_PATH"]
pic_ext = ['.jpg','.png','.jpeg']
ssl_cert_path = "client-cert.pem"
ssl_key_path = "client-key.pem"
ssl_root_cert_path = "server-ca.pem"

def connect_to_db():
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
	return conn, conn.cursor()

def add_image_to_db(image_filename, message):	
	conn, c = connect_to_db()

	c.execute("""CREATE TABLE IF NOT EXISTS images(staticID TEXT, 
													 staticName TEXT,
													 url TEXT,
													 author TEXT,
													 insertDate DATE, 
													 insertTime TIMESTAMP)""")
	static_id = image_filename.split(".")[0]
	static_name = image_filename
	url = message.attachments[0].url
	author = message.author.id
	today_date = datetime.now(timezone('US/Hawaii')).date().strftime("%m-%d-%Y")
	last_updated = datetime.now(timezone('US/Hawaii')).strftime("%m-%d-%Y %I:%M:%S")

	params = (static_id, static_name, url, author, today_date, last_updated)
	query = ("""INSERT INTO images (staticID, staticName, url, author, insertDate, insertTime)
				VALUES (%s, %s, %s , %s, %s, %s)""")
	c.execute(query, params)

	c.execute("""CREATE TABLE IF NOT EXISTS users(author TEXT PRIMARY KEY, entrycount INTEGER)""")
	params = (str(author),)
	#this incriments after. TODO: Update so that it works in one statement, and do it for del as well.
	query = ("""INSERT INTO users (author, entrycount) VALUES (%s, 0) ON CONFLICT (author) DO NOTHING""")
	c.execute(query, params)

	c.execute("UPDATE users SET entrycount = entrycount + 1 WHERE author=%s", params)
	
	conn.commit()
	conn.close()

def create_authors_db():
	conn, c = connect_to_db()
	c.execute("""CREATE TABLE IF NOT EXISTS users(author TEXT PRIMARY KEY, entrycount INTEGER)""")

	userlist = []

	c.execute("SELECT author FROM images")
	rows = c.fetchall()

	for row in rows:
		author = row[0]
		if author not in userlist:
			userlist.append(author)
			
	for author in userlist:
		entrycount = count_hentai(author)
		params = (author, entrycount)
		query = ("""INSERT INTO users (author, entrycount) VALUES (%s, %s) ON CONFLICT (author) DO NOTHING""")
		c.execute(query, params)
	
	conn.commit()
	conn.close()

def sync_db():
	images_recovered = 0
	images_deleted = 0

	conn, c = connect_to_db()
	c.execute("SELECT staticName, url FROM images")
	image_database = c.fetchall()

	#clean database
	for row in image_database:
		filename = row[0]
		url = row[1]

		full_image_path = os.path.join(photos_path, filename)
		if not os.path.isfile(full_image_path):
			try:
				images.save_image(url, filename=filename)
				images_recovered += 1
				print(filename, "recovered")
			except Exception as e:
				print(e)
				c.execute("DELETE FROM images WHERE staticName=%s", (filename,))
				images_deleted += 1
				print(filename, "deleted")

	#clean images directory
	files = os.listdir(photos_path)
	for filename in files:
		for ext in pic_ext:
			if filename.endswith(ext):
				c.execute("SELECT staticName FROM images WHERE staticName=%s", (filename,))
				if c.rowcount == 0:
					images.delete_image(filename)
					images_deleted += 1
					print(filename, "deleted")
	conn.commit()
	conn.close()
	return images_deleted, images_recovered

def delete_entry(image_id):
	conn, c = connect_to_db()

	c.execute("SELECT author FROM images WHERE staticID=%s", (image_id,))
	row = c.fetchone()
	c.execute("UPDATE users SET entrycount = entrycount - 1 WHERE author=%s", row)
	c.execute("DELETE FROM users WHERE entrycount=0") #delete those mfers who do not contribute

	c.execute("SELECT staticName FROM images WHERE staticID=%s", (image_id,))
	row = c.fetchone()
	filename = row[0]
	images.delete_image(filename)

	c.execute("DELETE FROM images WHERE staticID=%s", (image_id,))

	conn.commit()
	conn.close()

def fetch_random_entry():
	conn, c = connect_to_db()
	c.execute("SELECT staticID, staticName, author, insertDate FROM images ORDER BY RANDOM() LIMIT 1")
	row = c.fetchone()
	conn.commit()
	conn.close()
	return row

def fetch_specific_entry(image_id):
	conn, c = connect_to_db()
	c.execute("SELECT staticID, staticName, author, insertDate FROM images WHERE staticID=%s", (image_id,))
	row = c.fetchone()
	conn.commit()
	conn.close()
	return row

def count_hentai(user_id=None):
	conn, c = connect_to_db()
	if user_id:
		c.execute("SELECT * FROM images WHERE author=%s", (user_id,))
	else:
		c.execute("SELECT * FROM images")
	total = c.rowcount
	conn.commit()
	conn.close()
	return total

def get_leaderboard():
	embed = discord.Embed(title="**Top 10 Hentai Patrons**")
	conn, c = connect_to_db()
	c.execute("SELECT * FROM users ORDER BY entrycount DESC LIMIT 10")
	rows = c.fetchall()

	for entry in rows:
		embed.add_field(name=helpers.make_mention_object_by_id(entry[0]), value="{} entries".format(entry[1]), inline=True)

	conn.commit()
	conn.close()
	return embed



def create_ssl_certs():
	with open(ssl_cert_path, 'w+') as f:
		f.write(os.environ["SSL_CERT"])

	with open(ssl_key_path, 'w+') as f:
		f.write(os.environ["SSL_KEY"])

	with open(ssl_root_cert_path, 'w+') as f:
		f.write(os.environ["SSL_ROOT_CERT"])

def ssl_certs_exist():
	return os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path) and os.path.exists(ssl_root_cert_path)

#create_authors_db()