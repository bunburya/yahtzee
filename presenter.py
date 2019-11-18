#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO:
# - dict mapping player names to Players
# - dict mapping DieLabels to dice

from ui import GameInterface
from game import Game, GameOver

class Presenter:
    
    def __init__(self, players):
        self.ui = None
        self.player_names = players
        self.new_game()
    
    def new_game(self):
        
        self.game = Game(self.player_names)
        self.players = {p.name: p for p in self.game.players}
        # prepare Dice for iteration (for when we assign DieLabels)
        self.dice = iter(self.game.dice)
        self.dice_by_label = {}
        self.setup_ui()
    
    def setup_ui(self):
        if self.ui is not None:
            self.ui.destroy()
        self.ui = GameInterface(self)
        self.ui.run()
        
    def roll_dice(self):
        self.game.dice.roll()
        for d in self.ui.die_labels:
            self.update_die_label(d)
        if self.game.dice.rolled >= 3:
            self.ui.disable_roll()
    
    def update_die_label(self, die_label, init=False):
        # init is True if this is being called on the initialisation
        # of the DieLabel instance, in which case we set the associated
        # Die, rather than fetching it
        if init:
            die = next(self.dice)
            self.dice_by_label[die_label] = die
        else:
            die = self.dice_by_label[die_label]
        die_label.update_img(die.value, die.is_held)
    
    def toggle_die_hold(self, die_label):
        die = self.dice_by_label[die_label]
        if die.dice.rolled < 1:
            # Player has to roll all 5 dice on first roll
            return
        die.is_held = not die.is_held
        self.update_die_label(die_label)
        
    def next_turn(self):
        # Called when a player places his or her score.  Calls
        # game.next_player() and then updates the UI accordingly.
        print('next turn')
        try:
            self.game.next_player()
        except GameOver:
            print('game over')
            self.game_over()
        for p_name in self.players:
            self.ui.update_player_col(p_name)
        self.ui.enable_roll()
    
    def place_player_score(self, p_name, cat):

        if self.game.current_player.name != p_name:
            # Player is clicking on someone else's tiles,
            # so do nothing.
            return
        if self.game.dice.rolled < 1:
            # Player hasn't rolled yet so don't allow to place score.
            return
        score = self.game.current_player.scorecard.score(cat, self.game.dice)
        self.ui.add_player_score(p_name, cat, score)
        self.next_turn()
    
    def game_over(self):
        winners, highest_score = self.game.winners
        if len(winners) == 1:
            play_again = self.ui.notify_winner(winners[0].name, highest_score)
        else:
            play_again = self.ui.notify_draw([p.name for p in winners], highest_score)
        if play_again:
            self.new_game()
        else:
            self.quit()
    
    def quit(self):
        self.ui.quit()

if __name__ == '__main__':
    
    p = Presenter(['alan', 'mark', 'john'])
