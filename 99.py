import random
from g import datanode as dn
from g.datanode import socknode as sn
from g.datanode.replnode import ReplNode
import time

class GameVars:
	def __init__(self):
		self.HOW_MANY_TO_WIN = 10

		self.current_trick=[]
		self.values = {
		'AD':0,'KD':0,'QD':0,'JD':0,'TD':0,'9D':0,'8D':0,'7D':0,'6D':0,
		'AS':1,'KS':1,'QS':1,'JS':1,'TS':1,'9S':1,'8S':1,'7S':1,'6S':1,
		'AH':2,'KH':2,'QH':2,'JH':2,'TH':2,'9H':2,'8H':2,'7H':2,'6H':2,
		'AC':3,'KC':3,'QC':3,'JC':3,'TC':3,'9C':3,'8C':3,'7C':3,'6C':3
		}
		self.sorted_deck = list(self.values.keys())
		self.leading_suit = None
		self.order_of_play = [0,1,2]
		self.who_goes_first = 0
		self.trump = 'Z'	#no trump at first
		self.game_over = False

gamevars = GameVars()

def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

data = [None,None,None]




def savedata0(msg):
	data[0] = msg
def savedata1(msg):
	data[1] = msg
def savedata2(msg):
	data[2] = msg


server = sn.SockNodeServer("10.0.0.85", 14517)
server.run(max_clients=3)

REMEMBERnode0 = dn.DataNode(savedata0)
REMEMBERnode1 = dn.DataNode(savedata1)
REMEMBERnode2 = dn.DataNode(savedata2)

def single_input(clientnumber,prompt):
	s = 'i|'+prompt
	server.connections[clientnumber].receive(s)
	while data[clientnumber] is None:
		time.sleep(0.01)
	d = data[clientnumber]
	data[clientnumber] = None
	return d

def async_input(prompt):
	s = 'i|'+prompt
	server.connections[0].receive(s)
	server.connections[1].receive(s)
	server.connections[2].receive(s)
	while data[0] is None or data[1] is None or data[2] is None:
		time.sleep(0.01)
	d = data[:]
	data[0] = None; data[1] = None; data[2] = None
	return d

def single_print(clientnumber,msg=''):
	s = 'p|'+str(msg)
	server.connections[clientnumber].receive(s)
	time.sleep(.1)

def all_print(msg=''):
	s = 'p|'+str(msg)
	server.connections[0].receive(s)
	server.connections[1].receive(s)
	server.connections[2].receive(s)

