from bs4 import BeautifulSoup
import requests

import discord
from discord import app_commands
from discord.ext import commands

from dotenv import dotenv_values


TONE_WEBSITE_URL = "https://r74n.com/words/twitter"


'''class Tone:
	def __init__(self, indicator: str, meaning: str):
		self.indicator = indicator
		self.meaning = meaning
	
	def __repr__(self):
		return f"{self.indicator} - {self.meaning}\n"'''

class MyClient(discord.Client):
	def __init__(self, *, intents: discord.Intents):
		super().__init__(intents=intents)
		self.tree = app_commands.CommandTree(self)

	async def setup_hook(self):
		# This loads the tones from the website
		self.tones = load_tones()
		print("Loaded tones")
		# This saves the bot's owner id in a variable
		self.owner = self.application.owner
		# This synces the registered commands
		await self.tree.sync()
		print("Synced commands")

	async def stringify_tones(self) -> str:
		tones_string = f"Total tones indicators found: `{len(self.tones)}`\n"
		for indicator, meaning in self.tones.items():
			tones_string += f"`{indicator}` - {meaning}\n"
		return tones_string



def load_tones() -> {str: str} or None :
	tone_website_response = requests.get(TONE_WEBSITE_URL)
	if tone_website_response.status_code != 200:
		return None
	else:
		website_text = tone_website_response.text
		parsed_website = BeautifulSoup(website_text, "html.parser")
		tone_string = parsed_website.body.find("h3", id="Tone").next_sibling.next_sibling.text # First next sibling is newline, so we skip it
		
		'''tones_list = []
		for line in tone_string.splitlines():
			(indicator, meaning) = line.split(" - ")
			tones_list.append(Tone(indicator, meaning))
		return tones_list'''
		tones_dict = {}
		
		for line in tone_string.splitlines():
			(indicators, meaning) = line.split(" - ")
			for indicator in indicators.split(", "):
				tones_dict[indicator] = meaning
		return tones_dict


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

TOKEN = dotenv_values(".env")["TOKEN"]

@client.tree.command(description="Main command of the bot. Gets a meaning for a tone indicator")
@app_commands.describe(indicator="The tone indicator to get the meaning for")
async def get_meaning(interaction: discord.Interaction, indicator: str):
	if indicator[0] != "/":
		indicator = "/"+indicator

	if indicator in interaction.client.tones.keys():
		await interaction.response.send_message(f"`{indicator}` means {interaction.client.tones[indicator]}", ephemeral=True)
	else:
		await interaction.response.send_message(f"The requested tone indicator `{indicator}` doesn't exist", ephemeral=True)

@client.tree.command(description="Shows all tone indicators and their meanings")
async def get_tones(interaction: discord.Interaction):
	await interaction.response.send_message(f"{await interaction.client.stringify_tones()}", ephemeral=True)


@client.tree.command(description="Owner-only command. Makes the bot terminate.")
async def exit(interaction: discord.Interaction):
	if interaction.user.id == interaction.client.owner.id:
		await interaction.response.send_message("Bot is exiting...", ephemeral=True)
		await interaction.client.change_presence(status=discord.Status.offline, activity=None)
		await interaction.client.close()
	else:
		await interaction.response.send_message(f"Only the owner, {self.owner.name} can execute that command")
	

if __name__ == "__main__":
	client.run(TOKEN)