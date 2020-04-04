import praw
import os
import time
import asyncio
import random

reddit = praw.Reddit(client_id=os.environ["reddit_id"],
	client_secret=os.environ["reddit_secret"], user_agent=os.environ["reddit_agent"])

async def get_incest_story():
	max_length = 1900
	min_length = 10
	valid_submissions = []

	for submission in reddit.subreddit("gayincest").hot(limit=100000):
		if len(submission.selftext) < max_length and len(submission.selftext) > min_length:
			if "https://imgur.com/" not in full_submission:
				valid_submissions.append(submission)

	if valid_submissions:
		full_submission = "**{}**\n\n{}".format(submission.title, submission.selftext.strip("\t"))
		return full_submission
	else:
		return "Could not fetch submission."