
def save(filename, Game):
    File = open('saves/'+filename+'.txt', 'w')
    File.write('Game\n')
    if Game.ON:
        File.write('1 ')
    else:
        File.write('0 ')
    if Game.NIGHT:
        File.write('1')
    else:
        File.write('0')
    File.write('\n'+str(Game.decksize)+'\n')
    for card in Game.Deck:
        File.write(str(card)+' ')
    File.write('\n')
    
    File.write(str(Game.pn) + '\n')
    for player in Game.Players:
        File.write('Player\n')
        File.write(player.name+'\n')
        File.write(player.nick+'\n')
        File.write(player.chatroom+'\n')
        File.write(player.disc+'\n')
        File.write(str(player.tag)+'\n')
        File.write(str(player.team)+' '+str(player.lives)+' '+str(player.color)+'\n')
        File.write(str(player.discard)+'\n')
        File.write(str(player.handsize)+'\n')
        for card in player.hand:
            File.write(str(card)+' ')
        File.write('\n')
        for vote in player.votes:
            File.write(str(vote)+' ')
        File.write('\n')
        for action in player.actions:
            File.write("Action "+str(action[0])+' '+str(action[1])+' '+str(action[2])+'\n')
    File.close()

def load(filename, Game):
    File = open('saves/'+filename+'.txt', 'r')
    if File.readline() != 'Game\n':
        print('Wrong File.')
        return
    line = File.readline()
    if line[0] == '1':
        Game.ON = True
    else:
        Game.ON = False
    if line[2] == '1':
        Game.NIGHT = True
    else:
        Game.NIGHT = False
    Game.decksize = int(File.readline())
    line = File.readline().split(' ')
    line.remove('\n')
    for i in range(len(line)):
        Game.Deck[i] = int(line[i])
    Game.pn = int(File.readline())
    line = File.readline()
    Game.Players = []
    for i in range(Game.pn):
        if line != 'Player\n':
            print("Something went wrong.")
            return
        name = File.readline()
        nick = File.readline()
        room = File.readline()
        disc = File.readline()
        tag = File.readline()
        Game.addPlayer(name[:len(name)-1],
                       room[:len(room)-1],
                       nick[:len(nick)-1],
                       disc[:len(disc)-1],
                       int(tag),
                       i)
        player = Game.Players[-1]
        line = File.readline().split(' ')
        player.team = int(line[0])
        player.lives = int(line[1])
        player.color = int(line[2])
        player.discard = int(File.readline())
        player.handsize = int(File.readline())
        line = File.readline().split(' ')
        for i in range(player.handsize):
            player.hand[i] = int(line[i])
        line = File.readline().split(' ')
        for i in range(player.lives):
            player.votes[i] = int(line[i])
        line = File.readline()
        while line[0:6] == 'Action':
            action = line[7:].split(' ')
            player.actions.append([int(action[0]),int(action[1]),int(action[2])])
            line = File.readline()
