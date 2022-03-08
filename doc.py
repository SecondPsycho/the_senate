from data import Cards
help_join = """
    !join [here]
        Join the game in the current chatroom.
        [here]:
            If already joined, switch to the current chatroom.
        Example:
            !join here
"""

help_unjoin = """
    !unjoin
        Un-join the game.
"""

help_draw = """
    !draw [<number>]
        Draw cards from a deck.
        <number> can be:
            An integer from 1 to 60. 3 by Default.
        Examples:
            !draw
            !draw 5
"""

help_show = """
    !show <key>
        Show information about your current gamestate.
        <key> can be:
            'hand' : show your current cards.
            'actions' : see the actions you're going to play.
            'color' : see what your color is set to.
            'votes' : see what your votes are set to.
            'lives' : see how many lives you have left.
            'guard' : see how many guards you have from last night.
        Example:
            !show hand
"""

#This command no longer implemented
help_set = """
    !set color <color>
        Choose which color of cards you want to play tonight.
        <color> can be:
            'red' : set your color to red.
            'green' : set your color to green.
            'blue' : set your color to blue.
        Example:
            !set color red
"""

help_play = """
    !play <ability> [[on] <target>] [<num>]
        Play an ability card.
        <ability> can be:
            'murder' or 'knife' : play murder card.
            'tax' or 'coin' : play tax card.
            'guard' or 'shield' : play guard card.
        [[on] <target>]:
            Specify another player as a target. Chooses yourself by Default.
        [on]:
            optional.
        <target> can be:
            Any Player's username or nickname.
            'me' or 'myself' : Choose yourself as Target.
        [<num>] can be:
            A number: specify the number of times to repeat this command.
            'all' : play all cards available.
        Examples:
            !play tax
            !play murder on gen_cat
            !play knife on gen_cat
            !play """+Cards[33]+""" on me
            !play shield 2
            !play tax on gen_cat all
"""

help_unplay = """
    !unplay [<num>]
        Undo the last '!play' command. Can be used multiple times to clear multiple plays.
        [<num>] can be:
            A number: clear <num> of plays.
            'all' : clear all plays at once.
        Example:
            !unplay
"""

help_discard = """
    !discard <ability> [<num>]
        Mark a card to be discarded.
        <ability> can be:
            'murder' or 'knife' or 'red' : it's a murder card.
            'tax' or 'coin' or 'green' : it's a tax card.
            'guard' or 'shield' or 'blue' : it's a guard card.
        [<num>] can be:
            A number: specify the number of times to repeat this command.
            'all' : discard all cards available.
        Examples:
            !discard tax
            !discard shield 2
            !discard red all
"""

help_vote = """
    !vote <player>
        Set your votes for a player.
        <player> can be:
            Any Player's username.
            'me' or 'myself' : Vote for yourself.
"""

#"""

help_help = """
    !help [<state>]
        Show available commands. By default, shows commands for the current state.
        [<state>]:
            Show commands for a specific game state.
        <state> can be:
            'join' : Game hasn't started.
            'day' : Day Cycle.
            'night' : Night Cycle.
            'help' : Show how to read help pages.
"""

help_man = """
Commands are shown in the following format:
    !command <argument1> [on <argument2>]
        Here is a description of the command.
        Words (like "command" and "on") should be written letter-for letter,
        Arguments in braces "<>" should be replaced by something indicating your intention, and
        Brackets "[]" indicate something is optional. It may have a Default value if not included.
        <argument1> can be:
            'option1' : Something to replace <argument1> with.
            'option2' : Something to replace <argument1> with.
        [on <argument2>]:
            Description of what this optional segment does.
        <argument2> can be:
            'choice1' : Something to replace <argument2> with.
            'choice2' : Something to replace <argument2> with.
            'choice3' : Something to replace <argument2> with.
    Examples:
        !command option1 on
        !command option2 on choice3
"""

help_plug = """
Use '!help help' for instructions on reading help pages."""

help_JOIN = help_join+help_unjoin+help_draw+help_plug
help_NIGHT1 = help_show+help_discard
help_NIGHT2 = help_play+help_unplay+help_plug
help_DAY = help_show+help_vote+help_discard+help_plug
help_HELP = help_man+help_help
