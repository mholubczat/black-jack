from card import Deck
from player import Player

decks = 2


def getPoints(hand):
    points = 0
    has_ace = False
    for next_card in hand["cards"]:
        if next_card.rank == 'ace':
            has_ace = True
            points += 1
        else:
            points += next_card.points
    if has_ace and points + 10 <= 21:
        points += 10
    return points


def menu():
    print("1 - New Game")
    print(f"2 - Change number of decks (currently {decks})")


def getPlayers(players):
    next_player = True
    player_name: str = input("Enter player name")
    players.append(Player(player_name))
    if input("Add next player? (y/n) ").lower() == "n":
        next_player = False
    while next_player and len(players) < 5:
        player_name: str = input("Enter player name")
        players.append(Player(player_name))
        if input("Add next player? (y/n) ").lower() == "n":
            next_player = False


def select_action(same):
    correct = False
    while not correct:
        print("Select action:")
        print("HIT (take a card)")
        print("STAND (pass)")
        print("DOUBLE (take final card, double the stake)")
        if same:
            print("SPLIT")
        print("SURRENDER")
        action = input()
        correct = (action == "HIT"
                   or action == "STAND"
                   or action == "DOUBLE"
                   or (action == "SPLIT" and same)
                   or action == "SURRENDER")
    return action


def selectInsuranceAction(player):
    correct = False
    bj = getPoints(player.hands[0]) == 21
    while not correct:
        print("Select action:")
        print("INSURANCE")
        if bj:
            print("EVEN MONEY")
        print("PASS (no insurance)")
        action = input()
        correct = (action == "INSURANCE"
                   or action == "PASS"
                   or (action == "EVEN MONEY" and bj))
    player.hands[0].lastAction = action


def selectActionsForSubsequentHands(player, deck):
    i = 0
    while i < len(player.hands):
        hand = player.hands[i]
        if (hand['lastAction'] == "STAND" or hand['lastAction'] == "DOUBLE" or hand['lastAction'] == "SURRENDER"
                or hand['lastAction'] == "EVEN MONEY" or hand['lastAction'] == "PAID INSURANCE" or hand['lastAction'] == "BUST"):
            i += 1
            continue
        print(f"{player} hand {i + 1} of {len(player.hands)} is played. Bid: {hand['bid']} Cards: ")
        for c in hand["cards"]:
            print(c)
        same = hand["cards"][0].points == hand["cards"][1].points and len(hand["cards"]) == 2
        action = select_action(same)
        hand['lastAction'] = action
        if action == "HIT":
            dealt_card = deck.dealCard()
            hand["cards"].append(dealt_card)
            print(f"{player} gets {dealt_card}. Points {getPoints(hand)}")
            if getPoints(hand) > 21:
                hand['lastAction'] = "BUST"
                print(f"{player} is busted! His bid {hand['bid']} is lost")
                player.credits -= hand['bid']
                i += 1
            continue
        if action == "STAND":
            print(f"{player} stands. Final points {getPoints(hand)}")
        if action == "DOUBLE":
            if player.credits - hand['bid'] < hand['bid']:
                print(f"{player} cannot afford to double")
                hand['lastAction'] = "HIT"
                continue
            hand['bid'] *= 2
            hand["cards"].append(deck.dealCard())
            double_points = getPoints(hand)
            print(f"{player} doubled. Final points {double_points}")
            if double_points > 21:
                hand['lastAction'] = "BUST"
                print(f"{player} is busted! His bid {hand['bid']} is lost")
                player.credits -= hand['bid']
        if action == "SURRENDER":
            print(f"{player} surrenders this hand, losing half his bid {hand['bid'] / 2}")
            player.credits -= hand['bid'] / 2
        if action == "SPLIT":
            if player.credits - hand['bid'] < hand['bid']:
                print("player cannot split - insufficient funds")
                continue
            new_card_current = deck.dealCard()
            new_card_next = deck.dealCard()
            print(f"{player} splits. Cards {new_card_current} and {new_card_next} are dealt respectively. Hands will "
                  f"be played in succession")
            new_hand = {"cards": [hand["cards"].pop(), new_card_next], "bid": hand['bid'], "lastAction": ""}
            hand["cards"].append(new_card_current)
            player.hands.append(new_hand)
            continue
    i += 1


