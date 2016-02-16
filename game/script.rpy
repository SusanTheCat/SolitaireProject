# You can place the script of your game in this file.

init python:
    
    import os
    #config.log = os.path.join(config.gamedir, "test.log")

    # Set the default value.
    if persistent.autofinish is None:
        persistent.autofinish = True
    
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

    e "If you want, I can try to give you some advice, but it's up to you if you want to take it."

    e "Good luck!"
  
label newgame:
    scene bg table
    
    show dim
    show eileen happy
    with dissolve

    call screen game_choice

    $ k = _return
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
    

    
screen game_choice:



    # Put the navigation columns in a three-wide grid.
    grid 3 1:
        xfill True
        yalign 0.4
        # The left column.
        vbox:
            frame:
                has vbox
                textbutton _("Klondike (Deal 1)") xfill True action Return(Klondike(1))
                textbutton _("Klondike (Deal 3)") xfill True action Return(Klondike(3))
            frame:
                has vbox
                textbutton _("Double Klondike (Deal 1)") xfill True action Return(DblKlondike(1))
                textbutton _("Double Klondike (Deal 3)") xfill True action Return(DblKlondike(3))
               
        vbox:
            frame:
                has vbox 
                textbutton _("Spider (4 suits)") xfill True action Return(Spider(4))
                textbutton _("Spider (2 suits)") xfill True action Return(Spider(2))
                textbutton _("Spider (1 suit)") xfill True action Return(Spider(1))
                
        vbox:
            frame:
                has vbox 
                textbutton _("Canfield") xfill True action Return(Canfield())