class Player():
	def __init__(self, num):
		self.num = num
		self.hand = []
		self.bid = 0
		self.bid_cards = []
		self.have_bid = False
		self.tricks = 0
		self.score = 0
		self.declared = False
		self.revealed = False
		self.is_leading = False

	def bidding(self, foo = None):
		single_print(self.num,'This is your hand right now:')
		single_print(self.num,self.hand)
		self.have_bid = False

		#error handling on error handling on...
		while True:
			try:
				card = str(single_input(self.num,"\nPick a card to bid, or type 'clear' to remove cards you've already selected: ")).upper()
				if card == 'clear':
					self.bid_cards = []
					self.bid = 0
					single_print(self.num,"Your currently selected bid is: "+str(self.bid_cards)+' for: '+str(self.bid))
					continue
				elif card not in gamevars.sorted_deck:
					single_print(self.num,'Sorry, that is not the name of a card.')
					continue
				elif card not in self.hand:
					single_print(self.num,'Sorry, that card is not in your hand.')
					continue
				elif card in self.bid_cards:
					single_print(self.num,"Sorry, you've already used that one.")
					continue
				else:
					self.bid_cards.append(card)
					self.bid = self.bid + gamevars.values[card]
					single_print(self.num)
					single_print(self.num)
					single_print(self.num,"Your currently selected bid is: "+str(self.bid_cards)+' for: '+str(self.bid))

				if len(self.bid_cards) >= 3:
					while True:
						try:
							single_print(self.num,'Leaving you with the hand: '+str(Diff(self.hand,self.bid_cards)))
							single_print(self.num)
							yn = single_input(self.num, 'Would you like to confirm your bid for '+str(self.bid)+'? y/n  ')
							if yn != 'y' and yn != 'n':
								single_print(self.num,'Sorry, please enter either "y" or "n":')
								continue
							if yn == 'y':
								self.hand = Diff(self.hand,self.bid_cards)
								single_print(self.num,'You have bid '+str(self.bid)+'.')
								self.have_bid = True
								break
							elif yn == 'n':
								self.bid_cards = []
								self.bid = 0
								single_print(self.num,"Your currently selected bid is: "+str(self.bid_cards)+' for: '+str(self.bid))
								single_print(self.num,'Leaving you with the hand: '+str(self.hand))
								break
							else:
								single_print(self.num,'Sorry, please enter either "y" or "n":')
								continue
						except(ValueError, IndexError):
							single_print(self.num,"Please enter either 'y' or 'n'.")
							single_print(self.num)
							continue
					if len(self.bid_cards)>0:
						single_print(self.num)
						single_print(self.num)
						break

			except(ValueError, IndexError):
				single_print(self.num,"Sorry, that didn't work. Please try again.")
				continue

	def declaring(self):
		while True:
			try:
				drn = single_input(self.num,'Do you want to declare or reveal? d = declare, r = reveal, n = neither ')
				if drn != 'd' and drn != 'r' and drn !='n':
					single_print(self.num,"Please enter 'd', 'r', or 'n'.")
				elif drn == 'd':
					self.declared = True
					break
				elif drn == 'r':
					self.revealed = True
					break
				elif drn == 'n':
					break
			except ValueError:
				single_print(self.num,'Something went wrong. Yikes!')

	def revealing(self):
		while True:
			try:
				yn = single_input(self.num,'Do you want to reveal? y/n ')
				if yn != 'y' and yn != 'n':
					single_print(self.num,"Please entereither 'y' or 'n'.")
				elif yn == 'y':
					self.revealed = True
					break
				elif yn == 'n':
					self.revealed = False
					break
			except (ValueError, IndexError):
				single_print(self.num,'Something went wrong. Yikes!')

	def playing(self):
		single_print(self.num,'Player '+ str(self.num+1)+', this is your hand right now:')
		single_print(self.num,self.hand)
		single_print(self.num)
		single_print(self.num,'And your bid is: '+str(self.bid))

		while True:		#asks you for a card until it can play it
			try:
				card = str(single_input(self.num,'\nPick a card to play: ')).upper()
				if card not in gamevars.sorted_deck:
					single_print(self.num,'Sorry, that is not the name of a card.')
					continue

				#if you're first, your whole hand is viable
				if self.is_leading:
					viable_cards = self.hand
				else:	#if you're not first, only cards that follow suit are viable
					viable_cards = [i for i in self.hand if gamevars.leading_suit in i]

				#but if you don't have any viable cards, then you can play anything!
				if not viable_cards:
					viable_cards = self.hand

				#now, just play
				if card in viable_cards:
					gamevars.current_trick.append(card)
					self.hand.remove(card)
					break
				else:
					single_print(self.num,"Sorry, that didn't work. Make sure that the card is in your hand and follows suit.")

			except (ValueError, IndexError):
				single_print(self.num,"Sorry, that didn't work. Please try again.")
		single_print(self.num)
		single_print(self.num)
		self.is_leading = False


# one game
def game():

	def Order(card):	#for use in sorted, below
		return gamevars.sorted_deck.index(card)
	def deal(player1, player2, player3):

		#shuffle deck
		shuffled_deck = list(gamevars.values.keys())
		random.shuffle(shuffled_deck)

		#deal and sort hands
		player1.hand = sorted(shuffled_deck[0:12], key = Order, reverse = True)
		player2.hand = sorted(shuffled_deck[12:24], key = Order, reverse = True)
		player3.hand = sorted(shuffled_deck[24:36], key = Order, reverse = True)

	server.connections[0].run()
	server.connections[1].run()
	server.connections[2].run()
	REMEMBERnode0 << server.connections[0]
	REMEMBERnode1 << server.connections[1]
	REMEMBERnode2 << server.connections[2]

	player1 = Player(0)
	player2 = Player(1)
	player3 = Player(2)
	players = [player1,player2,player3]

	biddingnode0 = dn.QueueNode(funct = player1.bidding)
	biddingnode1 = dn.QueueNode(funct = player2.bidding)
	biddingnode2 = dn.QueueNode(funct = player3.bidding)
	REMEMBERnode0 << biddingnode0
	REMEMBERnode1 << biddingnode1
	REMEMBERnode2 << biddingnode2


	while True:		
		
		deal(player1, player2, player3)

		#everyone bids
		all_print('*Starting Bidding*\n')
		all_print('Just a reminder: D is 0, S is 1, H is 2, C is 3\n')
		#the string doesn't matter, it just gets everyone bidding
		biddingnode0.receive('start')
		biddingnode1.receive('start')
		biddingnode2.receive('start')

		while player1.have_bid == False or player2.have_bid == False or player3.have_bid == False:
			time.sleep(.01)

