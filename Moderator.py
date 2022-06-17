### DISCORD BOT THAT MODERATES A GAME OF MAFIA
### CURRENTLY ONLY WORKS ON MY OWN MAFIA SERVER

import os
import discord
import random
import Game
import time
from discord.ext import commands

BOTTOKEN = 'NzQzNTc3MjU5MzczMzYzMjMw.XzWsSQ.P4Tyf8CQUaIn_wGmKnHeyWS4OJI'
newGame = Game.Game(0, 0)
bot = commands.Bot(command_prefix='!')

async def dmRoles():
### DM ROLES TO ALL PLAYERS
    for x in newGame.mafia:
        await x.create_dm()
        channel = x.dm_channel
        await channel.send('```Your role is MAFIA```')
    for x in newGame.town:
        await x.create_dm()
        channel = x.dm_channel
        await channel.send('```Your role is TOWN```')

async def kill(member):
### KILL A PLAYER
    aliveRole = discord.utils.get((bot.guilds[0]).roles, name = 'Alive')
    deadRole = discord.utils.get((bot.guilds[0]).roles, name = 'Dead')
    await member.add_roles(deadRole)
    await member.remove_roles(aliveRole)

async def checkWin():
### CHECK WIN CONDITIONS FOR BOTH SIDES
### MAFIA WINS IF MAFIA >= TOWN
### TOWN WINS IF MAFIA == 0
    mafiaCount = 0
    townCount = 0
    aliveRole = discord.utils.get((bot.guilds[0]).roles, name = 'Alive')
    alivePlayers = aliveRole.members
    alivePlayers.remove(bot.user)

    for x in alivePlayers:
        if(newGame.isMafia(x)):
            mafiaCount = mafiaCount + 1
        else:
            townCount = townCount + 1

    if mafiaCount >= townCount:
        return 'MAFIA'
    elif mafiaCount == 0:
        return 'TOWN'
    else:
        return 'NONE'

async def resetRoles():
### RESET ALL PLAYER ROLES
    allMembers = bot.guilds[0].members
    mafiaChannel = bot.guilds[0].get_channel(743602074381582446)
    generalVoiceChannel = bot.guilds[0].get_channel(743578844547776575)
    aliveRole = discord.utils.get((bot.guilds[0]).roles, name = 'Alive')
    deadRole = discord.utils.get((bot.guilds[0]).roles, name = 'Dead')
    for x in allMembers:
        if(x.voice != None):
            await x.move_to(generalVoiceChannel)
            await x.edit(mute = False)
        await mafiaChannel.set_permissions(x, overwrite = None)
        await x.remove_roles(aliveRole)
        await x.remove_roles(deadRole)

async def endGame():
### ENDS THE CURRENT GAME IN PROGRESS
    newGame.initMessageID = 0
    newGame.specialMessageId = 0
    newGame.voteMessageId = 0
    newGame.channelID = 0
    newGame.numMafia = 0
    newGame.numTown = 0
    newGame.cycleCount = 0
    newGame.players = []
    newGame.alive = []
    newGame.dead = []
    newGame.town = []
    newGame.mafia = []
    newGame.toBeKilled = []
    newGame.night = True
    newGame.doctor = False
    newGame.detective = False
    newGame.vigi = False
    newGame.voteInProgress = False
    newGame.mafiaKilled = False
    await resetRoles()

async def nextPhaseHelper():
### PHASES DAY AND NIGHT CYLCES AND ENDS THE GAME IF IT IS OVER
    generalTextChannel = bot.guilds[0].get_channel(743578844547776574)
    dayTextChannel = bot.guilds[0].get_channel(743602222952349766)
    ### KILL EVERYONE WHO DIED THE PREVIOUS NIGHT/DAY
    for x in newGame.toBeKilled:
        await kill(x)
        await generalTextChannel.send('```' + x.display_name + ' was killed```')
        if(x.voice != None):
            await x.edit(mute=True)

    ### CHECK IF THERE IS A WINNER
    winCondition = await checkWin()

    ### CONTINUE THE GAME IF THERE IS NO WINNER
    if(winCondition == 'NONE'):
        newGame.toBeKilled = []
        if(newGame.night):
            aliveRole = discord.utils.get((bot.guilds[0]).roles, name = 'Alive')
            alivePlayers = aliveRole.members
            alivePlayers.remove(bot.user)
            newGame.night = False
            newGame.voteInProgress = False
            newGame.cycleCount = newGame.cycleCount + 1
            await dayTextChannel.send('```It is now DAY ' + str(newGame.cycleCount) + '. Dicuss who you think the mafia is.```')
            for x in alivePlayers:
                if(x.voice != None):
                    await x.edit(mute = False)
        else:
            newGame.night = True
            await dayTextChannel.send('```It is now NIGHT ' + str(newGame.cycleCount) +'. Mafia will kill someone and town special roles may perform their action.```')
            for x in newGame.players:
                if(x.voice != None):
                    await x.edit(mute = True)
            newGame.mafiaKilled = False
            newGame.voteInProgress = False
    else:
        ### END GAME IF A WIN CONDITION WAS MET
        await dayTextChannel.send('```GAME OVER```')
        await dayTextChannel.send('```' + winCondition + ' WINS```')
        await dayTextChannel.send('```The mafia was:```')
        for x in newGame.mafia:
            await dayTextChannel.send('```' + x.display_name + '```')
        await resetRoles()


