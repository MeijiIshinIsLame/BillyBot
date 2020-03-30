import asyncio
import os

import helpers
import database
import images
import environment_variables

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
hentai_channel_id = int(os.environ["HENTAI_CHANNEL_ID"])

def is_hentai_channel(ctx):
	return ctx.channel == hentai_channel_id

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

@bot.command(pass_context=True)
async def cat(ctx):
	await ctx.channel.send('cat')

####################    COMMANDS    ####################
@bot.command(name='delete', pass_context=True)
#@commands.check(is_hentai_channel)
async def delete_image(ctx, index: str):
	print(ctx, index)
	print("we triedb\n\n\n\n\n\n")
	if ctx.channel == hentai_channel_id:
		try:
			database.delete_entry(index)
			await ctx.channel.send('Deleted entry #{}.'.format(index))
		except Exception as e:
			print(e)
			await ctx.channel.send('Image was unable to be deleted. Syncing database...')
			#sync database
			await ctx.channel.send('Finished!')
	else:
		await ctx.channel.send("Come on bro, hentai commands go in the hentai channel...")
####################    END COMMANDS    ####################

@bot.event
async def on_message(message):
	hentai_channel = bot.get_channel(hentai_channel_id)

	await bot.process_commands(message)

	if message.author.id == bot.user.id:
			return 

	if message.channel == hentai_channel:
		if message.content.startswith('!stop'):
			await message.channel.send('脱退させていただきます')
			await client.logout()

		if message.attachments:
			if helpers.is_image(message.attachments[0].url):
				try:
					saved_image = images.save_image(message.attachments[0].url)
					image_id = saved_image.split(".")[0]
					try:
						database.add_image_to_db(saved_image, message)
						await message.channel.send('Image saved as entry #' + image_id + ". " + helpers.get_random_save_message())
					except Exception as e:
						await message.channel.send('Image saved, but adding to database failed. Image deleted.')
						images.delete_image(saved_image)
						print(e)
				except Exception as e:
					await message.channel.send('Could not save image. Check the logs Zach.')
					print(e)

def make_mention_object_by_id(author_id):
	return "<@{}>".format(message.author.id)

bot.run(os.environ["BOT_TOKEN"])