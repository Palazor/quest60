# -*- coding: utf-8 -*-

import json

from quest_parser.parser import Dungeon
from quest_parser.visualize import Table

zid = 1584

dungeon = Dungeon(zid)
quests = dungeon.quests
with open('quest-{}-{}.json'.format(dungeon.dungeon, zid), 'w') as fp:
    json.dump(quests, fp, ensure_ascii=False)
# with open('quest-黑石深渊-1584.json') as fp:
#     quests = json.load(fp)

table = Table(quests)
print(table)
