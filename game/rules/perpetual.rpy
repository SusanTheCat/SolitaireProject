# perpetual.rpy - Double Klondike Solitaire
# Copyright (C) 2016 Susan <susan@thecatsweb.com>

init python:

    class Perpetual(object):

        # We represent a card as a (suit, rank) tuple. The suit is one of the
        # following four constants, while the rank is 1 for ace, 2 for 2,
        # ..., 10 for 10, 11 for jack, 12 for queen, 13 for king.        
        CLUB = 0
        SPADE = 1
        HEART = 2
        DIAMOND = 3
        
        
        def __init__(self):

            # Constants that let us easily change where the game is
            # located.
            LEFT=200
            TOP=58
            COL_SPACING = 90
            ROW_SPACING = 120
            CARD_XSPACING = 20
            CARD_YSPACING = 30
            
            self.TABLEAUS  = 4
            
            
            self.start_rank = 0

            
            # Create the table, stock, and waste.
            self.table = t = Table(base="card/base.png", back="card/back.png")
            self.stock = t.stack(LEFT+COL_SPACING*6, TOP+ROW_SPACING*3, xoff=0.5, yoff=0, click=True)
            self.waste = t.stack(LEFT+COL_SPACING*4, TOP+ROW_SPACING*3, xoff=0, yoff=0, click=True)


            # The 4 tableau stacks.
            self.tableau = [ ]
            for i in range(0, self.TABLEAUS):
                s = t.stack(LEFT + COL_SPACING * (i + 2), TOP + ROW_SPACING*2, xoff=0, yoff=0, drag=DRAG_ABOVE, click=True, drop=True)
                self.tableau.append(s)

            # Create the stock and shuffle it.
            for rank in range(1, 14):
                for suit in range(0, 4):
                    for deck in range(0, 1):
                        value = (suit, rank, deck)
                        t.card(value, "card/%d.png" % self.card_num(suit, rank))
                        t.set_faceup(value, False)
                        self.stock.append(value)
                    
            self.stock.shuffle()
            

            
            # Deal out the initial tableau.
            for i in range(0, self.TABLEAUS):
                c = self.stock.deal()
                self.tableau[i].append(c)       
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
            
            #only drag one card
            if len(cards) != 1:
                return False

            csuit, crank, cdeck = card
            
            # If the stack is empty, allow any card to be dragged to it.
            if not stack:
                for i in cards:
                    stack.append(i)

                return "tableau_drag"

            # Otherwise, the stack has a bottom card.
            bottom = stack[-1]
            bsuit, brank,bdeck = bottom


            # Can we legally place the cards?
            if crank == brank:

                # Place the cards:
                for i in cards:
                    stack.append(i)

                return "tableau_drag"

            return False
                    
      
        def tableau_doubleclick(self, evt):
            lrank = None
            FourOfAKind = True
            for i in range(0, self.TABLEAUS):
                if self.tableau[i]:
                    card = self.tableau[i][-1]
                    csuit, crank, cdeck = card
                    if lrank != None and lrank != crank:
                        FourOfAKind = False
                    lrank = crank
            if FourOfAKind:
                if self.tableau[i]:
                    for i in range(0, self.TABLEAUS):
                        c = self.tableau[i][-1]
                        self.waste.append(c)
                
                return "tableau_drag"
            return False
        
        def stock_click(self, evt):

            # If there are cards in the stock
            if self.stock:
            
                for i in range(0, self.TABLEAUS):
                    c = self.stock[-1]
                    self.table.set_faceup(c, True)  
                    self.tableau[i].append(c)     
                return "stock_click"
                        
            # Otherwise, move the contents of the tableau to the stock.
            else:
                for i in range(self.TABLEAUS, 0, -1):
                    while self.tableau[i-1]:
                        c = self.tableau[i-1][-1]
                        self.table.set_faceup(c, False)
                        self.stock.append(c)

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
                    
            elif evt.type == "doubleclick":
                if evt.stack in self.tableau:
                    rv = self.tableau_doubleclick(evt)

            
            if len(self.waste) == 52:
                return "win"
            else:
                return rv
            
        # Sets things as sensitive (or not).
        def set_sensitive(self, value):
            self.table.set_sensitive(value)
        
        # Utility functions.

        # Is it okay to drag the over card onto under, where under is
        # part of a tableau.
        def can_hint(self, under, over):
            usuit, urank, udeck = under
            osuit, orank, odeck = over

            if orank == urank:
                return True

        # Returns the first faceup card in the stack.
        def first_faceup(self, s):
            for c in s:
                if self.table.get_faceup(c):
                    return c

        # This tries to find a reasonable hint, and returns it as a
        # pair of cardnames.
        def hint(self):

            for i in self.tableau:
                if not i:
                    continue

                over = self.first_faceup(i)

                for j in self.tableau:
                    if not j or i is j:
                        continue

                    under = j[-1]

                    if self.can_hint(under, over):
                        return (under, over)

            if self.waste:

                over = self.waste[-1]

                for j in self.tableau:
                    if not j:
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
                     
                    
