# canfield.rpy - Double Klondike Solitaire
# Copyright (C) 2016 Susan <susan@thecatsweb.com>

init python:

    class Canfield(object):

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
            
            TABLEAUS  = 4
            
            self.start_rank = 0

            
            # Create the table, stock, and waste.
            self.table = t = Table(base="card/base.png", back="card/back.png")
            self.stock = t.stack(LEFT+COL_SPACING*6, TOP+ROW_SPACING*3, xoff=0, yoff=0, click=True)
            self.reserve = t.stack(LEFT, TOP, xoff=0, yoff=CARD_YSPACING, drag=DRAG_TOP, show=13, click=True)
            self.waste = t.stack(LEFT+COL_SPACING*7, TOP+ROW_SPACING*3, xoff=CARD_XSPACING, drag=DRAG_TOP, show=3, click=True)

            # The 4 foundation stacks.
            self.foundations = [ ]
            for i in range(0, 4):
                s = t.stack(LEFT + COL_SPACING * (i + 2), TOP, xoff=0, yoff=0, drag=DRAG_TOP, drop=True)
                self.foundations.append(s)

            # The 4 tableau stacks.
            self.tableau = [ ]
            for i in range(0, 4):
                s = t.stack(LEFT + COL_SPACING * (i + 2), TOP + ROW_SPACING, xoff=0, yoff=CARD_YSPACING, drag=DRAG_ABOVE, click=True, drop=True)
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
            
            # Deal out the reserve
            for i in range(0, 13):
                c = self.stock.deal()
                self.reserve.append(c)       
                self.table.set_faceup(self.reserve[-1], False) 
            
            self.table.set_faceup(self.reserve[-1], True)
            
            #deal first foundation
            
            c = self.stock.deal()
            self.foundations[0].append(c)       
            self.table.set_faceup(self.foundations[0][-1], True) 
            
            csuit, crank, cdeck = c
                
                
            self.start_rank = crank
            
            
            
            # Deal out the initial tableau.
            for i in range(0, TABLEAUS):
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
            
            #only drag one card UNLESS it is the whole stack
            if len(cards) != 1 and len(cards) != len(evt.stack):
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

            # Figure out which of the stacks are black.
            cblack = (csuit == self.SPADE) or (csuit == self.CLUB)
            bblack = (bsuit == self.SPADE) or (bsuit == self.CLUB)

            # Can we legally place the cards?
            if (bblack != cblack) and (crank == brank - 1 or (crank == 13 and brank == 1)):

                # Place the cards:
                for i in cards:
                    stack.append(i)

                return "tableau_drag"

            return False
                    
        def foundation_drag(self, evt):

            # We can only drag one card at a time to a foundation.
            if len(evt.drag_cards) != 1:
                return False

            suit, rank, deck = evt.drag_cards[0]

            # If there is a card on the foundation already, then
            # check to see if we're dropping then next one in
            # sequence.
            if len(evt.drop_stack):
                dsuit, drank, ddeck = evt.drop_stack[-1]
                if suit == dsuit and (rank == drank + 1 or (rank == 1 and drank == 13)):
                    evt.drop_stack.append(evt.drag_cards[0])
                    return "foundation_drag"
                    
            # Otherwise, make sure we're dropping an ace.
            else:
                if rank == self.start_rank:
                    evt.drop_stack.append(evt.drag_cards[0])
                    return "foundation_drag"

            return False
                
        def tableau_doubleclick(self, evt):

            # Make sure that there's at least one card in the stack.
            if not evt.stack:
                return False

            # The bottom card in the stack.
            card = evt.stack[-1]
            suit, rank, deck = card

            # If the card is an ace, find an open foundation and put it
            # there.
            if rank == self.start_rank:
                for i in self.foundations:
                    if not i:
                        i.append(card)
                        break
                return "foundation_drag"

            # Otherwise, see if there's a foundation where we can put
            # the card.
            for i in self.foundations:
                if not i:
                    continue
                
                fsuit, frank, fdeck = i[-1]
                if suit == fsuit and(rank == frank + 1 or (rank == 1 and frank == 13)):
                    i.append(card)
                    return "foundation_drag"

            return False
        
        def stock_click(self, evt):

            # If there are cards in the stock, dispense up to three3
            # of them.
            if self.stock:
                for i in range(0,3):
                    if self.stock:
                        c = self.stock[-1]
                        self.table.set_faceup(c, True)
                        self.waste.append(c)

                return "stock_click"
                        
            # Otherwise, move the contents of the waste to the stock.
            else:
                while self.waste:
                    c = self.waste[-1]
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
                    
                elif evt.drop_stack in self.foundations:
                    rv = self.foundation_drag(evt)
                    
            elif evt.type == "click":
                if evt.stack == self.stock:
                    rv = self.stock_click(evt)
                    
            elif evt.type == "doubleclick":
                if (evt.stack in self.tableau) or (evt.stack is self.waste):
                    rv = self.tableau_doubleclick(evt)

            #Fill and blank tableaus
            if len(self.reserve) > 0:
                for i in self.tableau:
                    if not i:
                        card = self.reserve[-1]
                        self.table.set_faceup(card, True)
                        i.append(card)

                    
            # Ensure that the bottom card in reserve is faceup.
            if self.reserve:
                self.table.set_faceup(self.reserve[-1], True)
                        
            if persistent.autofinish and len(self.stock)==0 and len(self.waste)==0:
                cardsleft = True
                while cardsleft:  
                    cardsleft = False
                    for tabby in self.tableau:
                        if tabby:                
                            card = tabby[-1]          
                            cardsleft = True
                            suit, rank, deck = card

                            # If the card is the staring rank, find an open foundation and put it
                            # there.
                            if rank == self.start_rank:
                                for i in self.foundations:
                                    if not i:
                                        i.append(card)
                                        renpy.pause(0.2)
                                        break

                            # Otherwise, see if there's a foundation where we can put
                            # the card.
                            for i in self.foundations:
                                if not i:
                                    continue
                                
                                fsuit, frank, fdeck = i[-1]
                                if suit == fsuit and (rank == frank + 1 or (rank == 1 and frank == 13)):
                                    i.append(card)
                                    renpy.pause(0.2)
                                    break
            
            
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

            if orank == self.start_rank:
                return False
            
            ublack = (usuit == self.SPADE) or (usuit == self.CLUB)
            oblack = (osuit == self.SPADE) or (osuit == self.CLUB)

            if (oblack != ublack) and (orank == urank - 1 or (orank == 13 and urank == 1)):
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
                     
                    
