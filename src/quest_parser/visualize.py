# -*- coding: utf-8 -*-

from quest_parser.configs import *


class Quest(object):
    def __init__(self, quest):
        self.quest = quest

    def __str__(self):
        title = self.quest['title']
        title = title if self.quest['in'] else SILVER_FORMAT.format(title)
        return QUEST_FORMAT.format(self.quest['qid'], title, self.quest['start'], self.quest['end'])


class Tr(object):
    def __init__(self, series):
        self.series = series

        quest_items = []
        main_quest = None
        for quest in self.series:
            quest_items.append(Quest(quest))
            if main_quest is None and quest['in']:
                main_quest = quest

        self.ah = main_quest['ah']
        self.quest_items = quest_items
        self.main_quest = main_quest

    def __str__(self):
        ah = IMG_A if 'A' in self.ah else ''
        if 'H' in self.ah:
            ah += IMG_H

        return TR_FORMAT.format(ah, self.main_quest['title'], '\n'.join(str(item) for item in self.quest_items))


class Table(object):
    def __init__(self, quests):
        self.quests = []

        self._parse_quests(quests)

    def _parse_quests(self, quests):
        series_set = set([','.join(quest['series']) for quest in quests.values()])
        series_list = sorted(series_set, key=lambda x: len(x), reverse=True)

        for series_id in series_list:
            series = [quests[qid] for qid in series_id.split(',')]
            self.quests.append(Tr(series))

    def __str__(self):
        quests = sorted(self.quests, key=lambda x: x.ah)
        return TABLE_FORMAT.format('\n\n'.join([str(item) for item in quests]))
