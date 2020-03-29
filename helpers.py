import random

pic_ext = ['.jpg','.png','.jpeg']

def is_image(link):
	for ext in pic_ext:
		if link.endswith(ext):
			return True
	return False

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