def place_bids(player):
    print(f"{player} places bid")
    bid = int(input("How much to bet?"))
    while not (0 < int(bid) <= player.credits):
        bid = int(input("Incorrect input. How much to bet?"))
    player.hands[0]['bid'] = bid


def newGame():
    deck = Deck(decks)
    players = []
    getPlayers(players)
    dealer = Player('Dealer')
    for player in players:
        place_bids(player)
    for player in players:
        draw_cards(deck, player)
    draw_cards(deck, dealer)
    ace = dealer.hands[0]["cards"][0].rank == 'ace'
    if ace:
        print(f"Dealer face up card is ace!")
        for player in players:
            selectInsuranceAction(player)
        if getPoints(dealer.hands[0] == 21):
            print("Dealer has a Black Jack!")
            for player in players:
                if player.hands[0]['lastAction'] == "INSURANCE":
                    print(f"{player} has insurance - end this round with unchanged credits balance")
                    player.hands[0]['lastAction'] = "PAID INSURANCE"
                if player.hands[0]['lastAction'] == "EVEN MONEY":
                    print(f"{player} has even money - wins his bid of {player.hands[0]['bid']}")
                    player.credits += player.hands[0]['bid']
        else:
            print("Dealer has no Black Jack")
            for player in players:
                if player.hands[0]['lastAction'] == "INSURANCE":
                    print(f"{player} has insurance {player.hands[0]['bid'] / 2} which is lost")
                    player.credits -= player.hands[0]['bid'] / 2
                if player.hands[0]['lastAction'] == "EVEN MONEY":
                    print(f"{player} has even money - wins his bid of {player.hands[0]['bid']}")
                    player.credits += player.hands[0]['bid']
    for player in players:
        selectActionsForSubsequentHands(player, deck)
    while getPoints(dealer.hands[0]) < 17:
        dealer.hands[0]["cards"].append(deck.dealCard())
    dealer_points = getPoints(dealer.hands[0])
    print(f"Dealer has {dealer_points} points")
    for player in players:
        for hand in player.hands:
            if hand['lastAction'] == "STAND" or hand['lastAction'] == "DOUBLE":
                player_points = getPoints(hand)
                if player_points == 21 and len(hand) == 2:
                    print(f"{player} has a BlackJack!")
                    if dealer_points == 21 and len(dealer.hands[0]) == 2:
                        print(f"PUSH - player gains/loses nothing")
                    else:
                        print(f"{player} wins 3/2 his bid {hand['bid'] * 1.5}")
                        player.credits += hand['bid'] * 1.5
                if player_points > 21:  # this should not happen - just in case
                    print(f"{player} is busted")
                    hand['lastAction'] = "BUST"
                    player.credits -= hand['bid']
                if dealer_points > 21 or player_points > dealer_points:
                    print(f"{player} wins his bid of {hand['bid']}")
                    player.credits += hand['bid']
                else:
                    print(f"{player} loses {hand['bid']}")
                    player.credits -= hand['bid']


def draw_cards(deck, player):
    player.hands[0]["cards"].append(deck.dealCard())
    player.hands[0]["cards"].append(deck.dealCard())
    print(player)
    for c in player.hands[0]["cards"]:
        print(c)


while True:
    print("Welcome to BlackJack. Select an option:")
    menu()
    option = input()

    if option == "1":
        newGame()
    elif option == "2":
        newCount = int(input("Enter the number of decks (1-8)"))
        while newCount < 1 or newCount > 8:
            newCount = int(input("Incorrect input. Enter the number of decks (1-8)"))
        decks = newCount
        print(f"Number of decks: {decks}")
    else:
        menu()
