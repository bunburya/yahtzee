#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import abspath, dirname, join
from sys import argv
import tkinter
from tkinter import N, W, E, S
from yahtzee import Game, TurnOver

# These are taken from yahtzee.py, TODO: pull them from a central source
# se we're not replicating code.
UPPER_SECTION = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
LOWER_SECTION = ['3x', '4x', 'fh', 'ss', 'ls', 'y', 'c']
CATEGORIES = UPPER_SECTION + LOWER_SECTION

# TODO: We have just implemented a Player class, so that needs to be
# reflected throughout the code.

class MenuCreationError: pass

class MenuBar(tkinter.Frame):
    
    def __init__(self, parent):
        self.parent = parent
        tkinter.Frame.__init__(self, parent)
    
    def create_menu(self, options, toplevel=False, parent=None):
        # Takes two arguments: option, and one of toplevel
        # or parent.
        # "option" is a tuple or list specifying the menu options.
        # "toplevel" is True if the menu is not a sub-menu of any
        # other menu.
        # "parent" is provided if the menu is a sub-menu and specifies
        # the sub-menu's parent menu.
        
        # An option tuple is a tuple of tuples, each representing a
        # menu item. Each sub-tuple usually contains three elements.
        # 0: The name of the option, and the text that will be
        #    displayed for the option.
        # 1: The option type; must be of a kind recognised by
        #    Tkinter's Menu.add() method.
        # 2: The command to be executed when the option is selected.
        #    If the option being created is a cascade menu, the command
        #    should be another option tuple which will be used to build
        #    the sub-menu.
        # If the option is a radiobutton, including a fourth element
        # (of any kind or value) will select the option by default.
        
        if toplevel:
            b_column, b_text = toplevel
            button = tkinter.Menubutton(self, text=b_text)
            button.grid(column=b_column, row=1, columnspan=1,
                sticky=W+N+E)
            button.menu = tkinter.Menu(button, tearoff=0)
            button["menu"] = button.menu
            my_menu = button.menu
        else:
            my_menu = parent
            
        for item in options:
            if item[1] == "cascade":
                cascade = tkinter.Menu(button, tearoff = 0)
                self.create_menu(item[2], parent=cascade)
                ##for submenu_item in item[2]:
                ##    cascade.add(submenu_item[1], label=submenu_item[0], command=submenu_item[2])
                my_menu.add_cascade(label=item[0], menu=cascade)
                
            elif item[1] == "radiobutton":
                try: group = item[3]
                except IndexError: raise MenuCreationError(
                    'Radiobutton "%s" requires additional "group" '
                    'argument.' % item[0])
                if not group in self.radio_ctrlvars:
                    self.radio_ctrlvars[group] = tkinter.StringVar()
                my_menu.add_radiobutton(label=item[0], command=item[2],
                    variable=self.radio_ctrlvars[group], value=item[0])
                if len(item) > 4:
                    self.radio_ctrlvars[group].set(item[0])
            else:
                my_menu.add(item[1], label=item[0], command=item[2])
    
    def setup_menus(self):
        
        filemenu = (
            ("Quit", "command", self.parent.quit),
            )
            
        menus = (
            ("File", filemenu),
            )
            
        for i, _menu in enumerate(menus):
            name, menu = _menu
            self.create_menu(menu, (i, name))
        
        

class PlayerColumn(tkinter.Frame):
    
    # We do this by *player*, ie, this class represents a column
    # that will contain a player name and that player's score for each
    # category.
    
    def __init__(self, parent, player, ui, **options):
        self.parent = parent
        self.player = player
        self.scorecard = self.player.scorecard
        self.ui = ui
        tkinter.Frame.__init__(self, parent, **options)
        self.setup()
    
    def update(self):
        # Update the column in light of current game state.
        if self.ui.game.current_player == self.player:
            self.config(relief='ridge')
        else:
            self.config(relief='flat')
        self.total_score_label.config(text=self.scorecard.total)

    def handle_click(self, event):
        if self.ui.game.current_player != self.player:
            # Player is clicking on someone else's tiles,
            # so do nothing.
            return
        if self.ui.game.dice.rolled < 1:
            # Player hasn't rolled yet so don't allow to place score.
            return
        cat = event.widget.category
        score = self.scorecard.score(cat, self.ui.game.dice)
        event.widget.config(text=score)
        print('score:', score)
        event.widget.config(relief='sunken')
        self.ui.next_turn()

    def setup(self):
        self.name_label = tkinter.Label(self, text=self.player.name)
        self.name_label.grid(row=0, column=0)
        self.score_labels = {}
        for r, c in enumerate(CATEGORIES):
            new_label = tkinter.Label(self, text='0')
            new_label.grid(row=r+1, column=0)
            new_label.player = self.player
            new_label.category = c
            new_label.bind('<ButtonRelease-1>', self.handle_click)
            self.score_labels[c] = new_label
        self.total_score_label = tkinter.Label(self, text='0')
        self.total_score_label.grid(row=len(CATEGORIES)+1, column=0)
        self.update()

