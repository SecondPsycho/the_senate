import discord
from data import *
import doc

#Small Helper Functions
def clean_up(data):
    data = data.split('\n')
    data = data[0].split(' ')
    while '' in data:
        data.remove('')
    for i in range(len(data)):
        data[i] = data[i].lower()
    return data

def one_line(data):
    data = data.split('\n')
    return data[0]

Narrator = 'Gen_CAT'

#"""
#Individual Command Functions
async def Help(Game, message, data):
    len_data = len(data)
    if len_data == 1:
        if not Game.ON:
            await message.channel.send("The Game hasn't started.\n"+doc.help_JOIN)
        elif Game.NIGHT:
            await message.channel.send("It's Nighttime.\n"+doc.help_NIGHT1)
            await message.channel.send(doc.help_NIGHT2)
        else:
            await message.channel.send("It's Daytime.\n"+doc.help_DAY)
    elif len_data == 2:
        if data[1] == 'help':
            await message.channel.send(doc.help_HELP)
        elif data[1] == 'join':
            await message.channel.send("Commands for before the game starts.\n"+doc.help_JOIN)
        elif data[1] == 'day':
            await message.channel.send("Commands for the Daytime.\n"+doc.help_DAY)
        elif data[1] == 'night':
            await message.channel.send("Commands for the Nighttime.\n"+doc.help_NIGHT1)
            await message.channel.send(doc.help_NIGHT2)
        else:
            await message.channel.send('There is no help for a "'+data[1]+'" command.')
    else:
        await message.channel.send('Unrecognized use of the "!help" command.')
        await message.channel.send(doc.help_help)

async def Draw(Game, message, data):
    len_data = len(data)
    if len_data < 3:
        if not Game.ON or message.author.name == Narrator:
            if len_data < 2:
                num_cards = 3
            else:
                try:
                    num_cards = int(data[1])
                    if num_cards <= 0:
                        await message.channel.send('Too few cards. Must be at least 1.')
                        return
                    elif num_cards > 60:
                        await message.channel.send('Too many cards. Must be at most 60.')
                        return
                except:
                    await message.channel.send('Invalid Input. "'+str(data[1])+'" is not an integer.')
                    return
            cards = Game.draw(num_cards)
            for i in range(num_cards):
                cards[i] = Cards[cards[i]]
            cards = ' '.join(cards)
            await message.channel.send("Drawing "+str(num_cards)+" Cards.")
            await message.channel.send(cards)
        else:
            await message.channel.send('The !draw command is not available to players while the game is live.')
    else:
        await message.channel.send('Unrecognized use of the "!draw" command.')
        await message.channel.send(doc.help_draw)

async def Join(Game, message, data):
    if Game.ON:
        await message.channel.send("Sorry. The game has already started.")
        return
    if message.author.bot:
        await message.channel.send("Sorry. Bots can't play.")
        return
    len_data = len(data)
    if len_data == 1:
        if Game.newPlayer(message):
            await message.channel.send('Thank you! Player '+message.author.name+' has joined the game in the '+message.channel.name+' chatroom.')
        else:
            await message.channel.send("You've already joined the game.")
    elif len_data == 2 and data[1] == 'here':
        if Game.newPlayer(message):
            await message.channel.send('Thank you! Registering Player "'+message.author.name+'" in the '+message.channel.name+' chatroom.')
        else:
            player = Game.getPlayer(message.author.name)
            if player.chatroom != message.channel.name:
                player.chatroom = message.channel.name
                await message.channel.send('This is now your chatroom.')
            else:
                await message.channel.send('This was already your chatroom.')
    elif len_data == 3 and data[1] == 'player':
        data[2] = message.content.split(' ')[2]
        if message.author.name == Narrator:
            player = Game.getPlayer(data[2])
            if player == '':
                Game.pn += 1
                Game.addPlayer(data[2], message.channel.name, 'None', ' ', 0, Game.pn)
                await message.channel.send('Thank you! Player "'+data[2]+'" is joined in the '+message.channel.name+' chatroom.')
            elif player.chatroom != message.channel.name:
                player.chatroom = message.channel.name
                await message.channel.send(player.name+"'s chat room is now "+message.channel.name+'.')
            else:
                await message.channel.send('That Player is already in the Game.')
        else:
            await message.channel.send('Only Gen_CAT can add other players.')
    else:
        await message.channel.send('Unrecognized use of the "!join" command.')
        await message.channel.send(doc.help_join)

