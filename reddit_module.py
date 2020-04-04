import praw
import os

reddit = praw.Reddit(client_id=os.environ["reddit_id"],
	client_secret=os.environ["reddit_secret"], user_agent=os.environ["reddit_agent"])

def get_incest_story():
	submission = reddit.subreddit("gayincest").random()
	max_length = 2000
	min_length = 15
	i = 0
	while True:
		full_submission = "**{}**\n\n{}".format(submission.title, submission.selftext.strip("\t"))
		if i == 10:
			return "Could not fetch submission."
		if len(full_submission) < max_length and len(full_submission) > min_length:
			break
	return full_submission