class DieLabel(tkinter.Label):

    # A special label that holds a die.
    # Ultimately this will hold an image.

    def __init__(self, master, die, die_imgs, invert_die_imgs):
        self.die = die
        self.die_imgs = die_imgs
        self.invert_die_imgs = invert_die_imgs
        tkinter.Label.__init__(self, master)
        self.update()

    def update(self, value=None, held=None):
        if value is None:
            value = self.die.value
        if held is None:
            held = self.die.is_held
        if held:
            img = self.invert_die_imgs[value-1]
        else:
            img = self.die_imgs[value-1]
        self.config(image=img)
        
    
    def toggle_hold(self, event):
        if self.die.dice.rolled < 1:
            # Player has to roll all 5 dice on first roll
            return
        self.die.is_held = not self.die.is_held
        self.update()


class GameInterface(tkinter.Frame):
    
    def __init__(self, players, master=None):
        self.game = Game(players)
        tkinter.Frame.__init__(self, master)
        self.get_die_images()
        self.create_widgets(self.game.players)
        self.grid()
    
    def get_die_images(self):
        # Get images and store them as PhotoImage objects
        gfx_dir = join(dirname(abspath(argv[0])), 'gfx')
        die_img_path = join(gfx_dir, 'dice_{}.png')
        invert_img_path = join(gfx_dir, 'dice_{}_invert.png')
        self.die_imgs = []
        self.invert_die_imgs = []
        for i in range(6):
            img_fname = die_img_path.format(i+1)
            invert_fname = invert_img_path.format(i+1)
            self.die_imgs.append(tkinter.PhotoImage(file=img_fname))
            self.invert_die_imgs.append(
                                tkinter.PhotoImage(file=invert_fname))
    
    def roll_dice(self):
        # This function is bound to the "roll" button.
        self.game.dice.roll()
        for d in self.die_labels:
            d.update()
        if self.game.dice.rolled >= 3:
            self.roll_button.config(state=tkinter.DISABLED)

    def create_widgets(self, players):
        
        menu_frame = MenuBar(self)
        menu_frame.setup_menus()
        menu_frame.grid(row=0, columnspan=2, sticky=W)
        score_frame = tkinter.Frame(self)
        cat_frame = tkinter.Frame(score_frame)
        
        empty_label = tkinter.Label(cat_frame, text='')
        empty_label.grid(column=0)
        
        for i, c in enumerate(CATEGORIES):
            label = tkinter.Label(cat_frame, text=c)
            label.grid(column=0)
        
        total_label = tkinter.Label(cat_frame, text="Total")
        total_label.grid(column=0)
        
        cat_frame.grid(row=1, column=0)
        
        players_frame = tkinter.Frame(score_frame)
        self.player_cols = {}
        for i, p in enumerate(players):
            pcol = PlayerColumn(players_frame, p, self, bd='2')
            pcol.grid(row=0, column=i+1)
            self.player_cols[p] = pcol

        dice_frame = tkinter.Frame(self)
        self.die_labels = []
        self.roll_button = tkinter.Button(dice_frame, text="Roll",
                            command=self.roll_dice)
        self.roll_button.grid(column=0)
        for i, d in enumerate(self.game.dice):
            dlabel = DieLabel(dice_frame, d, self.die_imgs,
                                self.invert_die_imgs)
            dlabel.bind('<ButtonRelease-1>', dlabel.toggle_hold)
            dlabel.grid(row=0, column=i+1)
            self.die_labels.append(dlabel)
        
        players_frame.grid(row=1, column=1)
        score_frame.grid(row=1, column=0)
        dice_frame.grid(row=2, column=0)

    def next_turn(self):
        # Called when a player places his or her score.  Calls
        # game.next_player() and then updates the UI accordingly.
        print('next turn')
        self.game.next_player()
        for pcol in self.player_cols.values():
            pcol.update()
        self.roll_button.config(state=tkinter.NORMAL)
    
    def quit(self):
        quit()
            
if __name__ == '__main__':
    root = tkinter.Tk()
    players = ['alan', 'john', 'fred']  # todo: get player names
    ui = GameInterface(players)
    ui.mainloop()