@bot.command(name='nextphase', help='Phase to the next day/night cycle')
async def next_phase(ctx):
    await nextPhaseHelper()

@bot.command(name = 'nominate', help = 'Nominate to kill someone, used for both town lynchings and mafia kills.')
async def nominate(ctx, arg1: str):
### NOMINATE A USER TO BE KILLED
    ### CHECK IF A VOTE IS IN PROGRESS
    if(newGame.voteInProgress):
        await ctx.send('```A vote is currently in progress```')
        return

    member = bot.guilds[0].get_member_named(arg1)
    mafiaChannel = bot.guilds[0].get_channel(743602074381582446)
    dayTextChannel = bot.guilds[0].get_channel(743602222952349766)
    aliveRole = discord.utils.get((bot.guilds[0]).roles, name = 'Alive')
    alivePlayers = aliveRole.members
    alivePlayers.remove(bot.user)
    yeaEmoji = '\U00002705'
    nayEmoji = '\U0000274c'
    yeas = 0
    nays = 0
    ### CHECK IF THE NOMINATED USER IS VALID
    if((member != None) and (member in alivePlayers)):
        newGame.voteInProgress = True
        ### CHECK IF MAFIA IS ABLE TO KILL
        if(newGame.night):
            if(newGame.isMafia(ctx.author) and not newGame.mafiaKilled and ctx.channel == mafiaChannel):
                ### VOTE TO KILL
                voteMessage = await ctx.send('```' + ctx.author.display_name + ' has nominated ' + arg1 + ' to be killed tonight. Vote yes to kill or no to not kill. You have 5 seconds to vote```')
                newGame.voteMessageId = voteMessage.id
                await voteMessage.add_reaction(yeaEmoji)
                await voteMessage.add_reaction(nayEmoji)
                time.sleep(5)
                message = await mafiaChannel.fetch_message(newGame.voteMessageId)
                yeas = message.reactions[0].count
                nays = message.reactions[1].count
                ### DETERMINE IF THE KILL GOES THROUGH
                if(yeas >= nays):
                    await ctx.send('```The vote to kill passed. ' + member.display_name + ' was killed.```')
                    newGame.toBeKilled.append(member)
                    newGame.mafiaKilled = True
                    newGame.voteInProgress = False
                else:
                    await ctx.send('```The vote to kill failed```')
                    newGame.voteInProgress = False
            else:
                await ctx.send('```You cannot do that right now```')
                newGame.voteInProgress = False
        else:
            voteMessage = await dayTextChannel.send('```' + ctx.author.display_name + ' has nominated ' + arg1 + ' to be lynched. Vote yes to lynch or no to not lynch. You have 5 seconds to vote```')
            newGame.voteMessageId = voteMessage.id
            await voteMessage.add_reaction(yeaEmoji)
            await voteMessage.add_reaction(nayEmoji)
            time.sleep(5)
            message = await dayTextChannel.fetch_message(newGame.voteMessageId)
            yeas = message.reactions[0].count
            nays = message.reactions[1].count
            ### DETERMINE IF THE KILL GOES THROUGH
            if(yeas > nays):
                await ctx.send('```The vote to kill passed. ' + member.display_name + ' was lynched.```')
                newGame.toBeKilled.append(member)
                newGame.voteInProgress = False
                await nextPhaseHelper()
            else:
                await ctx.send('```The vote to kill failed```')
                newGame.voteInProgress = False
    else:
        await ctx.send('```' + arg1 + ' is not a valid user```')

