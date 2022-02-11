from json import loads
from asyncio import get_event_loop, gather
from aiohttp import ClientSession, TCPConnector

# UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
#      'Chrome/91.0.4472.77 Safari/537.36'
HEADER = {
    # "User-Agent": UA,
    "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
}


async def get_url(url, hard=True):
    while True:
        try:
            async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                async with session.get(url, headers=HEADER) as r:
                    _result = await r.text()
                    if hard:
                        if r.status == 200:
                            return _result
                    else:
                        if r.status == 200:
                            return _result
                        elif r.status == 403:
                            return None
        except Exception as e:
            print(e)


async def post_url(url, data, hard=True):
    while True:
        try:
            async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                async with session.post(url, headers=HEADER, json=data) as r:
                    _result = await r.text()
                    if hard:
                        if r.status == 200:
                            return _result
                    else:
                        if r.status == 200:
                            return _result
                        elif r.status == 403:
                            return None
        except Exception as e:
            print(e)


def get_feed(account):
    data_all = [{"req": {"accountAddress": account},
                 "page": {"pageSize": 200, "page": 1}}]
    tasks = [post_url('https://api.skyweaver.net/rpc/SkyWeaverAPI/GetFeed', data, False) for data in data_all]
    _results = get_event_loop().run_until_complete(gather(*tasks))
    result_dict = loads(_results[0])
    total = result_dict['page']['totalRecords']
    # pages = (total - 1) // 200 + 1
    pages = 1
    data_all = [{"req": {"accountAddress": account},
                 "page": {"pageSize": 200, "page": i+1}} for i in range(pages)]
    tasks = [post_url('https://api.skyweaver.net/rpc/SkyWeaverAPI/GetFeed', data, False) for data in data_all]
    _results = get_event_loop().run_until_complete(gather(*tasks))
    for result in _results:
        last_time = ''
        mode_map = {}  # RANKED_CONSTRUCTED CONQUEST_CONSTRUCTED
        reward_map = {'SW_SILVER_CARDS': 0, 'SW_GOLD_CARDS': 0, 'SW_BASE_CARDS': 0}
        ticket_used = 0
        result_dict = loads(result)
        for item in result_dict['res']:
            if item['type'] == 'REWARD':
                is_conquest = False
                cards = item['cards']
                for card in cards:
                    if card['itemType'] == "SW_SILVER_CARDS":
                        reward_map['SW_SILVER_CARDS'] += 1
                        is_conquest = True
                    elif card['itemType'] == "SW_GOLD_CARDS":
                        reward_map['SW_GOLD_CARDS'] += 1
                        is_conquest = True
                        ticket_used += 1
                    elif card['itemType'] == "SW_BASE_CARDS":
                        reward_map['SW_BASE_CARDS'] += 1
                # if is_conquest:
                #     ticket_used += 1
            if item['type'] == 'MATCH':  # LEVELUP, REWARD
                match = item['match']
                mode = match['mode']
                if match['player1']['address'] == account:
                    number = 1
                    player = match['player1']
                else:
                    number = 2
                    player = match['player2']
                deck = player['deckString']
                if match['winningPlayer'] == number:
                    winned = True
                else:
                    winned = False
                last_time = match['endedAt']

                if mode in ['CONQUEST_CONSTRUCTED', 'CONQUEST_DISCOVERY']:
                    if not winned:
                        ticket_used += 1

                if mode not in mode_map:
                    mode_map[mode] = {'W': 0, 'L': 0, 'D': {}}
                if winned:
                    mode_map[mode]['W'] += 1
                else:
                    mode_map[mode]['L'] += 1
                if deck not in mode_map[mode]['D']:
                    mode_map[mode]['D'][deck] = {'W': 0, 'L': 0}
                if winned:
                    mode_map[mode]['D'][deck]['W'] += 1
                else:
                    mode_map[mode]['D'][deck]['L'] += 1
        for mode in mode_map:
            _w = mode_map[mode]['W']
            _l = mode_map[mode]['L']
            wr = _w / (_w + _l) * 100
            print(f"  --{mode}--  {_w}W{_l}L {wr:.1f}%")
            if (mode == 'RANKED_CONSTRUCTED') or (mode == 'CONQUEST_CONSTRUCTED'):
                D_sort = sorted(mode_map[mode]['D'].items(), key=lambda d: d[1]['W'] + d[1]['L'], reverse=True)
                for deck, dd in D_sort:
                    _w = dd['W']
                    _l = dd['L']
                    wr = _w / (_w + _l) * 100
                    print(f"{dd['W']}W{dd['L']}L {wr:.1f}% {deck}")
        
        print('####出金率###: ', int(100 * (reward_map['SW_GOLD_CARDS'] / ticket_used)), '%'  )
        print(ticket_used / reward_map['SW_GOLD_CARDS'], '票一金')
        for reward in reward_map:
            print(f"{reward_map[reward]} {reward}")
        print(f"{ticket_used} tickets used")
        print(f"{last_time}")



def run():
        print('5群内卷榜')
        print('---------------------------------------------')
        print('5哥')
        get_feed('0x814a7f72b64e4b7c20bd138be90f111abc187ecb')
        print('---------------------------------------------')
        print('Storm')
        get_feed('0xe5856FEFB63D88fDdafD1B166E47DE486DF9845d')
        print('---------------------------------------------')
        print('A宝')
        get_feed('0xd30Ee42Ce365Da9F7590d453a0e89aD39CffE1f4')
        print('---------------------------------------------')
        print('冰队')
        get_feed('0x8563AB624452420760814B08415dF81934cDb1E7')
        print('---------------------------------------------')
        print('Y哥')
        get_feed('0xF8e51fbd802F1B0D6c29155fb9C9DDa8D93fB84E')
        print('---------------------------------------------')
        print('咪宝')
        get_feed('0xf4866719f288d6e314abDcF931B4f1BCFbC96780')
        print('yexx天梯第一')
        get_feed('0xd7559dd61b9f25daf09d31378be80d81632e7d86')
        print('shenggou')
        get_feed('0x89a200079e6e2d0f1b0593e820770ce196aedc27')
        print('xiayu')
        get_feed('0x966fdd0cbf5d4a9d4d5c1d0cafa7f12f257ee1bb')
        print('Felzak')
        get_feed('0x373578b5918462ba58c7a791e1f9e32ca42e2d2c')
        print('dark')
        get_feed('0xff23ea3ccb5842524e574f8c1be4f30988b960ff')
        print('lv')
        get_feed('0xcbb149b3e49e5e0432d336f38d6313c4e1d56453')
        print('joker')
        get_feed('0x9f7a3b6d885b5ed5386c9b00d337f29c49185a1f')



if __name__ == '__main__':
    run()
# 'https://skyweaverstats.com/deck/'  # 好用一点 也废了
# 'https://skyweaverdecks.com/decks/'  # 废了
