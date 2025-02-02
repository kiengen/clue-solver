# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 19:40:57 2024
"""
#  1 = has card
#  0 = doesn't have card
# -1 = unsure

import copy
import csv

# import csv
# just for testing purposes (can be deleted later)
turns = []
"""with open('clue_data.csv') as f:
    allClueData = csv.DictReader(f)
    for line in allClueData:
        turns.append([line['Guesser'], line['Location'], line['Suspect'], line['Tool'], line['Helper'], line['']])"""

card_template = {"person": {"Mustard": -1, "Scarlett": -1, "Green": -1, "Plum": -1, "Orchid": -1, "Peacock": -1},
                 "item": {"Candlestick": -1, "Dagger": -1, "Lead Pipe": -1, "Revolver": -1, "Rope": -1, "Wrench": -1},
                 "place": {"Ballroom": -1, "Billiard Room": -1, "Conservatory": -1, "Dining Room": -1, "Hall": -1, "Kitchen": -1, "Library": -1, "Lounge": -1, "Study": -1}}

# to be filled in with our version's cards
"""card_template = {"person": {},
                 "item": {},
                 "place": {}}"""

finals = copy.deepcopy(card_template)
final_three = {"item":"", "person":"", "place":""}

opponent_card_counts = {}
opponent_card_finals = {}

history = []

valid_responses = {"type": ["person", "item", "place"], "person": ['done', 'quit',], "item": ['done', 'quit',], "place": ['done', 'quit',], "any": []}
for item_type in card_template.keys():
    for term in card_template[item_type].keys():
        valid_responses[item_type].append(term)
        valid_responses["any"].append(term)

def displayCard():
    print("")
    row = "               "
    for player in players:
        row += " "+player[:5]+" "*(5-len(player))+" "
    print(row)
    for type_key in card_template.keys():
        row = ""
        print(type_key+" "+"="*(14-len(type_key))+"="*len(players)*7)
        for item_key in card_template[type_key].keys():
            row += item_key
            row += " "*(14-len(item_key))+"|"
            for player in players:
                row += "   "
                if(opponent_cards[player][type_key][item_key] == -1):
                    row_mod = ""
                    # have they responded to it? (will put a number based on who asked)
                    for group in history:
                        if group[1] in opponent_card_finals[player] or group[2] in opponent_card_finals[player] or group[3] in opponent_card_finals[player]:
                            pass
                        else:
                            if item_key in group[1:4] and group[4] == player and group[0] != 'me':
                                row_mod += str(players.index(group[0])+1)
                    if len(row_mod) == 0:
                        row_mod += " "
                        #print(len(row))
                    # ? if there are 3+
                    elif len(row_mod) > 2:
                        row_mod = "?"
                    row += row_mod
                elif(opponent_cards[player][type_key][item_key] == 1):
                    row += "@"
                elif(opponent_cards[player][type_key][item_key] == 0):
                    row += "x"
                row += " "*(8-(len(row)%7))
                #row += "   "
            if(len(finals[type_key]) == 1 and item_key in finals[type_key].keys()):
                row += " <--"
            print(row)
            row = ""

# makes sure input is valid + requeries as necessary
def validateInput(item_type, message):
    response = input(message)
    while(not (response in valid_responses[item_type])):
        print("Item not recognized.")
        response = input(message)
    return response

def typeOf(item):
    for type_key in valid_responses.keys():
        if(item in valid_responses[type_key]):
            return type_key
    return "UNKOWN_VALUE"


# player has item of type item_type
def theyHave(player, item_type, item):
    global players
    global opponent_cards
    if(opponent_cards[player][item_type][item] == -1):
        print("-- "+player+" determined to have "+item+"!")
        opponent_card_finals[player]. append(item)
    opponent_cards[player][item_type][item] = 1
    if(item in finals[item_type].keys()):
        del finals[item_type][item]
    for temp_player in players:
        if(player != temp_player):
            opponent_cards[temp_player][item_type][item] = 0

def checkSet(potential_set, opponent_sets):
    for turn in opponent_sets:
        one_works = False
        for key_type in turn.keys():
            if(turn[key_type] in potential_set):
                one_works = True
        if(not one_works):
            return False
    return True

def analyzeDecks():
    global finals
    temp_finals = copy.deepcopy(finals)
    
    # look through each of the sets and check for isolated possibilities
    global opponent_sets
    temp_sets = copy.deepcopy(opponent_sets)
    for player in players:
        group_index = len(opponent_sets[player]) - 1
        current_index_deleted = False
        while group_index >= 0:
            for item_key in opponent_sets[player][group_index].keys():
                if current_index_deleted == False and opponent_cards[player][item_key][opponent_sets[player][group_index][item_key]] == 0:
                    #print("-- deleted "+player+"'s "+item_key+" from a set ("+temp_sets[player][group_index][item_key]+")")
                    del temp_sets[player][group_index][item_key]
                # loses its significance if player is confirmed to have at least one item in the set
                elif current_index_deleted == False and opponent_cards[player][item_key][opponent_sets[player][group_index][item_key]] == 1:
                    del temp_sets[player][group_index]
                    current_index_deleted = True
            # player must have last item if they can't have other two
            if(current_index_deleted == False and len(temp_sets[player][group_index]) == 1):
                theyHave(player, list(temp_sets[player][group_index].keys())[0], list(temp_sets[player][group_index].values())[0])
                del temp_sets[player][group_index]
                
            group_index -= 1
    opponent_sets = temp_sets
    
    # card count logic
    # count tiles for which there is a possibility and tiles that are certainly theirs
    all_player_working_sets = {}
    for player in players:
        if(not player in done_players):
            possible_keys = []
            certain_keys = []
            for item_type_key in opponent_cards[player].keys():
                for item_key in opponent_cards[player][item_type_key].keys():
                    if(opponent_cards[player][item_type_key][item_key] == -1):
                        possible_keys.append([item_type_key, item_key])
                    elif(opponent_cards[player][item_type_key][item_key] == 1):
                        certain_keys.append([item_type_key, item_key])
            # if there are only the number of cards they have left that are possible, they must all be theirs
            if(len(possible_keys) + len(certain_keys) == opponent_card_counts[player]):
                for key_pair in possible_keys:
                    theyHave(player, key_pair[0], key_pair[1])
            # if they already have three, they can't have any others
            if(len(certain_keys) == opponent_card_counts[player]):
                for key_pair in possible_keys:
                    opponent_cards[player][key_pair[0]][key_pair[1]] = 0
                print("-- all of "+player+"'s cards determined!")
                done_players.append(player)
            
            # I couldn't use the previous set iterator, so I have to make a new one... :
            possible_set_keys = []
            for turn in opponent_sets[player]:
                for key_type in turn.keys():
                    if(not turn[key_type] in possible_set_keys):
                        possible_set_keys.append(turn[key_type])
            
            
            possible_set_keys = []
            for pair in possible_keys:
                if not pair[1] in possible_set_keys:
                    possible_set_keys.append(pair[1])
            
            # this isn't actually that complex
            # just go through and see which potentialities could explain every set.
            working_set = []
            worked = False
            cards_left = opponent_card_counts[player] - len(certain_keys)
            potential_set = []
            #print("possible_keys: "+str(possible_keys))
            #print("possible_set_keys: "+str(possible_set_keys))
            
            def permutation_func(prev_key, recur_level):
                if(cards_left > recur_level):
                    for key_index in range(prev_key+1):
                        potential_set.append(possible_set_keys[key_index])
                        permutation_func(key_index, recur_level + 1)
                else:
                    worked = checkSet(potential_set, opponent_sets[player])
                    if(worked == True):
                        working_set.append(copy.deepcopy(potential_set))
                if(recur_level > 0):
                    potential_set.pop(recur_level - 1)
            
            if(cards_left > 0 and len(opponent_sets[player]) >= cards_left):
                permutation_func(0, 0)

            permutation_func(len(possible_set_keys)-cards_left, 0)
            
            # if all sets of working_sets share a single thing (or multiple things),
            # they must have the shared thing(s)
            #if(working_set != [] and len(opponent_sets[player]) > cards_left):
            if(working_set != []):
                all_player_working_sets[player] = working_set
            if(working_set != [] and len(opponent_sets[player]) > cards_left):
                for index in range(len(working_set[0])):
                    item = working_set[0][index]
                    works = True
                    for group in working_set:
                        if(not item in group):
                            works = False
                            break
                    if(works == True):
                        theyHave(player, typeOf(item), item)
                        print("BOOYAH!")
        
    # just to make things more difficult, now go through all the working sets for each player and
    # see if there is any set that doesn't actually work because it would make the other players' sets
    # not work
    # TODO         
    
    # if nobody has it, it's the final one!
    # iterates through people
    for item_key in finals["person"].keys():
        if(final_three["person"] == ""):
            num_possible = 0
            for player in players:
                if opponent_cards[player]["person"][item_key] == -1:
                    num_possible += 1
                elif opponent_cards[player]["person"][item_key] == 1:
                    num_possible += 1
                    del temp_finals["person"][item_key]
            if(num_possible == 0):
                print("!! FINAL person determined to be "+item_key+"!")
                temp_finals["person"].clear()
                temp_finals["person"][item_key] = 1
                final_three["person"] = item_key
    
    # iterates through items
    for item_key in finals["item"].keys():
        if(final_three["item"] == ""):
            num_possible = 0
            for player in players:
                if opponent_cards[player]["item"][item_key] == -1:
                    num_possible += 1
                elif opponent_cards[player]["item"][item_key] == 1:
                    num_possible += 1
                    del temp_finals["item"][item_key]
            if(num_possible == 0):
                print("!! FINAL item determined to be "+item_key+"!")
                temp_finals["item"].clear()
                temp_finals["item"][item_key] = 1
                final_three["item"] = item_key
    
    # iterates through places
    for item_key in finals["place"].keys():
        if(final_three["place"] == ""):
            num_possible = 0
            for player in players:
                if opponent_cards[player]["place"][item_key] == -1:
                    num_possible += 1
                elif opponent_cards[player]["place"][item_key] == 1:
                    num_possible += 1
                    del temp_finals["place"][item_key]
            if(num_possible == 0):
                print("!! FINAL place determined to be "+item_key+"!")
                temp_finals["place"].clear()
                temp_finals["place"][item_key] = 1
                final_three["place"] = item_key
    
    # if it's the last one, it's the final
    for card_type_key in temp_finals.keys():
        if(final_three[card_type_key] == ""):
            if(len(temp_finals[card_type_key]) == 1):
                for player in players:
                    opponent_cards[player][card_type_key][list(temp_finals[card_type_key].keys())[0]] = 0
    finals = temp_finals
    
    if(len(finals["person"]) + len(finals["item"]) + len(finals["place"]) == 3):
        print("\n\nEUREKA! IT'S "+list(finals["person"].keys())[0]+", with the "+list(finals["item"].keys())[0]+", in the "+list(finals["place"].keys())[0]+"!")
            

def suggestGuess():
    analyzeDecks()
    displayCard()
    """prospects = copy.deepcopy(finals)
    # NEVER guess one that is known
    for item_type in prospects:
        for item in prospects[item_type]:
            if item.values()[0] == 0 or item.values()[0] in players:
                del prospects[]"""
    # place a preference on items where you know the latter half but not the half near you
    
    pass

print("WELCOME TO PYTHON CLUE")
numPlayers = input("How many people are playing?\n  >> ")
players = []
done_players = []

print("Enter each name in seating order, starting with the player to your left and working clockwise.")
# gets names of all players
for i in range(int(numPlayers)-1):
    temp_name = input(str("Player "+str(i+1)+" name:\n  >> "))
    players.append(temp_name)

# gets number of cards each other player has
opponent_cards = {}
opponent_sets = {}
for player in players:
    numCards = input(str("How many cards was "+player+" dealt?\n  >> "))
    opponent_card_counts[player] = int(numCards)
    opponent_cards[player] = copy.deepcopy(card_template)
    opponent_sets[player] = []
    opponent_card_finals[player] = []

# gets cards of main player
numCards = input("How many cards were you dealt?\n  >> ")
player_cards = copy.deepcopy(card_template)
for i in range(int(numCards)):
    card_type = validateInput("type", "Type of next card: (person/place/item)\n  >> ")
    card_name = validateInput("any", "Card name:\n  >> ")
    player_cards[card_type][card_name] = 1
    for j in players:
        opponent_cards[j][card_type][card_name] = 0
    del finals[card_type][card_name]
    
# gets any public cards
numCards = input("How many public cards are there?\n  >> ")
#opponent_cards["public"] = copy.deepcopy(card_template)
for i in range(int(numCards)):
    card_type = input("Type of next card: (person/place/item)\n  >> ")
    card_name = validateInput("any", "Card name:\n  >> ")
    player_cards[card_type][card_name] = 1
    for j in players:
        opponent_cards[j][card_type][card_name] = 0
    del finals[card_type][card_name]

# for now, it's the same
numPlayers = 6
players = ["Peacock", "Plum", "Mustard", "Orchid", "Scarlett"]
done_players = []

# gets number of cards each other player has
opponent_card_counts = {"Peacock":3, "Plum":3, "Mustard":3, "Orchid":3, "Scarlett":3}
opponent_cards = {}
opponent_sets = {}
for player in players:
    opponent_cards[player] = copy.deepcopy(card_template)
    opponent_sets[player] = []
    opponent_card_finals[player] = [""]*opponent_card_counts[player]

# gets cards of main player
numCards = 3
player_cards = copy.deepcopy(card_template)
card_types = ["person", "place", "place"]
card_names = "Mustard", "Conservatory", "Dining Room"
for i in range(int(numCards)):
    #card_type = validateInput("type", "Type of next card: (person/place/item)\n  >> ")
    #card_name = validateInput("any", "Card name:\n  >> ")
    card_type = card_types[i]
    card_name = card_names[i]
    player_cards[card_type][card_name] = 1
    for j in players:
        opponent_cards[j][card_type][card_name] = 0
    del finals[card_type][card_name]

# -------------------------------------
# |           SETUP DONE              |
# -------------------------------------
print("\nAwesome! Let's start.")
round_num = 0
# True: automatic, False: manual
while(True and round_num < len(turns)-1):
    guesser, place, person, item, player_who_helped, card = turns[round_num]
    print("\n"+str(round_num)+". "+guesser+" suspected "+person+" with the "+item+" in the "+place)
    input(player_who_helped+" helped")
    
    if(player_who_helped == 'no'):
        couldnthelpslice = players[:]
        if(guesser != 'me'):
            couldnthelpslice.remove(guesser)
    elif(player_who_helped != "me"):
        if(guesser == 'me'):
            if(card == person):
                theyHave(player_who_helped, "person", card)
            elif(card == item):
                theyHave(player_who_helped, "item", card)
            elif(card == place):
                theyHave(player_who_helped, "place", card)
            couldnthelpslice = players[0:players.index(player_who_helped)]
        else:
            opponent_sets[player_who_helped].append({"person": person, "item": item, "place": place})
            if(players.index(player_who_helped) > players.index(guesser)):
                couldnthelpslice = players[players.index(guesser)+1:players.index(player_who_helped)]
            else:
                if(len(players[:players.index(player_who_helped)])):
                    couldnthelpslice = players[:players.index(player_who_helped)]
                if(len(players[players.index(guesser)+1:]) > 0):
                    couldnthelpslice.extend(players[players.index(guesser)+1:])
    else:
        couldnthelpslice = players[players.index(guesser)+1:]

    for player in couldnthelpslice:
        opponent_cards[player]["person"][person] = 0
        opponent_cards[player]["place"][place] = 0
        opponent_cards[player]["item"][item] = 0
    
    if(guesser == 'me'):
        history.append([guesser, place, person, item, player_who_helped, card])
    else:
        history.append([guesser, place, person, item, player_who_helped])
    analyzeDecks()
    analyzeDecks()
    if(round_num % 5 == 4):
        displayCard()
    round_num += 1


while(False):
    guesser = input("=====\nWhose turn is it to guess?  >> ")
    turn_done = False
    if(guesser == 'me'):
        suggestGuess()
    if(guesser == 'me' or guesser in players):
        while(turn_done == False):
            #print("Say 'quit' at any point to start over (same guesser). Say 'done' to leave player guess phase (new guesser).")
            #print("guesser: "+guesser)
            place = validateInput("place", "location: >> ")
            if(place == 'done'):
                turn_done = True
            elif(place != 'quit'):
                person = validateInput("person", "person:   >> ")
                if(person == 'done'):
                    turn_done = True
                elif(person != 'quit'):
                    item = validateInput("item", "item:     >> ")
                    if(item == 'done'):
                        turn_done = True
                    elif(item != 'done'):
                        
                        couldnthelpslice = []
                        if(True):
                            player_who_helped = input("Which player helped? (put no if nobody helped)  >> ")
                            if(player_who_helped == "done"):
                                turn_done = True
                                break
                            elif(player_who_helped == 'quit'):
                                break
                            elif(player_who_helped == 'no'):
                                couldnthelpslice = players[:]
                                if(guesser != 'me'):
                                    couldnthelpslice.remove(guesser)
                            elif(player_who_helped != "me"):
                                if(guesser == 'me'):
                                    card = validateInput("any", "What card did they show you?  >> ")
                                    if(card == person):
                                        theyHave(player_who_helped, "person", card)
                                    elif(card == item):
                                        theyHave(player_who_helped, "item", card)
                                    elif(card == place):
                                        theyHave(player_who_helped, "place", card)
                                    couldnthelpslice = players[0:players.index(player_who_helped)]
                                else:
                                    opponent_sets[player_who_helped].append({"person": person, "item": item, "place": place})
                                    if(players.index(player_who_helped) > players.index(guesser)):
                                        couldnthelpslice = players[players.index(guesser)+1:players.index(player_who_helped)]
                                    else:
                                        if(len(players[:players.index(player_who_helped)])):
                                            couldnthelpslice = players[:players.index(player_who_helped)]
                                        if(len(players[players.index(guesser)+1:]) > 0):
                                            couldnthelpslice.extend(players[players.index(guesser)+1:])
                            else:
                                couldnthelpslice = players[players.index(guesser)+1:]
                        
                        for player in couldnthelpslice:
                            opponent_cards[player]["person"][person] = 0
                            opponent_cards[player]["place"][place] = 0
                            opponent_cards[player]["item"][item] = 0
                        if(guesser == 'me'):
                            history.append([guesser, place, person, item, player_who_helped, card])
                        else:
                            history.append([guesser, place, person, item, player_who_helped])
                        turn_done = True
        analyzeDecks()
        analyzeDecks()
    else:
        print("Name not recognized. Try again.")