#		for k in range(3):
#			players[gamevars.order_of_play[k]].bidding()

		#we don't want this to be simultaneous.
		#declaring and revealing
		for p in range(3):
			temp = players[gamevars.order_of_play[p]]
			temp.declaring()

			if not temp.declared and not temp.revealed:
				all_print('Player '+ str(gamevars.order_of_play[p]+1)+' has not declared.')
				pass
			elif temp.declared:
				all_print('Player '+ str(gamevars.order_of_play[p]+1)+' has declared.')
				for y in range(3):
					tempp = players[(p+1+y)%3]
					tempp.revealing()
					if not tempp.revealed:
						all_print('Player '+ str(gamevars.order_of_play[(p+1+y)%3]+1)+' has not revealed.')
					elif tempp.revealed:
						all_print('Player '+ str(gamevars.order_of_play[(p+1+y)%3]+1)+' has revealed!')
						player1.declared = False
						player2.declared = False
						player3.declared = False
						tempp.declared = True
						break	
				break
			elif temp.revealed:
				all_print('Player '+ str(gamevars.order_of_play[p]+1)+' has revealed!')
				player1.declared = False
				player2.declared = False
				player3.declared = False
				temp.declared = True
				break

		all_print('*Starting Play*')
		all_print('')

		#looping over individual hands
		for hand_num in range(9):

			for u in range(3):
				temp = players[gamevars.order_of_play[u]]
				if temp.declared:
					all_print("Player "+ str(gamevars.order_of_play[u]+1)+"'s bid is: "+str(temp.bid_cards)+' for '+str(temp.bid))
				if temp.revealed:
					all_print("Player "+ str(gamevars.order_of_play[u]+1)+"'s hand is: "+str(temp.hand))

			#everyone plays


			players[gamevars.order_of_play[0]].is_leading = True	#first player can play anything
			all_print('The trick so far: '+ str(gamevars.current_trick))
			players[gamevars.order_of_play[0]].playing()
			first_card = gamevars.current_trick[0]; gamevars.leading_suit = first_card[-1]	#figures out the leading suit
		
			all_print('The trick so far: '+ str(gamevars.current_trick))
			players[gamevars.order_of_play[1]].playing()
			
			all_print('The trick so far: '+ str(gamevars.current_trick))
			players[gamevars.order_of_play[2]].playing()

			#determine winner. It goes backwards because it just overwrites with higher priority
			startsearch = 100
			winner_num = 100
			winner = 0

			#check leading suit
			if (gamevars.leading_suit == 'D'): startsearch = 8
			if (gamevars.leading_suit == 'S'): startsearch = 17
			if (gamevars.leading_suit == 'H'): startsearch = 26
			if (gamevars.leading_suit == 'C'): startsearch = 35
			for i in range (9):
				for card_num_in_trick in range(3):
					if gamevars.current_trick[card_num_in_trick] == gamevars.sorted_deck[startsearch-i]:
						winner_num = gamevars.order_of_play[card_num_in_trick]
						winner = players[winner_num]

			#check if gamevars.trump wins
			try:
				if (gamevars.trump == 'D'): startsearch = 8
				if (gamevars.trump == 'S'): startsearch = 17
				if (gamevars.trump == 'H'): startsearch = 26
				if (gamevars.trump == 'C'): startsearch = 35
				for i in range (9):
					for card_num_in_trick in range(3):
						if gamevars.current_trick[card_num_in_trick] == gamevars.sorted_deck[startsearch-i]:
							winner_num = gamevars.order_of_play[card_num_in_trick]
							winner = players[winner_num]
			except:	#if there is no gamevars.trump, it throws an indexing error. Just keep moving
				pass

			#moving on, cleaning up
			winner.tricks = winner.tricks + 1
			all_print('------------------------------')
			all_print('Player '+str(gamevars.order_of_play[0]+1)+' played '+gamevars.current_trick[0])
			all_print('Player '+str(gamevars.order_of_play[1]+1)+' played '+gamevars.current_trick[1])
			all_print('Player '+str(gamevars.order_of_play[2]+1)+' played '+gamevars.current_trick[2])
			all_print()
			all_print('Player 1 now has '+ str(player1.tricks)+' trick(s), Player 2 has '+str(player2.tricks)+' trick(s), and Player 3 has '+str(player3.tricks)+' trick(s).')
			all_print('------------------------------')
			all_print()
			gamevars.order_of_play = [winner_num, (winner_num+1)%3, (winner_num+2)%3]
			gamevars.current_trick = []

	#Inbetween games, give out scores and figure out gamevars.trump (and some other little things)

		all_print()
		all_print('The round is over.')

		print('a')
		how_many_winners = 0		#figure out how many people got their bids
		print('b')
		for y in range(3):
			temp = players[y]
			if temp.tricks == temp.bid: 
				how_many_winners = how_many_winners + 1
		print('c')

		for t in range(3):		#give scores
			temp = players[t]
			if temp.tricks == temp.bid:
				all_print('Player '+str(t+1)+' bid '+str(player1.bid)+' and got it.')
				temp.score = temp.score + temp.bid + 40 - how_many_winners*10
				if temp.declared:
					all_print('Player '+str(t+1)+' declared and got it!')
					temp.score = temp.score + 30
				if temp.revealed:
					all_print('Player '+str(t+1)+' revealed and got it!')
					temp.score = temp.score + 60
			elif temp.tricks != temp.bid:
				all_print('Player '+str(t+1)+' bid '+str(player1.bid)+' and missed it.')
			if temp.score >= gamevars.HOW_MANY_TO_WIN:
				gamevars.game_over = True
		print('d')

		#set gamevars.trump for next game
		if how_many_winners == 0:
			gamevars.trump = 'D'
		elif how_many_winners == 1:
			gamevars.trump = 'S'
		elif how_many_winners == 2:
			gamevars.trump = 'H'
		elif how_many_winners == 3:
			gamevars.trump = 'C'
		else:
			all_print('Fuck off')

		all_print('Scores:')
		all_print('Player 1 has '+str(player1.score))
		all_print('Player 2 has '+str(player2.score))
		all_print('Player 3 has '+str(player3.score))
		all_print()
		all_print('Trump is now ' +str(gamevars.trump))
		all_print()

		#who goes first
		gamevars.who_goes_first = (gamevars.who_goes_first+1)%3
		gamevars.order_of_play = [gamevars.who_goes_first, (gamevars.who_goes_first+1)%3, (gamevars.who_goes_first+2)%3]

		#reset
		gamevars.current_trick = []
		for r in range(3):
			temp = players[r]
			temp.bid = 0
			temp.bid_cards = []
			temp.declared = False
			temp.revealed = False

		if gamevars.game_over:
			scores = [player1.score,player2.score,player3.score]

			first_place = scores.index(max(scores))

			last_place = scores.index(min(scores))
			second_place_list = Diff(gamevars.order_of_play,[first_place,last_place]); second_place = second_place_list[0]

			first_place_player = players[first_place]
			second_place_player = players[second_place]
			last_place_player = players[last_place]

			all_print()
			all_print()
			all_print('------------------------------')
			all_print('The game is over.')
			all_print('Congratulations to Player '+str(first_place+1)+', you win with '+str(first_place_player.score)+'!')
			all_print('Player '+str(second_place+1)+', you came in second with '+str(second_place_player.score)+'.')
			all_print('Player '+str(last_place+1)+', you came in last with '+str(last_place_player.score)+'.')
			all_print('------------------------------')
			all_print()
			all_print()
			all_print('*Starting new game*')
			all_print()
			all_print()

			gamevars.order_of_play = [0,1,2]
			player1.score = 0
			player2.score = 0
			player3.score = 0
			gamevars.trump = 'Z'
			gamevars.game_over = False

server.register_new_connection_callback(game, 3)