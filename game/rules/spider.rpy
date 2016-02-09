# spider.rpy - Spider Solitaire
# Copyright (C) 2016 Susan <susan@thecatsweb.com>

init python:

    class Spider(object):
     
        CLUB = 0
        SPADE = 1
        HEART = 2
        DIAMOND = 3
        
        
        def __init__(self, suits=4):

            # Constants that let us easily change where the game is
            # located.
            LEFT=200
            TOP=58
            COL_SPACING = 90
            ROW_SPACING = 120
            CARD_XSPACING = 20
            CARD_YSPACING = 25

            self.suits = suits
            
            self.table = t = Table(base="card/base.png", back="card/back.png")

            self.stock = t.stack(LEFT, TOP, xoff=0, yoff=0, click=True)
            
            
            # The 8 foundation stacks.
            self.foundations = [ ]
            for i in range(0, 8):
                s = t.stack(LEFT + COL_SPACING * (i + 3), TOP, xoff=0, yoff=0, drag=DRAG_TOP, drop=True)
                self.foundations.append(s)

            # The 10 tableau stacks.
            self.tableau = [ ]
            for i in range(0, 10):
                s = t.stack(LEFT + COL_SPACING + COL_SPACING * i, TOP + ROW_SPACING, xoff=0, yoff=CARD_YSPACING, drag=DRAG_ABOVE, click=True, drop=True)
                self.tableau.append(s)

            counter = 0
            # Create the stock and shuffle it.
            for rank in range(1, 14):
                for suit in range(0, self.suits):
                    for deck in range(0, self.num_of_decks(self.suits)):
                        new_suit = (suit + 1) % 4
                        value = (new_suit, rank, deck)
                        t.card(value, "card/%d.png" % self.card_num(new_suit, rank))
                        t.set_faceup(value, False)
                        self.stock.append(value)
                        counter += 1
                        renpy.log ("Count %d (%d %d %d)" % (counter,new_suit, rank, deck))
            self.stock.shuffle()
            
            # Deal out the initial tableau.
            for j in range(0, 5):
                for i in range(0, 10):
                    c = self.stock.deal()
                    self.tableau[i].append(c)  
            for i in range(0, 4):
                c = self.stock.deal()
                self.tableau[i].append(c)                   

            # Ensure that the bottom of each tableau is faceup.
            for i in range(0, 10):
                if self.tableau[i]:
                    self.table.set_faceup(self.tableau[i][-1], True)


        # This figures out the image filename for a given suit and rank.
        def card_num(self, suit, rank):
            ranks = [ None, 1, 49, 45, 41, 37, 33, 29, 25, 21, 17, 13, 9, 5 ]
            return suit + ranks[rank]
                
        def show(self):
            self.table.show()

        def hide(self):
            self.table.hide()
            
        def tableau_drag(self, evt):
            card = evt.drag_cards[0]
            cards = evt.drag_cards
            stack = evt.drop_stack

            #only move cards that follow suits
            for i in range(1,len(cards)):
                last_card = cards[i-1]
                current_card = cards[i]
                lsuit, lrank, ldeck = last_card
                csuit, crank, cdeck = current_card
                if lsuit != csuit:
                    return False
                if lrank != crank + 1 :
                    return False
                    
                
            renpy.log("stack ok")
                
 

            csuit, crank, cdeck = card
                       
            # If the stack is empty, allow a card to be dragged to it.
            if not stack:
                for i in cards:
                    stack.append(i)

                return "tableau_drag"

            # Otherwise, the stack has a bottom card.
            bottom = stack[-1]
            bsuit, brank,bdeck = bottom

            # Can we legally place the cards?
            if (crank == brank - 1):

                # Place the cards:
                for i in cards:
                    stack.append(i)

                return "tableau_drag"

            return False
                    
                
        
        def stock_click(self, evt):
            
            for i in range(0, 10):
                if not self.tableau[i]:
                    return False

            # If there are cards in the stock, dispense up to three3
            # of them.
            if self.stock:
                for i in range(0, 10):
                    if self.stock:
                        c = self.stock[-1]
                        self.table.set_faceup(c, True)
                        self.tableau[i].append(c)  

                return "stock_click"
                        
                    
        def interact(self):

            evt = ui.interact()
            rv = False
            
            # Check the various events, and dispatch them to the methods
            # that handle them.
            if evt.type == "drag":
                if evt.drop_stack in self.tableau:
                    rv = self.tableau_drag(evt)
                    
                    
            elif evt.type == "click":
                if evt.stack == self.stock:
                    rv = self.stock_click(evt)
                    
                    
                    
            #place finished stacks in foundation   
            for i in range(0, 10):
                #check last 13 cards in stack 
                stack = self.tableau[i]  
                foundy = self.first_empty_foundation()
                if len(stack) < 13:
                    continue 
                stack_good = True
                for j in range(-12,0):
                    last_card = stack[j-1]
                    current_card = stack[j]
                    lsuit, lrank, ldeck = last_card
                    csuit, crank, cdeck = current_card
                    if lsuit != csuit:
                        stack_good = False
                        break
                    if lrank != crank + 1 :
                        stack_good = False
                        break
                 
                if stack_good:
                    for j in range(0,13):
                        current_card = stack[-1]
                        foundy.append(current_card)

            
            # Ensure that the bottom card in each tableau is faceup.
            for i in range(0, 10):
                if self.tableau[i]:
                    self.table.set_faceup(self.tableau[i][-1], True)
            
            # Check to see if any of the foundations has less than
            # 13 cards in it. If it does, return False. Otherwise,
            # return True.
            for i in self.foundations:
                if len(i) != 13:
                    return rv
                
            return "win"
            
        # Sets things as sensitive (or not).
        def set_sensitive(self, value):
            self.table.set_sensitive(value)
        
        # Utility functions.

        # Is it okay to drag the over card onto under, where under is
        # part of a tableau.
        def can_hint(self, under, over):
            usuit, urank, udeck = under
            osuit, orank, odeck = over

            if orank == 1:
                return False

            if (orank == urank - 1):
                return True

        # Returns the first faceup card in the stack.
        def first_faceup(self, s):
            for c in s:
                if self.table.get_faceup(c):
                    return c
                    
        def top_bottom_run(self, s):
            last_c = None
            for c in reversed(s):
                if last_c != None:
                    lsuit, lrank, ldeck = last_c
                    csuit, crank, cdeck = c
                    
                    if not self.table.get_faceup(c):
                        return last_c            
                    if (lrank != crank - 1):
                        return last_c
                    if (lsuit != csuit):
                        return last_c
                last_c = c
                
        def first_empty_foundation(self):
            for f in self.foundations:
                if not f:
                    return f

        # This tries to find a reasonable hint, and returns it as a
        # pair of cardnames.
        def hint(self):

            for i in self.tableau:
                if not i:
                    continue

                over = self.top_bottom_run(i)

                if over == None:
                    continue
                    
                for j in self.tableau:
                    if not j or i is j:
                        continue

                    under = j[-1]

                    if self.can_hint(under, over):
                        return (under, over)

                
            return None, None
            
        def card_name(self, c):
            suit, rank, deck = c

            return  [
                "INVALID",
                "Ace",
                "Two",
                "Three",
                "four",
                "Five",
                "Six",
                "Seven",
                "Eight",
                "Nine",
                "Ten",
                "Jack",
                "Queen",
                "King" ][rank] + " of " + [
                "Clubs",
                "Spades",
                "Hearts",
                "Diamonds" ][suit]
                     
        def num_of_decks(self, num_of_suits):
            switcher = {
                1: 8,
                2: 4,
                4: 2,
            }
            return switcher.get(num_of_suits, 0)
