# You can place the script of your game in this file.

init:
    $ e = Character('Eileen', color="#c8ffc8")

    image eileen happy = "eileen_happy.png"
    image bg table = "#262F"
    image dim = "#0008"

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
    
    $ hint_count = renpy.random.randint(10, 20)
    
    while True:

        python:
        
            ui.textbutton("Give Up", ui.jumps("giveup"), xalign=.02, yalign=.98)
            k.set_sensitive(True)
            event = k.interact()

            if event:
                renpy.checkpoint()
            
        if event == "win":
            jump win

        if event == "tableau_drag" or event == "stock_click":
            $ hint_count -= 1
            if hint_count <= 0:
                jump hint

label win:

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

    if under is None:
        jump quick_continue
        
    $ under = k.card_name(under)
    $ over = k.card_name(over)
    
    $ k.set_sensitive(False)

    show dim
    show eileen happy
    with dissolve

    $ hint = renpy.random.randint(0, 2)

    if hint == 0:
        e "Maybe put the %(over)s on top of the %(under)s."

    elif hint == 1:
        e "You can try moving the %(over)s to the %(under)s."

    elif hint == 2:
        e "I think something can go on the %(under)s."
    
    jump continue