async def Unjoin(Game, message, data):
    if Game.ON:
        await message.channel.send("Sorry. The game has already started.")
        return
    len_data = len(data)
    if len_data == 1:
        if Game.removePlayer(message.author.name):
            await message.channel.send("Sorry to see you go. Bye!")
        else:
            await message.channel.send("You were already out of the game.")
    elif len_data == 3 and data[1] == 'player':
        if message.author.name == Narrator:
            player = Game.findPlayer(data[2])
            if player == '':
                await message.channel.send('No player "'+data[2]+'" to remove.')
            else:
                Game.removePlayer(player.name)
                await message.channel.send('Player "'+player.name+'" has been removed.')
        else:
            await message.channel.send('Only Gen_CAT can remove other players.')
    else:
        await message.channel.send('Unrecognized use of the "!unjoin" command.')
        await message.channel.send(doc.help_unjoin)

async def Show(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    if len(data) == 2:
        player = Game.getPlayer(message.author.name)
        if player != '':
            if message.channel.name != player.chatroom:
                await message.channel.send('You can only use the "!show" command in your own chatroom!')
            elif data[1] == 'hand' or data[1] == 'cards':
                hand = player.printableCards()
                if hand != '':
                    await message.channel.send("Here's your hand.")
                    await message.channel.send(player.printableCards())
                    if (not Game.NIGHT) and player.discard > len(player.actions):
                        await message.channel.send('(You still have to discard '+str(player.discard-len(player.actions))+' card(s) today)')
                else:
                    await message.channel.send("Your hand is empty.")
            elif data[1] == 'color':
                if player.color == -1:
                    await message.channel.send("Your color is not set.")
                else:
                    await message.channel.send("Your color is currently set to "+Colors[player.color]+'.')
            elif data[1] == 'actions':
                if len(player.actions) == 0:
                    await message.channel.send("You have no actions listed.")
                else:
                    await message.channel.send("Here are your currently listed actions:")
                    await message.channel.send(player.printableActions())
            elif data[1] == 'vote' or data[1] == 'votes':
                report = "You're voting for: "
                if player.votes[0] == -1:
                    report += 'nobody'
                else:
                    report += Game.Players[player.votes[0]].name
                    for vote in player.votes[1:]:
                        if vote != -1:
                            report += ' & ' + Game.Players[vote].name
                report += '.'
                await message.channel.send(report)
            else:
                await message.channel.send('"!show" does not recognize "'+data[1]+'" as a key.')
        else:
            await message.channel.send('You have not joined the game.')
    else:
        await message.channel.send('Unrecognized use of the "!show" command.')
        await message.channel.send(doc.help_show)

async def Set(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    if not Game.NIGHT:
        await message.channel.send("You can only use this command at night.")
        return
    player = Game.getPlayer(message.author.name)
    if player.lives <= 0:
        await message.channel.send("Dead players can't use this command.")
        return
    if len(data) == 3 and data[1] == 'color':
        for i in range(1,4):
            if data[2] == Colors[i]:
                if player.color == i:
                    await message.channel.send('Your color was already set to '+Colors[i]+'.')
                else:
                    player.color = i
                    await message.channel.send('Your color for the night has been set to '+Colors[i]+'.')
                    player.actions = []
                return
        await message.channel.send('Did not recognize "'+data[2]+'" as a color.')
    else:
        await message.channel.send('Unrecognized use of the "!set" command.')
        await message.channel.send(doc.help_set)

async def play_card(Game, message, player, data, card):
    card_2d = card+player.color
    if player.color == -1:
        await message.channel.send("You have not set your color.")
    elif card_2d in player.hand:
        playedcount = 0
        for action in player.actions:
            if action[1] == card_2d:
                playedcount += 1
        if playedcount >= player.hand.count(card_2d):
            await message.channel.send('You cannot play that card again.')
            return
        if data[2] == 'me' or data[2] == 'myself':
            target = player
        else:
            target = Game.findPlayer(data[2])
        if target != '':
            player.actions.append([player.ID,card+player.color,target.ID])
            if card == 20:
                await message.channel.send("Preparing to offer a tax to "+target.name+".")
            elif card == 10:
                await message.channel.send("Preparing to murder "+target.name+".")
            else:
                await message.channel.send("Preparing to guard "+target.name+".")
        else:
            await message.channel.send("Couldn't find a Player named "+'"'+data[2]+'" in the game.')
    else:
        await message.channel.send("You do not have a "+Colors[player.color]+" "+Actions[int(card/10)]+" card.")
        
async def Play(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    if not Game.NIGHT:
        await message.channel.send("You can only use this command at night.")
        return
    player = Game.getPlayer(message.author.name)
    if player.lives <= 0:
        await message.channel.send("Dead players can't play abilities.")
        return
    if player.mustDiscard():
        await message.channel.send("You must discard a card before playing another ability. Use the '!discard' command.")
        return
    len_data = len(data)
    if len_data >= 2:
        if data[1] == 'red' or data[1] == 'green' or data[1] == 'blue':
            if data[1] == Colors[player.color]:
                data.pop(1)
                len_data -= 1
            elif len(player.actions) == 0:
                    await message.channel.send("Your color is set to "+Colors[player.color]+", and you have actions listed.")
                    return
            else:
                player.color = Colors.index(data[1])
                await message.channel.send('Your color for the night has been sent to "'+data[1]+'"')
                data.pop(1)
                len_data -= 1
    if len_data == 4 and data[2] == 'on':
        data.pop(2)
        len_data -= 1
    elif len_data == 2:
        data.append('me')
        len_data += 1
    if len_data == 3:
        if "murder" in data[1] or "knife" in data[1] or "kill" in data[1] or "stab" in data[1] or data[1] == '1' or data[1] == "10":
            await play_card(Game, message, player, data, 10)
        elif "guard" in data[1] or "shield" in data[1] or "protect" in data[1] or data[1] == '3' or data[1] == '30':
            await play_card(Game, message, player, data, 30)
        elif "tax" in data[1] or "coin" in data[1] or data[1] == '2' or data[1] == '20':
            await play_card(Game, message, player, data, 20)
        else:
            await message.channel.send('"'+data[1]+'" is not a recognized ability.')
    else:
        await message.channel.send('Unrecognized use of the "!play" command.')
        await message.channel.send(doc.help_play)

async def Unplay(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    len_data = len(data)
    if len_data == 1:
        player = Game.getPlayer(message.author.name)
        if len(player.actions) == 0:
            await message.channel.send('You have no actions listed.')
        else:
            await message.channel.send('Your last action has been unplayed.')
            player.actions.pop(-1)
    elif len_data == 2 and data[1] == 'all':
        player = Game.getPlayer(message.author.name)
        player.actions = []
        await message.channel.send('All actions have been cleared.')
    else:
        await message.channel.send('Unrecognized use of the "!unplay" command.')
        await message.channel.send(doc.help_unplay)

async def Discard(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    player = Game.getPlayer(message.author.name)
    if not Game.NIGHT and len(player.actions) >= player.discard:
        await message.channel.send("You don't have to discard any more cards.")
        return
    len_data = len(data)
    if len_data == 2:
        index = 0
        cardtype = 0
        if data[1] == 'red':
            cardtype = 1
        elif data[1] == 'green':
            cardtype = 2
        elif data[1] == 'blue':
            cardtype = 3
        if cardtype != 0:
            for card in player.hand:
                if card % 10 == cardtype:
                    if index == 0:
                        index = card
                    else:
                        await message.channel.send('You have more than one '+Colors[cardtype]+' card.')
                        return
            if index == 0:
                await message.channel.send("You don't have any "+Colors[cardtype]+" cards.")
                return
        else:
            if "murder" in data[1] or "knife" in data[1] or "kill" in data[1] or "stab" in data[1] or data[1] == '1' or data[1] == "10":
                cardtype = 1
            elif "tax" in data[1] or "coin" in data[1] or data[1] == '2' or data[1] == '20':
                cardtype = 2
            elif "guard" in data[1] or "shield" in data[1] or "protect" in data[1] or data[1] == '3' or data[1] == '30':
                cardtype = 3
            if cardtype != 0:
                for card in player.hand:
                    if int(card/10) == cardtype:
                        if index == 0:
                            index = card
                        else:
                            await message.channel.send('You have more than one '+Actions[cardtype]+' card.')
                            return
                if index == 0:
                    await message.channel.send("You don't have any "+Actions[cardtype]+" cards.")
                    return
            else:
                await message.channel.send('Unable to identify "'+data[1]+'" as a card.')
                return
        card_count = 0
        for action in player.actions:
            if action[1] == 0 and action[2] == index:
                card_count += 1
        if card_count >= player.hand.count(index):
            await message.channel.send('You cannot discard any more '+Colors[index%10]+" "+Actions[int(index/10)]+' cards.')
        else:
            await message.channel.send('Discarding a '+Colors[index%10]+" "+Actions[int(index/10)]+" card.")
            player.actions.append([player.ID,0,index])
    elif len_data == 3:
        cardtype = 0
        if data[1] == 'red':
            cardtype = 1
        elif data[1] == 'green':
            cardtype = 2
        elif data[1] == 'blue':
            cardtype = 3
        else:
            await message.channel.send('Unable to identify "'+data[1]+'" as a color.')
            return
        if "murder" in data[2] or "knife" in data[2] or "kill" in data[2] or "stab" in data[2] or data[2] == '1' or data[2] == "10":
            cardtype += 10
        elif "tax" in data[2] or "coin" in data[2] or data[2] == '2' or data[2] == '20':
            cardtype += 20
        elif "guard" in data[2] or "shield" in data[2] or "protect" in data[2] or data[2] == '3' or data[2] == '30':
            cardtype += 30
        else:
            await message.channel.send('Unable to identify "'+data[2]+'" as an action.')
            return
        await message.channel.send('Discarding a '+Colors[cardtype%10]+" "+Actions[int(cardtype/10)]+" card.")
        player.actions.append([player.ID,0,cardtype])
    else:
        await message.channel.send('Unrecognized use of the "!discard" command.')
        await message.channel.send(doc.help_discard)

async def vote_for(Game, message, player, data, num):
    if data[1] == 'nobody':
        for i in range(num):
            player.votes[i] = -1
        await message.channel.send("Setting "+str(num)+" vote(s) for nobody.")
        return
    elif data[1] == 'me' or data[1] == 'myself':
        target = player
    else:
        target = Game.findPlayer(data[1])
    if target != '':
        for i in range(num):
            player.votes[i] = target.ID
        await message.channel.send("Setting "+str(num)+" vote(s) for "+target.name+".")
    else:
        await message.channel.send("Couldn't find a Player named "+'"'+data[1]+'" in the game.')

async def Vote(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    if Game.NIGHT:
        await message.channel.send("You can only use this command during the day.")
        return
    player = Game.getPlayer(message.author.name)
    if player.lives <= 0:
        await message.channel.send("Dead players can't vote.")
        return
    len_data = len(data)
    if len_data == 2:
        await vote_for(Game, message, player, data, player.lives)
    elif len_data == 3:
        try:
            count = abs(int(data[2]))
            await vote_for(Game, message, player, data, min(count,player.lives))
        except:
            await message.channel.send('"'+data[2]+'" is not a valid number of votes.')
    else:
        await message.channel.send('Unrecognized use of the "!vote" command.')
        await message.channel.send(doc.help_vote)

async def Start(Game, client, message, data):
    if message.author.name == Narrator:
        if data[1] == 'game':
            if Game.ON:
                await message.channel.send("The Game has already started.")
            else:
                Game.deal(3)
                Game.ON = True
                await message.channel.send("Let the Games Begin.")
        elif not Game.ON:
            await message.channel.send('The game has not Started.')
        elif data[1] == 'night':
            if not Game.NIGHT:
                await message.channel.send('The Night Cycle has Begun.')
                report = "**VOTING IS CLOSED.**\n"
                tally = [0]*Game.pn
                for player in Game.Players:
                    report += '**' + player.name + ' voted for: '
                    if player.votes[0] == -1:
                        report += 'nobody'
                    else:
                        report += Game.Players[player.votes[0]].name
                        tally[player.votes[0]] += 1
                        for vote in player.votes[1:]:
                            if vote != -1:
                                report += ' & ' + Game.Players[vote].name
                                tally[vote] += 1
                    report += '.**\n'
                await message.channel.send(report)
                high = 0
                index = -1
                report = '**FINAL TALLY:**\n'
                for i in range(Game.pn):
                    if tally[i] > 0:
                        report += '**' + Game.Players[i].name + ': '+str(tally[i])+'**\n'
                        if tally[i] > high:
                            index = i
                            high = tally[i]
                        elif tally[i] == high:
                            index = -1
                if index == -1:
                    report += '**Vote is Tied.**'
                else:
                    report += '**'+Game.Players[index].name+' is Elected.**'
                await message.channel.send(report)
                Game.startNight()
                Game.save('night')
            else:
                await message.channel.send('It is already night.')
        elif data[1] == 'day':
            if Game.NIGHT:
                await message.channel.send('The Day Cycle has Begun.')
                report = "Here's the Nightly Report:\n"
                for player in Game.Players:
                    report += player.name + ':\n' + player.printableActions() + '\n'
                await message.channel.send(report)
                Game.startDay()
                Game.save('day')
            else:
                await message.channel.send('It is already day.')
        else:
            await message.channel.send('Unrecognized use of the "!start" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Save(Game, message, data):
    if message.author.name == Narrator:
        len_data = len(data)
        if len_data == 1:
            Game.save('manual')
            await message.channel.send('Save Successful.')
        elif len_data == 2:
            Game.save(data[1])
            await message.channel.send('Save Successful.')
        else:
            await message.channel.send('Unrecognized use of the "!save" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Load(Game, message, data):
    if message.author.name == Narrator:
        len_data = len(data)
        if len_data == 2:
            if data[1] == 'new':
                Game.reset()
                await message.channel.send('Loaded a New Game.')
            else:
                try:
                    Game.load(data[1])
                except:
                    await message.channel.send('Loading Failed.')
                    return
                await message.channel.send('Loading Successful!')
        else:
            await message.channel.send('Unrecognized use of the "!load" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

result = 'No result.'
async def Report(Game, message, data):
    if message.author.name == Narrator:
        if len(data) > 1:
            try:
                report = message.content[8:]
                if '(' in report:
                    await message.channel.send("Input cannot contain parentheses.")
                elif '=' in report:
                    await message.channel.send("Input cannot contain an equals sign.")
                else:
                    global result
                    exec('global result\nresult = str('+report+')')
                    await message.channel.send(result)
            except:
                await message.channel.send('Invalid Input. Cannot run "'+report+'".')
        else:
            await message.channel.send('Unrecognized use of the "!report" command.')
    else:
        await message.channel.send("Only "+Narrator+" can run the '!report' command.")

async def Control(Game, message, data):
    print('control')
    if message.author.name == Narrator:
        len_data = len(data)
        if len_data == 4 and (data[1] == 'give' or data[1] == 'take'):
            target = Game.findPlayer(data[2])
            if target == '':
                await message.channel.send("Couldn't find player"+' "'+data[2]+'"')
                return
            try:
                card = abs(int(data[3]))
                if card in Cards and card != 0:
                    if data[1] == 'give':
                        if target.giveCard(card):
                            await message.channel.send("Gave a "+Cards[card]+" to "+target.name+'.')
                        else:
                            await message.channel.send(target.name+" has reached the max hand size.")
                    elif data[1] == 'take':
                        if target.discardCard(card):
                            await message.channel.send("Took a "+Cards[card]+" from "+target.name+'.')
                        else:
                            await message.channel.send(target.name+" had no "+Cards[card]+" .")
                    else:
                        await message.channel.send('You should never see this...')
                else:
                    await message.channel.send('"'+data[3]+'" is not a valid card.')
            except:
                await message.channel.send('"'+data[3]+'" is not a valid integer.')
        elif len_data == 4 and data[1] == 'lives':
            target = Game.findPlayer(data[2])
            if target == '':
                await message.channel.send("Couldn't find player"+' "'+data[2]+'"')
                return
            try:
                lives = abs(int(data[3]))
                if lives <= 3:
                    target.lives = lives
                    await message.channel.send("Set "+target.name+"'s lives to "+str(lives)+'.')
                else:
                    await message.channel.send(str(lives)+" is too many.")
            except:
                await message.channel.send('"'+data[3]+'" is not a valid integer.')
        else:
            await message.channel.send('Unrecognized use of the "!control" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Exit(Game, message, data):
    if message.author.name == Narrator:
        await message.channel.send("Goodbye!")
        Game.save('exit')
        exit(0)
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Test(Game, message, data, client):
    for player in Game.Players:
        if player.tag != 0:
            await client.get_channel(Channels[player.chatroom]).send('<@'+str(player.tag)+'> Dinner is Ready.')
        else:
            await message.channel.send(player.name+' has no listed tag.')

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        #musings = self.get_channel(Channels['narrator-musings'])
        musings = self.get_channel(Channels['bot-tests'])
        await musings.send('Bot is Online.')
        try:
            Game.load('tmp')
            await musings.send('Loaded "tmp.txt"')
        except:
            await musings.send('Game Loading Failed. Loaded a New Game.')
    async def on_message(self, message):
        if message.author == client.user:
                return
        elif message.content.startswith('!'):
            print(message.author.name,':\n   ',message.content)
            if 1==1: #try:
                player = Game.getPlayer(message.author.name)
                if player != '':
                    if player.nick != message.author.nick:
                        #print("Updated Nickname.", player.nick, str(message.author.nick))
                        player.nick = str(message.author.nick)
                    if player.disc == ' ':
                        player.disc = message.author.discriminator
                    if player.tag == 0:
                        player.tag = message.author.id
                elif Game.ON and message.author.name != Narrator:
                    await message.channel.send("Seems you're not listed as a Player... contact Gen_CAT if you feel this should be different.")
                    return
                
                data = clean_up(message.content)
                if data[0] == '!help':
                    await Help(Game, message, data)
                elif data[0] == '!draw':
                    await Draw(Game, message, data)
                elif data[0] == '!join':
                    await Join(Game, message, data)
                elif data[0] == '!unjoin':
                    await Unjoin(Game, message, data)
                elif data[0] == '!show':
                    await Show(Game, message, data)
                    
                elif data[0] == '!set':
                    await Set(Game, message, data)
                elif data[0] == '!play':
                    await Play(Game, message, data)
                elif data[0] == '!unplay':
                    await Unplay(Game, message, data)
                elif data[0] == '!discard':
                    await Discard(Game, message, data)

                elif data[0] == '!vote':
                    await Vote(Game, message, data)
                
                elif data[0] == '!start':
                    await Start(Game, self, message, data)
                elif data[0] == '!save':
                    await Save(Game, message, data)
                elif data[0] == '!load':
                    await Load(Game, message, data)
                elif data[0] == '!report':
                    await Report(Game, message, data)
                elif data[0] == '!control':
                    await Control(Game, message, data)
                elif data[0] == '!exit':
                    await Exit(Game, message, data)
                elif data[0] == '!test':
                    await Test(Game, message, data, client)
                else:
                    await message.channel.send("Unrecognized Command.")
                    await Help(Game, message, data)
            else: #except:
                if message.content == '!exit' and message.author.name == Narrator:
                    exit(0)
                await message.channel.send("Oops. Something went wrong :(")
                print("There was a Problem with input:",message.content)
            Game.save('tmp')


Game = NewGame()

File = open('token.txt', 'r')
token = File.readline()
File.close()

client = MyClient()
client.run(token)
