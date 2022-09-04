# Lil Cheeky Responder bot or something

import os
import re
import discord
from dotenv import load_dotenv
from discord.ext import commands
from pymongo import MongoClient

#Load Token from ENV
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
OWNER_ID = [REDACTED]
GUILD_ID = [REDACTED] #Personal Test Server
bot_dir = os.path.dirname(__file__)

#Variables
try:
	dbClient = MongoClient()
	print('[INIT] Successfully loaded MongoDB!')
except:
	print("[ERROR] Could not load MongoDB...")
	dbClient.close()

class MyBot(commands.Bot):
	async def on_ready(self):
		activity = discord.Activity(name='Hoshi closely', type=discord.ActivityType.watching)
		await self.change_presence(activity=activity)
		print('|| Bot logged on as %s ||' % (self.user,))

	async def on_message(self, message):
		if message.author == self.user or message.guild == None or message.author.bot:
			return
		if not dbClient['db'].users.find_one({'_id': message.author.id}):
			_dict = {'_id': message.author.id, 'username': message.author.name, 'small_E': 0, 'large_E': 0}
			DB_enter('USER', message.author.id, _dict=_dict)
		else:
			emojis = re.findall(r'(<:.+?:\d+>)', message.content)
			_unicode = re.findall(r'([😀-🤷🏿‍♀])', message.content)
			if emojis or _unicode:
				emoji_length = 0
				unicode_length = 0
				count = 0
				for i in range(len(emojis)):
					emoji_length += len(emojis[i])
					count += 1
				for i in range(len(_unicode)):
					unicode_length += len(_unicode[i])
					count += 1
				db = dbClient['db']
				length = emoji_length + unicode_length
				if length == len(message.content.replace(' ', '')):
					doc = db.users.find_one({'_id': message.author.id})
					x = doc['large_E']
					x += count
					DB_enter('USER', message.author.id, key_val=('large_E', x))
				else:
					doc = db.users.find_one({'_id': message.author.id})
					x = doc['small_E']
					x += count
					DB_enter('USER', message.author.id, key_val=('small_E', x))
					await message.add_reaction('\U0001F1F8')
					await message.add_reaction('\U0001F1F2')
					await message.add_reaction('\U0001F1F4')
					await message.add_reaction('\U0001F1F1')
					await message.add_reaction('\U0001F1F5')
					await message.add_reaction('\U0001f17f')
					await message.add_reaction('\U0001F602')
		await self.process_commands(message)

	async def on_guild_join(self, guild):
		_dict = {'_id': guild.id, 'name': guild.name, 'prefix': '>>'}
		DB_enter('GUILD', guild.id, _dict=_dict)

	async def on_guild_remove(self, guild):
		return
		#DB_remove('GUILD', guild.id)	

#UTILITY FUNCTIONS
#--------------------------------
def DB_enter(searchTYPE, searchID, key_val=None, _dict=None):
	db = dbClient['db']
	if _dict == None:
		query = {'_id': searchID}
		newvalue = {'$set': {key_val[0]: key_val[1]}}
		if searchTYPE == 'GUILD':
			db.guilds.update_one(query, newvalue)
		else:
			db.users.update_one(query, newvalue)
	else:
		if searchTYPE == 'GUILD':
			db.guilds.insert_one(_dict)
		else:
			db.users.insert_one(_dict)

#Delete key_val option? Redundant?
def DB_remove(searchTYPE, searchID, key_val=None):
	db = dbClient['db']
	if key_val == None:
		query = {'_id': searchID}
		if searchTYPE == 'GUILD':
			db.guilds.delete_one(query)
		else:
			db.users.delete_one(query)
	else:
		query = {'_id': searchID, key_val[0]: key_val[1]}
		if searchTYPE == 'GUILD':
			db.guilds.delete_one(query)
		else:
			db.users.delete_one(query)

def is_admin(ctx):
	permissions = ctx.channel.permissions_for(ctx.author)
	return permissions.administrator

def get_pre(bot, message):
	db = dbClient['db']
	doc = db.guilds.find_one({'_id': message.guild.id})
	return doc['prefix']
#--------------------------------
#END UTILITY FUNCTIONS

#Create MyBot object
try:
	bot = MyBot(command_prefix=get_pre, help_command=None, owner_id=OWNER_ID)
	print('[INIT] Connected to Discord!')
except:
	print("[ERROR] Could not connect to Discord...")
	bot.logout()

#BOT COMMANDS
#--------------------------------
#CREATOR ONLY COMMANDS
@bot.command()
async def kill(ctx):
	is_owner = await bot.is_owner(ctx.author)
	if is_owner:
		try:
			dbClient.close()
			await bot.logout()
		except:
			print('Bot is kill')

#ADMIN COMMANDS
@bot.command()
async def setpre(ctx, newpre):
	if is_admin(ctx):
		DB_enter('GUILD', ctx.guild.id, key_val=('prefix', newpre))

#GENERAL COMMANDS
@bot.command()
async def getpre(ctx):
	db = dbClient['db']
	doc = db.guilds.find_one({'_id': ctx.guild.id})
	await ctx.send('Command prefix is: \"%s\"' % (doc['prefix']))
#-------------------------------
#END BOT COMMANDS
bot.run(TOKEN)