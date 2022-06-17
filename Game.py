### HELPER CLASS FOR MODERATOR.PY
### REPRESENTS AN INSTANCE OF A GAME

import os
import discord
import random

class Game:
    initMessageID = 0
    voteMessageId = 0
    specialMessageId = 0
    channelID = 0
    players = []
    mafia = []
    town = []
    toBeKilled = []
    numMafia = 0
    numTown = 0
    night = True
    cycleCount = 0
    voteInProgress = False
    mafiaKilled = False
    doctor = False
    vigi = False
    detective = False

    def __init__(self, mafia, town):
        self.initMessageID = 0
        self.voteMessageId = 0
        self.specialMessageId = 0
        self.channelID = 0
        self.numMafia = mafia
        self.numTown = town
        self.toBeKilled = []
        self.players = []
        self.mafia = []
        self.town = []
        self.night = True
        self.cycleCount = 0
        self.voteInProgress = False
        self.mafiaKilled = False
        self.doctor = False
        self.vigi = False
        self.detective = False

    def setRoles(self):
    ### RANDOMLY SELECTS MAFIA/TOWN ROLES FOR ALL PLAYERS
        random.seed()
        self.mafia = random.choices(self.players, k = self.numMafia)

        for x in self.players:
            self.town.append(x)

        for x in self.town:
            for y in self.mafia:
                if(y==x):
                    self.town.remove(x)

    def isMafia(self, member):
    ### CHECKS IF A MEMBER IS MAFIA
        for x in self.mafia:
            if(member == x):
                return True
        return False

    def isTown(self, member):
    ### CHECKS IF A MEMBER IS TOWN
        for x in self.town:
            if(member == x):
                return True
        return False
