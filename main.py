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

NARRATOR = 249679490429485057
ME = 812330570456760340

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
        if not Game.ON or message.author.id == NARRATOR:
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
        if message.author.id == NARRATOR:
            player = Game.getPlayer(data[2])
            if player == '':                
                Game.addPlayer(data[2], message.channel.name, 'None', ' ', '0', Game.pn)
                Game.pn += 1
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
        if message.author.id == NARRATOR:
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
            elif data[1] == "lives" or data[1] == "life":
                report = "You have "
                if player.lives == 1:
                    report += "1 life left."
                else:
                    report += str(player.lives) + " lives left."
                await message.channel.send(report)
            elif "guard" in data[1] or "shield" in data[1] or "protect" in data[1]:
                await message.channel.send("You have " + str(player.shields) + " " + Cards[30] +" from last night.")
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
    if player.chatroom != message.channel.name:
        await message.channel.send("You can only use the \"!play\" command in your own chatroom!")
        return
    len_data = len(data)
    if len_data >= 2:
        if data[1] == 'red' or data[1] == 'green' or data[1] == 'blue':
            if data[1] == Colors[player.color]:
                data.pop(1)
                len_data -= 1
            elif len(player.actions) != 0:
                    await message.channel.send("Your color is set to "+Colors[player.color]+", and you have actions listed.")
                    return
            else:
                player.color = Colors.index(data[1])
                await message.channel.send('Your color for the night has been set to '+data[1]+'.')
                data.pop(1)
                len_data -= 1
    if len_data >= 4 and data[2] == 'on':
        data.pop(2)
        len_data -= 1
    count = 1
    all_count = False
    if len_data == 4 or (len_data == 3 and Game.findPlayer(data[2]) == "" and data[2] != "me" and data[2] != "myself"):
        if data[-1] == 'all':
            all_count = True
        else:
            try:
                count = abs(int(data[-1]))
            except:
                if len_data == 3 and Game.findPlayer(data[2]) == "" and data[2] != "me" and data[2] != "myself":
                    await message.channel.send('"'+data[-1]+'" is not a valid number or Player.')
                else:
                    await message.channel.send('"'+data[-1]+'" is not a valid number.')
                return
        data.pop(-1)
        len_data -= 1
    if len_data == 2:
        data.append('me')
        len_data += 1
    if len_data == 3:
        cardType = 0
        if "murder" in data[1] or "knife" in data[1] or "kill" in data[1] or "stab" in data[1] or data[1] == '1' or data[1] == "10":
            cardType = 10
        elif "guard" in data[1] or "shield" in data[1] or "protect" in data[1] or data[1] == '3' or data[1] == '30':
            cardType = 30
        elif "tax" in data[1] or "coin" in data[1] or data[1] == '2' or data[1] == '20':
            cardType = 20
        else:
            await message.channel.send('"'+data[1]+'" is not a recognized ability.')
            return
        if all_count:
            count = player.hand.count(cardType + player.color)
        for i in range(count):
            if await must_discard(player, message):
                break
            await play_card(Game, message, player, data, cardType)
        await Show(Game, message, ['!show', 'actions'])
    else:
        await message.channel.send('Unrecognized use of the "!play" command.')
        await message.channel.send(doc.help_play)

async def must_discard(player, message):
    if player.mustDiscard():
        await message.channel.send("You must discard a card before playing another ability. Use the '!discard' command.")
        return True
    return False

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
            await Show(Game, message, ['!show', 'actions'])
            player.actions.pop(-1)
    elif len_data == 2 and data[1] == 'all':
        player = Game.getPlayer(message.author.name)
        player.actions = []
        await message.channel.send('All actions have been cleared.')
    elif len_data == 2:
        player = Game.getPlayer(message.author.name)
        try:
            count = min(abs(int(data[1])), len(player.actions))
            for i in range(count):
                player.actions.pop(-1)
            await message.channel.send('Uplayed ' + str(count) + ' actions.')
            await Show(Game, message, ['!show', 'actions'])
        except:
            await message.channel.send('"'+data[1]+'" is not a valid number.')
            return
    else:
        await message.channel.send('Unrecognized use of the "!unplay" command.')
        await message.channel.send(doc.help_unplay)

