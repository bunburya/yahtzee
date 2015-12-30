#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from collections import Counter
from operator import itemgetter
from itertools import groupby

class AlreadyScoredError(Exception): pass

class TurnOver(Exception):
    """Raised when a player's turn is over."""
    pass

class NoScoreType:
    
    """A class with a numerical value of 0, so is counted as 0 for the
    purpose of tallying scores, but is distinct from an int, so that the
    game can differentiate between cases where a score has not yet been
    entered for a given category and cases where a score of 0 has been
    entered.
    
    The class will be instantiated once and that instance used globally,
    like None.
    
    Is stringified to an empty string, rather than `0`."""
    
    def __int__(self):
        return 0
    
    def __str__(self):
        return ''
    
    def __add__(self, other):
        return other
    
    def __radd__(self, other):
        return other
    
NoScore = NoScoreType()

class Die:
    
    def __init__(self, dice, value=None):
        self.dice = dice
        self.is_held = False
        self.value = value or random.randint(1, 6)
    
    def roll(self):
        self.value = random.randint(1, 6)
        return self.value

class Dice:
    
    """Represents a set of five dice."""
    
    def __init__(self, values=None):
        if values is not None:
            self.dice = [Die(self, i) for i in values]
        else:
            self.dice = [Die(self, i) for i in range(1, 6)]
        self.rolled = 0
    
    def __iter__(self):
        self._i = 0
        return self
    
    def __next__(self):
        try:
            val = self.dice[self._i]
        except IndexError:
            raise StopIteration
        self._i += 1
        return val        

    def roll(self):
        for d in self.dice:
            if not d.is_held:
                d.roll()
            else:
                # If dice is marked as held, don't roll it, but un-mark
                # it for future rolls
                d.is_held = False
        self.rolled += 1
    
    def hold(self, indices):
        """Takes a sequence of indices, and marks the die at each index
        as being held.  Remember that 0 is the first die."""
        for i in indices:
            self.dice[i].is_held = True
    
    @property
    def count(self):
        return Counter(d.value for d in self.dice)
    
    @property
    def values(self):
        return [d.value for d in self.dice]
    
    @property
    def total(self):
        return sum(d.value for d in self.dice)

class Player:

    def __init__(self, name):
        self.name = name
        self.rolled = False
        self.scorecard = Scorecard()

class Scorecard:
    """A score card for a single player."""
    
    UPPER_SECTION = ['ones', 'twos', 'threes', 'fours', 'fives', 'sixes']
    LOWER_SECTION = ['3x', '4x', 'fh', 'ss', 'ls', 'y', 'c']
    CATEGORIES = UPPER_SECTION + LOWER_SECTION
    
    def __init__(self):
        self.scores = {c: NoScore for c in self.CATEGORIES}
        self.SCORE_FUNCS = {
            'ones': lambda d, p: self.upper(1, d),
            'twos': lambda d, p: self.upper(2, d),
            'threes': lambda d, p: self.upper(3, d),
            'fours': lambda d, p: self.upper(4, d),
            'fives': lambda d, p: self.upper(5, d),
            'sixes': lambda d, p: self.upper(6, d),
            '3x': self.three_kind,
            '4x': self.four_kind,
            'fh': self.full_house,
            'ss': self.short_straight,
            'ls': self.long_straight,
            'y': self.yahtzee,
            'c': self.chance
        }
            
    def handle_score(self, score, cat, preview=False):
        if not preview:
            if self.scores[cat] is not NoScore:
                raise AlreadyScoredError('Player has already entered score for this category.')
            self.scores[cat] = score
        return score

    def score(self, cat, dice, preview=False):
        try:
            return self.SCORE_FUNCS[cat](dice, preview)
        except AlreadyScoredError:
            pass
    
    def upper(self, n, dice, preview=False):
        """This function places scores in the upper section of the
        scorecard.  `n` is the number (1-6) that you want to score."""
        print(n, dice, preview)
        if 0 >= n >= 7:
            raise ValueError('n must be number between 1 and 6.')
        cat = self.UPPER_SECTION[n-1]
        print(dice)
        score = len([d.value for d in dice if d.value == n]) * n
        return self.handle_score(score, cat, preview)
    
    def _kind(self, n, cat, dice, preview=False):
        """General method for n-of-a-kind rolls."""
        for c in dice.count.values():
            if c >= n:
                score = dice.total
                break
        else:
            score = 0
        return self.handle_score(score, cat, preview)
    
    def three_kind(self, dice, preview=False):
        return self._kind(3, '3x', dice, preview)
    
    def four_kind(self, dice, preview=False):
        return self._kind(4, '4x', dice, preview)
    
    def full_house(self, dice, preview=False):
        if set(dice.count.values()) == {3, 2}:
            score = 25
        else:
            score = 0
        return self.handle_score(score, 'fh', preview)
    
    def _straight(self, n, cat, dice, preview=False):
        if 6 <= n <= 3:
            raise ValueError('n must be 4 or 5.')
        values = sorted({d.value for d in dice})
        for k, g in groupby(enumerate(values), lambda x:x[0]-x[1]):
            streak = list(map(itemgetter(1), g))
            if len(streak) >= n:
                score = 30 if n == 4 else 40
                break
        else:
            score = 0
        return self.handle_score(score, cat, preview)
    
    def short_straight(self, dice, preview=False):
        return self._straight(4, 'ss', dice, preview)
    
    def long_straight(self, dice, preview=False):
        return self._straight(5, 'ls', dice, preview)
    
    def yahtzee(self, dice, preview=False):
        if len({d.value for d in dice}) == 1:
            score = 50
        else:
            score = 0
        return self.handle_score(score, 'y', preview)
    
    def chance(self, dice, preview=False):
        score = dice.total
        return self.handle_score(score, 'c', preview)

    @property
    def upper_score(self):
        return sum(self.scores[c] for c in self.UPPER_SECTION)

    @property
    def bonus(self):
        return 35 if self.upper_score >= 63 else 0
    
    @property
    def total(self):
        return sum(self.scores.values()) + self.bonus
    
    @property
    def full(self):
        return not (NoScore in self.scores.values())
    
class Game:
    
    def __init__(self, players):
        self.players = [Player(p) for p in players]
        self.dice = Dice()
        self.scores = {p: Scorecard() for p in players}
        self._player_i = 0 # so current player is first in list
    
    @property
    def current_player(self):
        return self.players[self._player_i]

    def next_player(self):
        if self._player_i < (len(self.players)-1):
            self._player_i += 1
        else:
            self._player_i = 0
        self.dice.rolled = 0

    def gameloop(self):
        try:
            while True:
                try:
                    self.turnloop(p)
                except TurnOver:
                    self.next_player()
        except GameOver:
            self.game_over()
    
    def turnloop(self, player):
        try:
            while True:
                player.move()
        except TurnOver:
            return
        
