import praw
import os
import time
import asyncio
import random
from datetime import datetime

reddit = praw.Reddit(client_id=os.environ["reddit_id"],
	client_secret=os.environ["reddit_secret"], user_agent=os.environ["reddit_agent"])

def refresh_valid_submissions():
	for submission in reddit.subreddit("gayincest").hot(limit=10000):
		if len(submission.selftext) < max_length and len(submission.selftext) > min_length:
			if "https://" not in submission.selftext:
				valid_submissions.append(submission)

async def get_incest_story(ctx):
	if valid_submissions:
		submission = random.choice(valid_submissions)
		full_submission = "**{}**\n\n{}".format(submission.title, submission.selftext.strip("\t"))
		await ctx.channel.send(full_submission)
	else:
		await ctx.channel.send("Could not fetch submission.")

	time_difference = datetime.now() - cached_time

	#debug
	await ctx.channel.send("Total subs: {}".format(str(len(valid_submissions))))

	if time_difference.days > 0:
		refresh_valid_submissions()
		cached_time = datetime.now()

	#more debug
	if time_difference.minutes > 0:
		refresh_valid_submissions()
		await ctx.channel.send("Refreshed")
		cached_time = datetime.now()

max_length = 1900
min_length = 10
valid_submissions = []
refresh_valid_submissions()
cached_time = datetime.now()