async def Discard(Game, message, data):
    if not Game.ON:
        await message.channel.send("You can only use this command once the game has started.")
        return
    player = Game.getPlayer(message.author.name)
    if player.chatroom != message.channel.name:
        await message.channel.send("You can only use the \"!discard\" command in your own chatroom!")
        return
    len_data = len(data)
    """
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
    #"""
    count = 1
    all_count = False
    if len_data == 4:
        if data[3] == 'all':
            all_count = True
        else:
            try:
                count = abs(int(data[3]))
            except:
                await message.channel.send('"'+data[3]+'" is not a valid number.')
                return
        len_data -= 1
    if len_data == 3:
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
        if all_count:
            count = player.hand.count(cardtype)
        for i in range(count):
            discard_count = 0
            for action in player.actions:
                if action[1] == 0 and action[2] == cardtype:
                    discard_count += 1
            if discard_count >= player.hand.count(cardtype):
                await message.channel.send('You cannot discard any more '+Colors[cardtype%10]+" "+Actions[int(cardtype/10)]+' cards.')
            elif not Game.NIGHT and len(player.actions) >= player.discard:
                await message.channel.send("You don't have to discard any more cards.")
                break
            else:
                await message.channel.send('Discarding a '+Colors[cardtype%10]+" "+Actions[int(cardtype/10)]+" card.")
                player.actions.append([player.ID,0,cardtype])
        await Show(Game, message, ['!show', 'actions'])
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
    if not player.electable:
        if player.lives <= 0:
            await message.channel.send("Dead players can't vote.")
        else:
            await message.channel.send(player.name + " has already been Consul.")
        return
    if message.channel.id != Channels['senate-floor']:
        await message.channel.send("You may only vote in <#" + str(Channels['senate-floor']) + ">.")
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
    log_channel = client.get_channel(Channels['senate-log'])
    if message.author.id == NARRATOR:
        if len(data) != 2:
            await message.channel.send('Unrecognized use of the "!start" command.')
        elif data[1] == 'game':
            if Game.ON:
                await message.channel.send("The Game has already started.")
            elif Game.pn < 2:
                await message.channel.send("There must be at least 2 Players.")
            else:
                Game.deal(4)
                Game.ON = True
                await message.channel.send("Let the Games Begin.")
                report = "**GAME START**\n"
                for i in range(Game.pn-2):
                    report += Game.Players[i].discordID + ", "
                report += Game.Players[-2].discordID + " & " + Game.Players[-1].discordID + " Playing.\n"
                report += "<@!" + str(NARRATOR) + "> and <@!" + str(ME) + "> Narrating.\n"
                report += "There are 3 Teams with " + str(Game.pn//3) + " Players per Team."
                await log_channel.send(report)
                for i in range(Game.pn):
                    player = Game.Players[i]
                    player_channel = client.get_channel(Channels[player.chatroom])
                    if player.team == -1:
                        await player_channel.send(player.discordID + " you are Neutral. Survive to win!")
                    else:
                        await player_channel.send(player.discordID + " you are on Team #" + str(player.team+1) + ". Find your Teammates!")
        elif not Game.ON:
            await message.channel.send('The game has not Started.')
        elif data[1] == 'end':
            if not Game.ON:
                await message.channel.send("The Game has not started.")
            else:
                await message.channel.send("Ending the Game.")
                await log_channel.send("**GAME OVER**")
        elif data[1] == 'night':
            if not Game.NIGHT:
                Game.save('day')
                await message.channel.send("Starting Night Cycle.")
                await log_channel.send('The Night Cycle has Begun.')
                report = '**VOTING IS CLOSED.**\n'
                tally = [0]*Game.pn
                for player in Game.Players:
                    if player.lives > 0:
                        if player.votes[0] == player.votes[1] == player.votes[2] == -1:
                            continue
                        vote = player.votes[0]
                        count = player.votes.count(vote)
                        report += player.discordID + " cast " + vote_report(Game, count, vote)
                        tally[vote] += count
                        if player.votes[0] != player.votes[1]:
                            vote = player.votes[1]
                            count = player.votes.count(vote)
                            report += " and " + vote_report(Game, count, vote)
                            tally[vote] += count
                        if player.votes[2] != player.votes[0] and player.votes[2] != player.votes[1]:
                            vote = player.votes[2]
                            count = player.votes.count(vote)
                            report += " and " + vote_report(Game, count, vote)
                            tally[vote] += count
                        report += '.\n'
                await log_channel.send(report)
                high = 0
                index = -1
                report = '**FINAL TALLY:**\n'
                for i in range(Game.pn):
                    if tally[i] > 0:
                        report += '**' + Game.Players[i].discordID + ': '+str(tally[i])+'**\n'
                        if tally[i] > high:
                            index = i
                            high = tally[i]
                        elif tally[i] == high:
                            index = -1
                if index == -1:
                    report += '**Vote is Tied.**'
                else:
                    report += '**'+Game.Players[index].discordID+' is Elected.**'
                    Game.Players[index].electable = 0
                await log_channel.send(report)
                Game.startNight()
            else:
                await message.channel.send('It is already night.')
        elif data[1] == 'day':
            master_channel = client.get_channel(Channels['bot-commands'])
            if Game.NIGHT:
                Game.save('night')
                await message.channel.send("Starting Day Cycle.")
                await log_channel.send('The Day Cycle has Begun.')
                report = "Here's the Nightly Report:\n"
                for player in Game.Players:
                    report += player.name + ':\n' + player.printableActions() + '\n'
                await send_large_message(master_channel, report, "\n.")

                for i in range(Game.pn):
                    target = Game.Players[i]
                    health = 0
                    stabbed = False
                    report = ""
                    for player in Game.Players:
                        count = 0
                        for action in player.actions:
                            if action[1] in [10,11,12,13] and action[2] == target.ID:
                                health -= 1
                                count += 1
                        if count >= 1:
                            stabbed = True
                            report += player.discordID+ " played "
                            for i in range(count):
                                report +=  Cards[10] + ' '
                            report += "on " + target.discordID + ".\n"
                    for player in Game.Players:
                        count = 0
                        for action in player.actions:
                            if action[1] in [30,31,32,33] and action[2] == target.ID:
                                health += 1
                                count += 1
                        if count >= 1 and stabbed:
                            report += player.discordID+ " played "
                            for i in range(count):
                                report +=  Cards[30] + ' '
                            report += "on " + target.discordID + ".\n"
                    if stabbed and target.shields > 0:
                        report += target.discordID + " carried "
                        for i in range(target.shields):
                            report += Cards[30] + ' '
                            health += 1
                        report += "from last Night.\n"
                    report += "**"
                    if health < 0:
                        target.shields = 0
                        target.lives += health
                        report += target.discordID + " takes " + str(-health) + " damage"
                        if target.lives <= 0:
                            report += " and Dies"
                            target.dies()
                    elif health >= 2:
                        target.shields = health - 1
                        if stabbed:
                            report += target.discordID + " takes no damage and carries "
                        else:
                            report += target.discordID + " carries "
                        for i in range(health-1):
                            report += Cards[30] + ' '
                        report += "to the next Night"
                    else:
                        target.shields = 0
                        if stabbed:
                            report += target.discordID + " takes no damage"
                    if report != "**":
                        report += ".**\n.\n"
                        await send_large_message(log_channel, report, ".\n")
                    
                
                Game.startDay()
            else:
                await message.channel.send('It is already day.')
        else:
            await message.channel.send('Unrecognized use of the "!start" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

def vote_report(Game, count, vote):
    if count > 1:
        return str(count) + " votes for " + Game.Players[vote].discordID
    return str(count) + " vote for " + Game.Players[vote].discordID

async def send_large_message(master_channel, report, cutter):
    if len(report) < 2000:
        await master_channel.send(report)
    else:
        precut = 0
        postcut = 0
        for i in range((len(report)//1000)):
            postcut = report[900+(1000*i):1100+(1000*i)].index(cutter) + 900 + (i*1000)
            await master_channel.send(report[precut:postcut])
            precut = postcut
        await master_channel.send(report[precut:])

async def Award(Game, message, data):
    if message.author.id == NARRATOR:
        len_data = len(data)
        if len_data == 2 or len_data == 3:
            player = Game.findPlayer(data[1])
            if player == '':
                await message.channel.send("Could not find player \"" + data[1] + "\".")
                return
            if player.lives <= 0:
                if len_data == 2:
                    await message.channel.send("Gave " + Cards[10] + " to " + player.name + ".")
                    player.giveCard(10)
                else:
                    await message.channel.send("Cannot award multiple cards to Dead Players.")
                return
            count = 1
            if len_data == 3:
                try:
                    count = abs(int(data[2]))
                except:
                    await message.channel.send('"'+data[3]+'" is not a valid integer.')
                    return
            return_message = ""
            for i in range(count):
                return_message += Game.giveCard(player) + '\n'
            await message.channel.send(return_message)
        else:
            await message.channel.send('Unrecognized use of the "!award" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Save(Game, message, data):
    if message.author.id == NARRATOR:
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
    if message.author.id == NARRATOR:
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
                await message.channel.send('Loaded "'+ data[1] +'.txt"')
        else:
            await message.channel.send('Unrecognized use of the "!load" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

result = 'No result.'
async def Report(Game, message, data):
    if message.author.id == NARRATOR:
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
        await message.channel.send("Only <@!"+str(NARRATOR)+"> can run the '!report' command.")

async def Control(Game, message, data):
    if message.author.id == NARRATOR:
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
        elif len_data == 4 and data[1] == 'shields':
            target = Game.findPlayer(data[2])
            if target == '':
                await message.channel.send("Couldn't find player"+' "'+data[2]+'"')
                return
            try:
                shields = abs(int(data[3]))
                target.shields = shields
                await message.channel.send("Set "+target.name+"'s shields to "+str(shields)+'.')
            except:
                await message.channel.send('"'+data[3]+'" is not a valid integer.')
        else:
            await message.channel.send('Unrecognized use of the "!control" command.')
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Exit(Game, message, data):
    if message.author.id == NARRATOR:
        await message.channel.send("Goodbye!")
        Game.save('exit')
        exit(0)
    else:
        await message.channel.send("Only the Narrator can use that command.")

async def Test(Game, message, data, client):
    for player in Game.Players:
        if player.discordID != 0:
            await client.get_channel(Channels[player.chatroom]).send(player.discordID + ' Dinner is Ready.')
        else:
            await message.channel.send(player.name+' has no listed DiscordID.')

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        #musings = self.get_channel(Channels['bot-commands'])
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
                    if player.discordID[0:2] != "<@!":
                        player.discordID = "<@!" + str(message.author.id) + ">"
                elif Game.ON and message.author.id != NARRATOR:
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
                elif data[0] == '!award':
                    await Award(Game, message, data)
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
                if message.content == '!exit' and message.author.id == NARRATOR:
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
