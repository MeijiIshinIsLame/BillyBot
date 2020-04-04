import praw
import os

reddit = praw.Reddit(client_id=os.environ["reddit_id"],
	client_secret=os.environ["reddit_secret"], user_agent=os.environ["reddit_agent"])

def get_incest_story():
	submission = reddit.subreddit("gayincest").random()
	while True:
		full_submission = "**{}**\n\n{}".format(submission.title, submission.selftext.strip("\t"))
		if full_submission.len() < 2000:
			break
	return full_submission