# You can place the script of your game in this file.


    

init python:
    
    import os
    #config.log = os.path.join(config.gamedir, "test.log")
    
    class ExplodeFactory: # the factory that makes the particles
        
        def __init__(self, theDisplayable, explodeTime=0, numParticles=10):
            self.displayable = theDisplayable
            self.time = explodeTime
            self.particleMax = numParticles
       
        def create(self, partList, timePassed):
                newParticles = None
                if partList == None or len(partList) < self.particleMax:
                    if timePassed < self.time or self.time == 0:
                        newParticles = self.createParticles()
                return newParticles
                
            
        def createParticles(self):
            timeDelay = renpy.random.random() * 0.6
            return [ExplodeParticle(self.displayable, timeDelay)]

        def predict(self):
            return [self.displayable]
    
    class ExplodeParticle:
        
        def __init__(self, theDisplayable, timeDelay):
            self.displayable = theDisplayable
            self.delay = timeDelay
            self.xSpeed = (renpy.random.random() - 0.5) * 25
            self.ySpeed = (renpy.random.random() - 0.5) * 25
            self.x = 640
            self.y = 360
        
        def update(self, theTime):
            
            if (theTime > self.delay):
                self.ySpeed += 0.2
                self.x += self.xSpeed
                self.y += self.ySpeed
                
                if self.x > 1280 or self.x < 0 or self.y > 720 or self.y < 0:
                    return None
        
            return (self.x, self.y, theTime, self.displayable)           

init:
    $ e = Character('Eileen', color="#c8ffc8")

    image eileen happy = "eileen_happy.png"
    image bg table = "#262F"
    image dim = "#0008"
    image boom = Particles(ExplodeFactory("card/back.png", numParticles=10, explodeTime = 5.0))  

    # Some styles for show text.
    $ style.centered_text.drop_shadow = (2, 2)
    $ style.centered_text.drop_shadow_color = "#000b"
                
label start:

    scene bg table
    
    show dim
    show eileen happy
    with dissolve

    e "Welcome to the Solitaire Project. Let's play some solitaire!"

    e "I might show up from time to time to give you some advice, but it's up to you if you want to take it."

    e "Good luck!"
  
label newgame:
    scene bg table
    
    show dim
    show eileen happy
    with dissolve

    menu:    
        e "What would you like to play?"

        "Klondike (Deal 1)":
            $ k = Klondike(1)
        "Klondike (Deal 3)":
            $ k = Klondike(3)
        "Double Klondike (Deal 1)":
            $ k = DblKlondike(1)
        "Double Klondike (Deal 3)":
            $ k = DblKlondike(3)
        "Spider (4 suits)":
            $ k = Spider(4)
        "Spider (2 suits)":
            $ k = Spider(2)
        "Spider (1 suit)":
            $ k = Spider(1)

        "Quit for now":
            e "Goodbye."
            return 

    e "Okay, here we go!"
    
    
label start_game:

    python:
        k.set_sensitive(False)
        k.show()
    

label continue:

    hide dim
    hide eileen
    with dissolve

label quick_continue:
    
    while True:

        python:
        
            ui.textbutton("Give Up", ui.jumps("giveup"), xalign=.02, yalign=.98)
            ui.textbutton("Hint", ui.jumps("hint"), xalign=.98, yalign=.98)
            k.set_sensitive(True)
            event = k.interact()

            if event:
                renpy.checkpoint()
            
        if event == "win":
            jump win

label win:

    show boom
    show dim
    show eileen happy
    with dissolve
    "Congratulations!"

    jump newgame

label giveup:

    $ k.set_sensitive(False)
    
    show dim
    show eileen happy
    with dissolve
    
    menu:
        e "Are you sure you want to give up?"

        "Yes":

            "Oh well, better luck next time."
            
            jump newgame

        "No":

            jump continue

    

label hint:

    $ under, over = k.hint()

    $ print under, over

    
    $ k.set_sensitive(False)
    
    show dim
    show eileen happy
    with dissolve

    if under is None or over is None:
        e "I can't see anything at the moment."
        jump continue
        
    $ under = k.card_name(under)
    $ over = k.card_name(over)

    $ hint = renpy.random.randint(0, 2)

    if hint == 0:
        e "Maybe put the %(over)s on top of the %(under)s."

    elif hint == 1:
        e "You can try moving the %(over)s to the %(under)s."

    elif hint == 2:
        e "I think something can go on the %(under)s."
    
    jump continue

