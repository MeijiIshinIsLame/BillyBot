import random
import environment_variables
import os

photos_path = os.environ["PHOTOS_PATH"]
pic_ext = ['.jpg','.png','.jpeg']

def is_image(link):
	for ext in pic_ext:
		if link.endswith(ext):
			return True
	return False

def make_mention_object_by_id(author_id):
	return "<@{}>".format(author_id)

def format_hentai_entry(row):
	image_attachment = row[1]
	entry_no = row[0]
	user = make_mention_object_by_id(row[2])
	add_date = row[3].strftime("%m-%d-%Y")

	return image_attachment, entry_no, user, add_date

def get_random_save_message():
	save_messages = ["Thanks u fkng degenerate",
					 "Nice one simp.",
					 "LOL fking loser.",
					 "Nice.",
					 "AMAZIN!",
					 "Nice one loser.",
					 "Permission to coom, commander?",
					 "Have a nice coom sesh.",
					 "Somebody fking kill me.",
					 "COOM SESH.",
					 "Are u ready to coom?",
					 "Enter the cum zone.",
					 "Idk what to say i'm rly disappointed in u son.",
					 "Kill urself tbh.",
					 "Nice one u faka.",
					 "I'M COOOO0000OOMING!!!!!"]
	return random.choice(save_messages)

def get_help_msg():
	help_msg = """Hello Billy Boys :)

**Commands:**
`$hentai (optional number): Pulls up a hentai entry in the database (Only useable in the hentai channel)`

`$del (entry number): Deletes a hentai entry.`

`$counthentai (Optional mention): Counts hentai entries in total or per user.`

`$gayincest: pulls up a random gay incest story.`

> Q: How do I add hentai?
Simply be in the hentai channel, and drop an image. Images under 400x400 are not supported, and neither are gifs."""
	return help_msg