@bot.command(name='creategame', help='Create a mafia game followed by number of mafia then number of town')
async def create_game(ctx, arg1 : int, arg2 : int):
### CREATES A GAME LOBBY
    generalTextChannel = bot.guilds[0].get_channel(743578844547776574)
    emoji = '\U0001F351'
    detectiveEmoji = '\U0001f575'
    doctorEmoji = '\U0001fa7a'
    vigiEmoji = '\U0001F52B'
### GAME INITIALIZATION MESSAGE
    message = await generalTextChannel.send('```React to this message to play```')
    newGame.initMessageID = message.id
    newGame.channelID = message.channel.id
    newGame.numMafia = arg1
    newGame.numTown = arg2
    await message.add_reaction(emoji)
### TOWN SPECIAL ROLE MESSAGE
    message2 = await generalTextChannel.send('```Choose any special town roles (detective, doctor, vigilante)```')
    newGame.specialMessageId = message2.id
    await message2.add_reaction(detectiveEmoji)
    await message2.add_reaction(doctorEmoji)
    await message2.add_reaction(vigiEmoji)

@bot.command(name='startgame', help='Start a mafia game with the readied players')
async def start_game(ctx):
### STARTS THE GAME WITH THE PLAYERS CURRENTLY IN LOBBY
    ### GET THE PLAYERS WHO REACTED AND PUT THEM IN THE LOBBY
    generalTextChannel = bot.guilds[0].get_channel(743578844547776574)
    dayVoiceChannel = bot.guilds[0].get_channel(743606182081462283)
    dayTextChannel = bot.guilds[0].get_channel(743602222952349766)
    channel = bot.guilds[0].get_channel(newGame.channelID)
    message = await channel.fetch_message(newGame.initMessageID)
    message2 = await channel.fetch_message(newGame.specialMessageId)
    newGame.players = await message.reactions[0].users().flatten()
    aliveRole = discord.utils.get((bot.guilds[0]).roles, name = 'Alive')
    for x in newGame.players:
        await x.add_roles(aliveRole)

    ### ADD SPECIAL ROLES IF ANY
    if (message2.reactions[0].count > 1):
        newGame.detective = True
    if (message2.reactions[1].count > 1):
        newGame.doctor = True
    if (message2.reactions[2].count > 1):
        newGame.vigi = True

    ### START THE GAME IF THE LOBBY SIZE IS CORRECT
    newGame.players.remove(bot.user)
    if(len(newGame.players) == newGame.numMafia + newGame.numTown):
        await generalTextChannel.send('```Starting game, ' + str(len(newGame.players)) + ' players in lobby:```')

        ### LIST PLAYERS IN LOBBY AND MOVE THEM TO VOICE
        for x in newGame.players:
            await generalTextChannel.send('```' + x.display_name + '```')
            if(x.voice != None):
                await x.move_to(dayVoiceChannel)
                await x.edit(mute = True)
        newGame.setRoles()
        await dmRoles()
        newGame.night = True
        newGame.mafiaKilled = False
        newGame.toBeKilled = []

        ### GIVE MAFIA PERMISSIONS
        mafiaChannel = bot.guilds[0].get_channel(743602074381582446)
        overwrite = discord.PermissionOverwrite(read_messages = True, send_messages = True, add_reactions = True, read_message_history = True)
        for x in newGame.mafia:
            await mafiaChannel.set_permissions(x, overwrite=overwrite)

        ### BEGIN THE GAME
        startingString = '```There are ' + str(newGame.numMafia) + ' MAFIA and ' + str(newGame.numTown) + ' TOWN```'
        specialString = '```Town special roles are:'
        if(newGame.detective):
            specialString = specialString + ' DETECTIVE'
        if(newGame.doctor):
            specialString = specialString + ' DOCTOR'
        if(newGame.vigi):
            specialString = specialString + ' VIGILANTE'
        if(not newGame.detective and not newGame.doctor and not newGame.vigi):
            specialString = specialString + ' NONE'
        specialString = specialString + '```'

        await generalTextChannel.send(startingString)
        await generalTextChannel.send(specialString)
        await dayTextChannel.send('```It is now NIGHT ' + str(newGame.cycleCount) +'. Mafia will kill someone and town special roles may perform their action.```')
    else:
        await generalTextChannel.send('```Lobby size does not match the game size.```')

@bot.command(name='resetgame', help='Resets the current game setup. DO NOT USE WHEN GAME IS IN PROGRESS')
async def reset_game(ctx):
### RESETS THE CURRENT GAME LOBBY
    generalTextChannel = bot.guilds[0].get_channel(743578844547776574)
    await endGame()
    await generalTextChannel.send('```Game reset```')

bot.run(BOTTOKEN)
