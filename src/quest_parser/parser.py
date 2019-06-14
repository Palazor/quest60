# -*- coding: utf-8 -*-

from queue import Queue
import time

from bs4 import BeautifulSoup

from quest_parser.configs import QUEST_URL
from quest_parser.configs import ZONE_URL
from quest_parser.utils import get_html


class Quest(object):

    def __init__(self, dungeon, qid):
        self.dungeon = dungeon
        self.qid = qid

        html = get_html(QUEST_URL.format(qid))
        self._soup = BeautifulSoup(html, 'html5lib')

        self.info = None
        self.prev = []
        self.list = None
        self.next = []

        if html is not None:
            self.info = {'qid': qid, 'ah': 'AH', 'in': True, 'series': []}
            self._parse_quest()

    def _parse_info(self, info):
        for li in info.select('li'):
            try:
                key, value = li.text.split(':')
            except:
                continue

            value = value.strip()

            if '任务类型' in key and '地下城' != value:
                self.info['in'] = False
            elif '所属地区' in key and self.dungeon != value:
                self.info['in'] = False
            elif '阵营要求' in key:
                if '联盟' == value:
                    self.info['ah'] = 'A'
                elif '部落' == value:
                    self.info['ah'] = 'H'
            elif '开始' in key:
                self.info['start'] = value
            elif '结束' in key:
                self.info['end'] = value

    def _parse_quest_list(self, quest_list):
        qid_list = []
        for li in quest_list.select('li'):
            if li.a:
                qid_list.append(li.a.get('href').split('/')[-1])
            elif 'active' in li.get('class'):
                qid_list.append(self.qid)
        return qid_list

    def _parse_quest(self):
        title = self._soup.select('.main .main_box .main_info .top .title h1')
        if title:
            self.info['title'] = title[0].text

        series = self._soup.select('.sidebar_box,.quickfacts')[0]

        info = series.select('.info')[0]
        self._parse_info(info)

        for ul in series.select('ul'):
            ul_class = ul.get('class')
            if 'quest_list_event' in ul_class:
                if self.list is None and not self.prev:
                    self.prev = self._parse_quest_list(ul)[:1]
                else:
                    self.next = self._parse_quest_list(ul)[:1]
            elif 'quest_list' in ul_class:
                self.list = self._parse_quest_list(ul)

        if self.list is None:
            self.list = [self.qid]

        full_list = self.info['series']
        full_list.extend(self.prev)
        full_list.extend(self.list)
        full_list.extend(self.next)

    @property
    def detail(self):
        return self.info


class Dungeon(object):

    def __init__(self, zid, banned_qid=None):
        self.zid = zid
        self.banned_qid = set([str(qid) for qid in banned_qid]) if banned_qid is not None else set()
        self.dungeon = None

        start = time.time()
        html = get_html(ZONE_URL.format(zid))
        print('Dungeon data downloaded in {:>.2f} seconds'.format(time.time() - start))
        self._soup = BeautifulSoup(html, 'html5lib')

        self.quests = {}
        self.qids = Queue()
        self.qid_set = set()

        self._parse_quests()

    def _add_quest(self, quest):
        new_series = quest['series']

        series = None
        for qid in new_series:
            if qid in self.quests:
                series = self.quests[qid]['series']
                break

        if series is not None:
            old_short = series[0] in new_series
            found = False
            ins = 0
            for i, qid in enumerate(new_series):
                if qid not in series:
                    if old_short and not found:
                        series.insert(ins, qid)
                        ins += 1
                    else:
                        series.extend(new_series[i:])
                        break
                else:
                    found = True
            quest['series'] = series

        series = quest['series']
        for qid in series:
            if qid not in self.qid_set:
                self.qids.put(qid)
                self.qid_set.add(qid)

        self.quests[quest['qid']] = quest

    def _parse_quests(self):
        main = self._soup.select('.main .main_box .main_info')[0]
        self.dungeon = main.select('.top .title h1')[0].text

        quests = main.select('.grid .grid-table table tbody tr')[1:]
        for tr in quests:
            tds = tr.select('td')
            try:
                title = tds[0].a
                qid = title.get('href').split('/')[-1]
                if qid in self.banned_qid:
                    continue
                self.qids.put(qid)
                self.qid_set.add(qid)
            except:
                continue

        print('Start with {} quests'.format(self.qids.qsize()))
        while self.qids.qsize():
            qid = self.qids.get()
            if qid in self.quests:
                continue

            start = time.time()
            quest = Quest(self.dungeon, qid)
            print('Quest {} data downloaded in {:>.2f} seconds'.format(qid, time.time() - start))

            if quest.detail is not None:
                self._add_quest(quest.detail)

            time.sleep(0.5)
