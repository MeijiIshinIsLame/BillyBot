import asyncio
import os

import helpers
import database
import images
import environment_variables

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')
hentai_channel_id = int(os.environ["HENTAI_CHANNEL_ID"])
photos_path = os.environ["PHOTOS_PATH"]

def is_hentai_channel(ctx):
	hentai_channel = bot.get_channel(hentai_channel_id)
	return ctx.channel == hentai_channel

def is_botadmin(ctx):
	zach_id = 138458225958715392
	return ctx.author.id == zach_id

async def send_to_log_channel(error):
	#695558382622343279
	logs_channel = os.environ["logs_channel"]
	channel = bot.get_channel(logs_channel)
	await channel.send("```{}```".format(error))

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

####################    COMMANDS    ####################

@bot.command(name='help', pass_context=True)
async def help_message(ctx):
	help_msg = helpers.get_help_msg()
	await ctx.channel.send(content=help_msg)

@bot.command(name='del', pass_context=True)
@commands.check(is_hentai_channel)
async def delete_image(ctx, index: str):
	try:
		database.delete_entry(index)
		await ctx.channel.send('Deleted entry #{}.'.format(index))
	except Exception as e:
		print(e)
		send_to_log_channel(e)
		await ctx.channel.send('Image was unable to be deleted.')
		#sync database

@bot.command(name='hentai', pass_context=True)
@commands.check(is_hentai_channel)
async def pull_hentai(ctx, index : str = None):
	if index:
		try:
			row = database.fetch_specific_entry(index)
			image_attachment, entry_no, user, add_date = helpers.format_hentai_entry(row)
			image_attachment = os.path.join(photos_path, image_attachment)
			msg = await ctx.channel.send("Fetching data...", file=discord.File(image_attachment))
			await msg.edit(content="Entry #{} added by {} on {}.".format(entry_no, user, add_date))
		except Exception as e:
			await ctx.channel.send('Could not send image.')
			print(e)
			send_to_log_channel(e)
	else:
		row = database.fetch_random_entry()
		image_attachment, entry_no, user, add_date = helpers.format_hentai_entry(row)
		image_attachment = os.path.join(photos_path, image_attachment)
		msg = await ctx.channel.send("Fetching data...", file=discord.File(image_attachment))
		await msg.edit(content="Entry #{} added by {} on {}.".format(entry_no, user, add_date))

@bot.command(name='counthentai', pass_context=True)
async def count_hentai(ctx, user : discord.User = None):
	try:
		if user:
			user_id = str(user.id)
			total_count = database.count_hentai(user_id)
			user = helpers.make_mention_object_by_id(user_id)
			msg = await ctx.channel.send("Fetching data...")
			await msg.edit(content="{} contributed {} entries to the hentai database.".format(user, total_count))
		else:
			total_count = database.count_hentai()
			await ctx.channel.send(content="There are {} entries in the hentai database.".format(total_count))	
	except Exception as e:
		print(e)
		send_to_log_channel(e)
		await ctx.channel.send(content="Could not fetch data.")

@bot.command(name='logout')
@commands.check(is_botadmin)
async def logout(ctx):
	await ctx.channel.send('Shootz outies.')
	await bot.logout()

@bot.command(name='syncdb', pass_context=True)
@commands.check(is_botadmin)
async def sync_db_command(ctx):
	msg = await ctx.channel.send("Syncing database...")
	images_deleted, images_recovered = database.sync_db()
	await msg.edit(content="Database synced! Images deleted: {}  |  Images recovered: {}".format(images_deleted, images_recovered))

####################    END COMMANDS    ####################

@bot.event
async def on_message(message):
	await bot.process_commands(message)

	if message.author.id == bot.user.id:
			return 

	if is_hentai_channel(message):
		if message.attachments:
			if helpers.is_image(message.attachments[0].url):
				try:
					saved_image = images.save_image(message.attachments[0].url)

					if images.image_too_small(saved_image):
						#waifu2x stuff will go here eventually
						images.delete_image(saved_image)
						await message.channel.send("Image too small! Gotta be bigger than 400x400 dawg.")	
					else:
						image_id = saved_image.split(".")[0]
						try:
							database.add_image_to_db(saved_image, message)
							await message.channel.send('Image saved as entry #' + image_id + ". " + helpers.get_random_save_message())
						except Exception as e:
							await message.channel.send('Image saved, but adding to database failed. Image deleted.')
							images.delete_image(saved_image)
							print(e)
							send_to_log_channel(e)
				except Exception as e:
					await message.channel.send('Could not save image. Check the logs Zach.')
					print(e)
					send_to_log_channel(e)

bot.run(os.environ["BOT_TOKEN"])


#todo: add regular username to database or just nope out and make flask app
#make logging