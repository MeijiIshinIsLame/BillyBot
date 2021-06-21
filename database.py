import os
import sqlite3
from datetime import datetime
from pytz import timezone
import discord

import environment_variables
import images
import helpers

photos_path = os.environ["PHOTOS_PATH"]
pic_ext = ['.jpg','.png','.jpeg']
db_file = '../database/hentai.db'

#checks if running for the first time.
#used to build the db if it is
#entries per line seperated by \t
def initial_startup():
	if os.path.isfile(db_file):
		pass
	else:
		helpers.create_file(db_file)
		raw_entries = []
		with open("bbotdb.txt", 'r') as f:
			raw_entries = f.readlines()
		create_db_from_backup(raw_entries)

def create_db_from_backup(raw_entries):
	for line in raw_entries:
		static_id, static_name, url, author, today_date, last_updated = line.split("\t")

		#postgres fucked me over, needs to be converted to the proper format
		#hence I do this shit
		today_date = datetime.strptime(today_date, "%Y-%m-%d").strftime("%m-%d-%Y")

		#and last_updated has a space and newline for some fking reason
		last_updated = last_updated.strip("\n")
		last_updated = last_updated[:-1] 
		last_updated = datetime.strptime(last_updated, "%Y-%m-%d %I:%M:%S").strftime("%m-%d-%Y %I:%M:%S")

		add_image_to_db_manually(static_id, static_name, url, author, today_date, last_updated)
		print("added " + static_name)

def connect_to_db():
	conn = sqlite3.connect(database=db_file)
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
				VALUES (?, ?, ? , ?, ?, ?)""")
	c.execute(query, params)

	c.execute("""CREATE TABLE IF NOT EXISTS users(author TEXT PRIMARY KEY, entrycount INTEGER)""")
	params = (str(author),)
	#this incriments after. TODO: Update so that it works in one statement, and do it for del as well.
	query = ("""INSERT OR IGNORE INTO users (author, entrycount) VALUES (?, 0)""")
	c.execute(query, params)

	c.execute("UPDATE users SET entrycount = entrycount + 1 WHERE author=?", params)
	
	conn.commit()
	conn.close()

def add_image_to_db_manually(static_id, static_name, url, author, today_date, last_updated):
	conn, c = connect_to_db()

	c.execute("""CREATE TABLE IF NOT EXISTS images(staticID TEXT, 
													 staticName TEXT,
													 url TEXT,
													 author TEXT,
													 insertDate DATE, 
													 insertTime TIMESTAMP)""")

	params = (static_id, static_name, url, author, today_date, last_updated)
	query = ("""INSERT INTO images (staticID, staticName, url, author, insertDate, insertTime)
				VALUES (?, ?, ? , ?, ?, ?)""")
	c.execute(query, params)

	c.execute("""CREATE TABLE IF NOT EXISTS users(author TEXT PRIMARY KEY, entrycount INTEGER)""")
	params = (str(author),)
	#this incriments after. TODO: Update so that it works in one statement, and do it for del as well.
	query = ("""INSERT OR IGNORE INTO users (author, entrycount) VALUES (?, 0)""")
	c.execute(query, params)

	c.execute("UPDATE users SET entrycount = entrycount + 1 WHERE author=?", params)
	
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
		query = ("""INSERT INTO users (author, entrycount) VALUES (?, ?)""")
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
				c.execute("DELETE FROM images WHERE staticName=?", (filename,))
				images_deleted += 1
				print(filename, "deleted")

	#clean images directory
	files = os.listdir(photos_path)
	for filename in files:
		for ext in pic_ext:
			if filename.endswith(ext):
				c.execute("SELECT staticName FROM images WHERE staticName=?", (filename,))
				if c.rowcount == 0:
					images.delete_image(filename)
					images_deleted += 1
					print(filename, "deleted")
	conn.commit()
	conn.close()
	return images_deleted, images_recovered

def delete_entry(image_id):
	conn, c = connect_to_db()

	c.execute("SELECT author FROM images WHERE staticID=?", (image_id,))
	row = c.fetchone()
	c.execute("UPDATE users SET entrycount = entrycount - 1 WHERE author=?", row)
	c.execute("DELETE FROM users WHERE entrycount=0") #delete those mfers who do not contribute

	c.execute("SELECT staticName FROM images WHERE staticID=?", (image_id,))
	row = c.fetchone()
	filename = row[0]
	images.delete_image(filename)

	c.execute("DELETE FROM images WHERE staticID=?", (image_id,))

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
	c.execute("SELECT staticID, staticName, author, insertDate FROM images WHERE staticID=?", (image_id,))
	row = c.fetchone()
	conn.commit()
	conn.close()
	return row

def fetch_specific_entry_from_author(author_id):
	conn, c = connect_to_db()
	c.execute("SELECT staticID, staticName, author, insertDate FROM images WHERE author=? ORDER BY RANDOM() LIMIT 1", (author_id,))
	row = c.fetchone()
	conn.commit()
	conn.close()
	print(row)
	print(author_id)
	return row

def count_hentai(user_id=None):
	conn, c = connect_to_db()
	if user_id:
		c.execute("SELECT * FROM images WHERE author=?", (user_id,))
	else:
		c.execute("SELECT * FROM images")
	total = c.rowcount
	conn.commit()
	conn.close()
	return total

def get_leaderboard():
	conn, c = connect_to_db()
	c.execute("SELECT * FROM users ORDER BY entrycount DESC LIMIT 10")
	rows = c.fetchall()
	conn.commit()
	conn.close()
	return rows
