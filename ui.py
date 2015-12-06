#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter
from yahtzee import Game

# These are taken from yahtzee.py, TODO: pull them from a central source
# se we're not replicating code.
UPPER_SECTION = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
LOWER_SECTION = ['3x', '4x', 'fh', 'ss', 'ls', 'y', 'c']
CATEGORIES = UPPER_SECTION + LOWER_SECTION



class PlayerColumn(tkinter.Frame):
    
    # We do this by *player*, ie, this class represents a column
    # that will contain a player name and that player's score for each
    # category.
    
    def __init__(self, parent, player, ui):
        self.parent = parent
        self.player = player
        self.ui = ui
        tkinter.Frame.__init__(self, parent)
        self.setup()
    
    def handle_click(self, event):
        if self.ui.game.current_player != self.player:
            # Player is clicking on someone else's tiles,
            # so do nothing.
            return
        scorecard = self.ui.game.scores[self.player]
        cat = event.widget.category
        score = scorecard.score(cat, self.ui.game.dice)
        event.widget.config(text=score)
        print('score:', score)
        event.widget.config(relief='sunken')
    
    def setup(self):
        self.name_label = tkinter.Label(self, text=self.player)
        self.name_label.grid(row=0, column=0)
        self.score_labels = {}
        for r, c in enumerate(CATEGORIES):
            new_label = tkinter.Label(self, text='0')
            new_label.grid(row=r+1, column=0)
            new_label.player = self.player
            new_label.category = c
            new_label.bind('<ButtonRelease-1>', self.handle_click)
            self.score_labels[c] = new_label

class DieLabel(tkinter.Label):

    # A special label that holds a die.  Ultimately this will hold an image.

    def __init__(self, master, die):
        self.die = die
        tkinter.Label.__init__(self, master, text=die.value)

    def toggle_hold(self, event):
        self.die.is_held = not self.die.is_held
        self.config(relief='sunken' if self.die.is_held else 'flat')

    def update(self):
        self.config(text=self.die.value)
        self.config(relief='sunken' if self.die.is_held else 'flat')


class GameInterface(tkinter.Frame):
    
    def __init__(self, players, master=None):
        self.game = Game(players)
        tkinter.Frame.__init__(self, master)
        self.create_widgets(players)
        self.grid()
    
    def roll_dice(self, event):
        # This function is bound to the "roll" button.
        self.game.dice.roll()
        for d in self.die_labels:
            d.update()

    def create_widgets(self, players):
        
        score_frame = tkinter.Frame(self)
        cat_frame = tkinter.Frame(score_frame)
        
        empty_label = tkinter.Label(cat_frame, text='')
        empty_label.grid(row=0, column=0)
        
        for i, c in enumerate(CATEGORIES):
            label = tkinter.Label(cat_frame, text=c)
            label.grid(row=i+1, column=0)
        
        cat_frame.grid(row=0, column=0)
        
        players_frame = tkinter.Frame(score_frame)
        self.player_cols = {}
        for i, p in enumerate(players):
            pcol = PlayerColumn(players_frame, p, self)
            pcol.grid(row=0, column=i+1)
            self.player_cols[p] = pcol

        dice_frame = tkinter.Frame(self)
        self.die_labels = []
        roll_label = tkinter.Label(dice_frame, text="Roll")
        roll_label.bind('<ButtonRelease-1>', self.roll_dice)
        roll_label.grid(row=0, column=0)
        for i, d in enumerate(self.game.dice):
            dlabel = DieLabel(dice_frame, d)
            dlabel.bind('<ButtonRelease-1>', dlabel.toggle_hold)
            dlabel.grid(row=0, column=i+1)
            self.die_labels.append(dlabel)
        
        players_frame.grid(row=0, column=1)
        score_frame.grid(row=0, column=0)
        dice_frame.grid(row=1, column=0)
            
if __name__ == '__main__':
    root = tkinter.Tk()
    players = ['alan', 'john', 'fred']  # todo: get player names
    ui = GameInterface(players)
    ui.mainloop()