

def draw_menu(stdscr, title, menu_items):
    h, w = stdscr.getmaxyx()
    to_draw = title + menu_items
    x = (w - len(title[0])) // 3
    y = (h - len(to_draw)) // 3
    cursor_x = x
    cursor_y = y + len(title) + 1
    for item in to_draw:
        if item in menu_items:
            item = "  " + item
        y += 1
        stdscr.addstr(y, x, item)
    return cursor_x, cursor_y

def display_menu(stdscr):
    """ Displays the initial menu. Returns None if quit is selected or q
        is pressed. Returns "cont" or "newgame" if such options are
        selected. """
    menu_items = (
        "Continue",
        "New game",
        "Help",
        "Credits",
        "Quit",
        )
    # I'm not using a dict here to preserve order
    menu_items_actions = (
        "cont",
        "newgame",
        "help",
        "credits",
        "quit",
        )
    title = ("-------------",
             "|Rock Tunnel|",
             "-------------")
    cursor_x, cursor_y = draw_menu(stdscr, title, menu_items)

    cursor_i = 0
    while True:
        draw_menu(stdscr, title, menu_items)
        stdscr.addch(cursor_y+cursor_i, cursor_x, "*")
        k = stdscr.getkey()
        stdscr.addch(cursor_y+cursor_i, cursor_x, " ")
        if k == "j" or k == "KEY_DOWN":
            if cursor_i < len(menu_items)-1:
                cursor_i += 1
            else:
                cursor_i = 0
        elif k == "k" or k == "KEY_UP":
            if cursor_i > 0:
                cursor_i -= 1
            else:
                cursor_i = len(menu_items)-1
        elif k == "q":
            return
        elif k == "KEY_ENTER" or k == "\n" or k == " ":
            action = menu_items_actions[cursor_i]
            if action == "help":
                show_big_msg(stdscr, help_txt)
            elif action == "credits":
                show_big_msg(stdscr, credits_txt)
            elif action == "quit":
                return
            else:
                return action

def show_big_msg(stdscr, msg):
    msg = msg.split("\n")
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    x = (w-80)//3
    y = (h-len(msg))//4
    for l in msg:
        stdscr.addstr(y, x, l)
        y += 1
    stdscr.getkey()
    stdscr.clear()

credits_txt = ("A game by:\n"
        "Jaume Delclòs, aka cosarara97\n")

help_txt = ("Help:\n"
        "You are the @, enemies are represented by other letters.\n"
        "Use hjklyubn or the arrows of shame to move.\n"
        "Run into an enemy to battle it, pokemon style.\n"
        "You can wait by pressing s.\n"
        "No matter what you do, you regain health with every move.\n"
        "This game is completely turn based, nothing will happen\n"
        "until you move.\n"
        "Press q if you want to quit without saving, or S to save and quit.")

intro_txt = ("You are Pikachu.\n"
        "You entered the rock tunnel to explore, and just after you\n"
        "entered the path got blocked. There is no going back.")

