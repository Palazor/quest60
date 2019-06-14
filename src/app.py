# -*- coding: utf-8 -*-

import json
import re
import sys

from quest_parser.configs import NAME2ZID
from quest_parser.parser import Dungeon
from quest_parser.visualize import Table

zid = 1584
banned_qid = [9015]

argv = sys.argv
argc = len(argv)
if argc > 1:
    zone = argv[1]
    if re.match('^\d+$', zone):
        zid = zone
    elif zone in NAME2ZID:
        zid = NAME2ZID[zone]
    else:
        print('Invalid dungeon name')
        exit(-1)

if argc > 2:
    banned_qid = argv[2:]

dungeon = Dungeon(zid, banned_qid)
quests = dungeon.quests
with open('quest-{}-{}.json'.format(dungeon.dungeon, zid), 'w') as fp:
    json.dump(quests, fp, ensure_ascii=False)
# with open('quest-黑石深渊-1584.json') as fp:
#     quests = json.load(fp)

table = Table(quests)
print(table)
