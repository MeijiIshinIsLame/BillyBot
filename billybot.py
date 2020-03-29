import discord
import asyncio

import helpers
import images

class MyClient(discord.Client):
	async def on_ready(self):
		print('Logged in as')
		print(self.user.name)
		print(self.user.id)
		print('------')

	async def on_message(self, message):
		hentai_channel = self.get_channel(692627802255523840)
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
						await message.channel.send(f'Image saved as entry #{image_id}. {helpers.get_random_save_message()}')
					except:
						await message.channel.send('Could not save image.')

client = MyClient()
client.run('NjkyNjE3ODkyMzg2MTc3MDI0.XnxL4Q.vx1vzPlTd-YZWWa7ImHMbojKjfE')
