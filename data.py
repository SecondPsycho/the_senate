import random
import memory

#    20 : '<:glassR:743884188612296704>',
#    21 : '<:glassB:743884188666691735>',
#    22 : '<:glassG:743884188150792293>',

Cards = {
    0 : '',
    11 : '<:knifeR:743884189044310046>',
    12 : '<:knifeG:743884188817817711>',
    13 : '<:knifeB:743884188784132256>',
    21 : '<:coinsR:815407541349122048>',
    22 : '<:coinsG:815407486404001802>',
    23 : '<:coinsB:815407485958488065>',
    31 : '<:guardR:743884188704440440>',
    32 : '<:guardG:743884188687663146>',
    33 : '<:guardB:743884188305981481>'
}

Colors = ['','red','green','blue']
Actions = ['','murder','tax','guard']

Channels = {
    'bot-tests' : 812334133551431741,
    'narrator-musings' : 743890837653553232,
    'island-palace' : 743897238476161036,
    'arctic-palace' : 743891278793801878,
    'mountain-palace' : 743891354412908626,
    'clockwork-palace' : 743899239607828600,
    'garden-palace' : 743891076363976784,
    'starlight-palace' : 743898836417642598,
    'cloud-palace' : 743891371835785276,
    'desert-palace' : 743897321787359355,
    'ocean-palace' : 743891308577292420,
    'jungle-palace' : 743891329603600424,
    'cavern-palace' : 743898732256296980,
    'volcanic-palace' : 743898898443272255,
    'industrial-palace' : 815592342131179570,
    'graveyard-palace' : 815431320872288306
}

class NewGame():
    def __init__(self):
        self.ON = False
        self.NIGHT = False
        self.new_deck()
        self.pn = 0
        self.Players = []
    def reset(self):
        self.ON = False
        self.NIGHT = False
        self.new_deck()
        self.pn = 0
        self.Players = []
    def newPlayer(self,message):
        for player in self.Players:
            if player.name == message.author.name:
                return False
        self.Players.append(Player(self,
                                   message.author.name,
                                   message.channel.name,
                                   message.author.nick,
                                   message.author.discriminator,
                                   message.author.id,
                                   self.pn))
        self.pn += 1
        return True
    def addPlayer(self, name, room, nick, disc, tag, ID):
        self.Players.append(Player(self,name,room,nick,disc,tag,ID))
    def getPlayer(self,name):
        for player in self.Players:
            if player.name == name:
                return player
        return ''
    def findPlayer(self,name):
        name = name.lower()
        for player in self.Players:
            if name == player.name.lower():
                return player
        for player in self.Players:
            if name == player.nick.lower():
                return player
        for player in self.Players:
            if name in player.name.lower() or name in player.nick.lower():
                return player
        return ''
    def removePlayer(self,name):
        player = self.getPlayer(name)
        if player == '':
            return False
        else:
            self.Players.remove(player)
            self.pn -= 1
            return True
    def deal(self, handsize):
        self.new_deck()
        teams = [0,0]
        tn = int(self.pn/2)
        if self.pn % 2 == 1:
            neutral = random.randint(0,self.pn-1)
            self.Players[neutral].team = 2
        else:
            neutral = -1
        for i in range(self.pn):
            if i == neutral:
                continue
            t = random.randint(0,1)
            self.Players[i].team = t
            teams[t] += 1
            if teams[t] == tn:
                if teams[0] == tn:
                    for j in range(i+1,self.pn):
                        if j == neutral:
                            continue
                        self.Players[j].team = 1
                break
        for player in self.Players:
            player.hand[0:handsize] = self.draw(handsize)
            player.handsize = handsize
    def new_deck(self):
        self.Deck = [11,11,12,13,21,22,22,23,31,32,33,33]*5
        self.decksize = 60
    def draw(self, num):
        result = ['']*num
        for i in range(num):
            result[i] = self.drawcard()
        return result
    def drawcard(self):
        self.decksize -= 1
        index = random.randint(0,self.decksize)
        card = self.Deck[index]
        self.Deck[index] = self.Deck[self.decksize]
        self.Deck[self.decksize] = 0
        if self.decksize == 0:
            self.new_deck()
        return card
    def save(self, filename):
        memory.save(filename, self)
    def load(self, filename):
        memory.load(filename, self)
    def startDay(self):
        if not self.NIGHT:
            return False
        self.NIGHT = False
        for player in self.Players:
            player.discard = 0
        for player in self.Players:
            player.votes = [-1,-1,-1]
            while (len(player.actions) > 0 and player.actions[-1][1] == 0):
                player.actions.pop(-1)
            for action in player.actions:
                if action[1] == 0:
                    player.discardCard(action[2])
                elif 20 <= action[1] <= 29:
                    target = self.Players[action[2]]
                    target.discard += 1
                    target.giveCard(self.drawcard())
                    target.giveCard(self.drawcard())
                #Deal with Shields and Stabs later
            player.actions = []
        return True
    def startNight(self):
        if self.NIGHT:
            return False
        self.NIGHT = True
        for player in self.Players:
            while player.discard > 0:
                if len(player.actions) > 0:
                    action = player.actions.pop(0)
                    if action[1] == 0:
                        player.discardCard(action[2])
                        player.discard -= 1
                else:
                    randcard = player.hand[random.randint(0,player.handsize-1)]
                    player.discardCard(randcard)
                    player.discard -= 1
            player.actions = []
            if player.lives > 0:
                player.giveCard(self.drawcard())
        return True


