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
photos_path = os.environ["PHOTOS_PATH"]

def is_hentai_channel(ctx):
	hentai_channel = bot.get_channel(hentai_channel_id)
	return ctx.channel == hentai_channel

def is_botadmin(ctx):
	zach_id = await bot.get_user_info(user_id="138458225958715392")
	return ctx.author.id == zach_id

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

####################    COMMANDS    ####################
@bot.command(name='del', pass_context=True)
@commands.check(is_hentai_channel)
async def delete_image(ctx, index: str):
	try:
		database.delete_entry(index)
		await ctx.channel.send('Deleted entry #{}.'.format(index))
	except Exception as e:
		print(e)
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
	else:
		row = database.fetch_random_entry()
		image_attachment, entry_no, user, add_date = helpers.format_hentai_entry(row)
		image_attachment = os.path.join(photos_path, image_attachment)
		msg = await ctx.channel.send("Fetching data...", file=discord.File(image_attachment))
		await msg.edit(content="Entry #{} added by {} on {}.".format(entry_no, user, add_date))

@bot.command(name='logout')
@commands.check(is_botadmin)
async def logout(ctx):
	await ctx.channel.send('脱退させていただきます')
	await bot.logout()
####################    END COMMANDS    ####################

@bot.event
async def on_message(message):
	await bot.process_commands(message)

	if message.author.id == bot.user.id:
			return 

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

			except Exception as e:
				await message.channel.send('Could not save image. Check the logs Zach.')
				print(e)

bot.run(os.environ["BOT_TOKEN"])