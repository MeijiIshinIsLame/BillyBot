import praw
import os
import time
import asyncio

reddit = praw.Reddit(client_id=os.environ["reddit_id"],
	client_secret=os.environ["reddit_secret"], user_agent=os.environ["reddit_agent"])

async def get_incest_story():
	submission = reddit.subreddit("gayincest").random()
	max_length = 2000
	min_length = 10
	i = 0
	while i < 1500:
		full_submission = "**{}**\n\n{}".format(submission.title, submission.selftext.strip("\t"))
		if len(full_submission) < max_length and len(full_submission) > min_length:
			return full_submission
		i += 1
	return "Could not fetch submission."