class Player():
    def __init__(self,Game,name,chatroom,nick,disc,tag,ID):
        self.Game = Game
        self.name = name
        self.nick = str(nick)
        self.chatroom = chatroom
        self.disc = disc
        self.tag = tag
        self.ID = ID

        self.team = 0
        self.lives = 3

        self.handsize = 0
        self.hand = [0]*20

        self.votes = [-1,-1,-1]
        self.color = -1
        self.discard = 0
        self.actions = []
    def giveCard(self, card):
        if self.handsize == 20:
            print("Player tried to exceed hand size.",self.name,self.ID,self.card)
            return False
        else:
            self.hand[self.handsize] = card
            self.handsize += 1
            return True
    def discardCard(self, card):
        for i in range(self.handsize):
            if self.hand[i] == card:
                for j in range(i,min(self.handsize,19)):
                    self.hand[j] = self.hand[j+1]
                self.handsize -= 1
                self.hand[self.handsize] = 0
                return True
        return False
    def mustDiscard(self):
        played_count = 0
        discard_count = 0
        for action in self.actions:
            if action[1] == 0:
                discard_count += 1
            else:
                played_count += 1
        if (played_count-discard_count) > 0:
            return True
        return False
    def printableCards(self):
        cards = [0]*self.handsize
        for i in range(self.handsize):
            cards[i] = Cards[self.hand[i]]
        return ' '.join(cards)
    def printableActions(self):
        if len(self.actions) == 0:
            return '    No Actions.\n'
        cards = ''
        for action in self.actions:
            cards += '....'
            if action[1] == 0:
                cards += "discarding "+Cards[action[2]]
            else:
                cards += Cards[action[1]] + " on "+self.Game.Players[action[2]].name+'.'
            cards += '\n'
        return cards

"""
Game = NewGame()
Game.Players = [Player(Game,'Gen_CAT','bot-tests','Mars',' ',1),
                Player(Game,'Player 2','room','nick',' ',2),
                Player(Game,'Player 3','room','nick',' ',3),
                Player(Game,'Player 4','room','nick',' ',4),
                Player(Game,'Player 5','room','nick',' ',5)]
Game.pn = 5
Game.deal(3)
Game.Players[2].actions.append([1,11,2])
Game.ON = True
Game.NIGHT = True

Game.Players[3].votes[1] = 1
Game.save('test')
#"""

