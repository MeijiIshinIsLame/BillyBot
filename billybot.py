import discord
import asyncio
import os

import helpers
import database
import images
import environment_variables

class MyClient(discord.Client):
	hentai_channel_id = int(os.environ["HENTAI_CHANNEL_ID"])

	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

	async def on_message(self, message):
		hentai_channel = self.get_channel(self.hentai_channel_id)
		if message.channel == hentai_channel:
			if message.author.id == self.user.id:
				return 
			if message.content.startswith('!stop'):
				await message.channel.send('脱退させていただきます')
				await client.logout()
			if message.attachments:
				if helpers.is_image(message.attachments[0].url):
					try:
						saved_image = images.save_image(message.attachments[0].url)
						image_id = saved_image.split(".")[0]
						database.add_image_to_db(saved_image, message)
						await message.channel.send('Image saved as entry #' + image_id + ". " + helpers.get_random_save_message())
					except Exception as e:
						await message.channel.send('Could not save image.')
						print(e)

client = MyClient()
client.run(os.environ["BOT_TOKEN"])
#NjkyNjE3ODkyMzg2MTc3MDI0.XnxL4Q.vx1vzPlTd-YZWWa7ImHMbojKjfE