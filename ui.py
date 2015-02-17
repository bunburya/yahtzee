#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter

# These are taken from yahtzee.py, TODO: pull them from a central source
# se we're not replicating code.
UPPER_SECTION = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
LOWER_SECTION = ['3x', '4x', 'fh', 'ss', 'ls', 'y', 'c']
CATEGORIES = UPPER_SECTION + LOWER_SECTION

class PlayerColumn(tkinter.Frame):
    
    # We do this by *player*, ie, this class represents a column
    # that will contain a player name and that player's score for each
    # category.
    
    def __init__(self, parent, player):
        self.parent = parent
        self.player = player
        tkinter.Frame.__init__(self, parent)
        self.setup()
    
    def handle_click(self, event):
        print('i am clicked')
    
    def setup(self):
        self.name_label = tkinter.Label(self, text=self.player)
        self.name_label.grid(row=0, column=0)
        self.score_labels = {}
        for r, c in enumerate(CATEGORIES):
            self.score_labels[c] = tkinter.Label(self, text='0')
            self.score_labels[c].grid(row=r+1, column=0)
            self.score_labels[c].bind('<ButtonRelease-1>', self.handle_click)
    

class GameInterface(tkinter.Frame):
    
    def __init__(self, players, master=None):
        tkinter.Frame.__init__(self, master)
        self.create_widgets(players)
        self.grid()
    
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
        
        for i, p in enumerate(players):
            pcol = PlayerColumn(players_frame, p)
            pcol.grid(row=0, column=i+1)
        
        players_frame.grid(row=0, column=1)
        score_frame.grid(row=0, column=0)
            
if __name__ == '__main__':
    root = tkinter.Tk()
    ui = GameInterface(['alan', 'john', 'fred'])
    ui.mainloop()
