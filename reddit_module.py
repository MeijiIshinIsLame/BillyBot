import praw
import os
import time
import asyncio
import random
from datetime import datetime

max_length = 1900
min_length = 10

class RedditBot:
	def __init__(self):
		self.cached_time = datetime.now()
		self.reddit = praw.Reddit(client_id=os.environ["reddit_id"],
			client_secret=os.environ["reddit_secret"], user_agent=os.environ["reddit_agent"])
		self.valid_submissions = []

	def refresh_valid_submissions(self):
		for submission in self.reddit.subreddit("gayincest").hot(limit=10000):
			if len(submission.selftext) in range(min_length, max_length):
				if "https://" not in submission.selftext:
					self.valid_submissions.append(submission)

	async def get_incest_story(self, ctx):
		if self.valid_submissions:
			submission = random.choice(self.valid_submissions)
			full_submission = "**{}**\n\n{}".format(submission.title, submission.selftext.strip("\t"))
			await ctx.channel.send(full_submission)
		else:
			await ctx.channel.send("Could not fetch submission.")

		time_difference = datetime.now() - self.cached_time

		#debug
		await ctx.channel.send("Total subs: {}".format(str(len(self.valid_submissions))))

		if time_difference.days > 0:
			self.refresh_valid_submissions()
			self.cached_time = datetime.now()

		#more debug
		if time_difference.minutes > 0:
			self.refresh_valid_submissions()
			await ctx.channel.send("Refreshed")
			self.cached_time = datetime.now()
