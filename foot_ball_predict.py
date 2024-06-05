import json
import threading
import time
import datetime
import ws_mange

my_set = set()
name_id_dict = dict() #缓存detail详情
import requests
id_dict = dict()
way_dict = dict() #主客方向不反买
data_dict = dict()
game_detail = dict()
game_score_data = dict()
game_pan_lj = dict()
goal_time = dict() #比分时间 防止盘口关闭
bet_log = dict() #记录上次下注方向和比分
duixian_data = dict()
sofa_score_data = dict()
his = 0.4
now = 0.6
game_bet_dict = dict()
cp = dict()

def setbili(his_,now_):
    global his,now
    his=  his_
    now=  now_




def get_data():
    try:
        resp = requests.get(
            '*********', #联系作者 wx   zuonwang
            timeout=2)
        #print(resp.json())
        return resp.json()['data']
    except Exception as e:
        print("timeout")
        return None
def getScoreData():
    return game_score_data



def submit_delayed_task(delay, func, args):
    def delayed_execution():
        time.sleep(delay)
        func(*args)

    thread = threading.Thread(target=delayed_execution)
    thread.start()
def g_send_pan(host_goal, away_goal, minute, pan, t, k, money, game_data,dec):
    d = {
        'game_data':game_data,
        'host_goal': host_goal,
        'away_goal': away_goal,
        'time': minute,
        'HT': pan[0],
        'dec': 0.95,
        'type': t,
        'id': k,
        'tag':dec
    }
    print('比赛预测自动推送', d)
    ws_mange.board_msg(json.dumps(d))
class auto_push_thread_by_target_off(threading.Thread):
    def __init__(self):
        super().__init__()
        self.dec_dict =  dict()
        self.zp_dict =  dict()
    def predict(self,predict_data):
        try:
            resp = requests.post("***********", json=predict_data,timeout=5) #联系作者 wx   zuonwang
            return resp.json()
        except Exception as e:
            pass
    def send_pan(self, host_goal, away_goal, minute, pan, t, k, money, game_data,dec):
        d = {
            'game_data':game_data,
            'host_goal': host_goal,
            'away_goal': away_goal,
            'time': minute,
            'HT': pan[0],
            'dec': 0.95,
            'type': t,
            'id': k,
            'tag':dec
        }
        print('比赛预测自动推送', d)
        ws_mange.board_msg(json.dumps(d))




    def run(self):
        while True:
            data = get_data()
            #这里重新解析data
            if data is None:
              #  print('====no data====')
                time.sleep(1)
                continue
            new_data = {}
            for k in data:
                try:
                    new_data[k] = {}
                    or_data = data[k]
                    host_game_data = or_data['hostData']
                    away_game_data = or_data['awayData']
                    pan_data = [j for j in or_data['panData'][1] if j[0]=='36*'][0]
                    new_data[k]['event'] = f'{or_data["cnHost"]} vs {or_data["cnAway"]}'
                    new_data[k]['lea'] = or_data["cnLeague"]
                    new_data[k]['host_score'] = or_data['hostScore']
                    new_data[k]['away_score'] = or_data['awayScore']
                    new_data[k]['host_target'] =host_game_data.get("5") if host_game_data.get("5") else 0
                    new_data[k]['away_target'] = away_game_data.get("5") if  away_game_data.get("5") else 0
                    new_data[k]['host_off'] =host_game_data.get("8") if host_game_data.get("8") else 0
                    new_data[k]['away_off'] =away_game_data.get("8") if away_game_data.get("8") else 0
                    new_data[k]['host_danger'] = host_game_data.get("7") if host_game_data.get("7") else 0
                    new_data[k]['away_danger'] =away_game_data.get("7") if away_game_data.get("7") else 0
                    new_data[k]['host_pan'] = float(pan_data[2])
                    new_data[k]['away_pan'] = -float(pan_data[2])
                    new_data[k]['host_pan_odd'] = round(1+float(pan_data[1]),2)
                    new_data[k]['away_pan_odd'] = round(1+float(pan_data[3]),2)
                    new_data[k]['minute'] = or_data['minute']
                   # print(new_data[k])
                except Exception as e:
                    pass
            if new_data:
                for k in new_data:
                    game_data = new_data[k]
                    try:
                     #   print(game_data)
                        host_goal = int(game_data['host_score'])
                        away_goal = int(game_data['away_score'])
                        minute = game_data['minute']
                        host_market_data = []
                        away_market_data = []
                        host_market_data.append((game_data['host_pan'],game_data['host_pan_odd']))
                        away_market_data.append((game_data['away_pan'],game_data['away_pan_odd']))
                        away_market_data.sort(key=lambda l: l[0], reverse=True)
                        goal_ = game_data['host_score']+"-"+game_data['away_score']
                        if k not in goal_time:
                            goal_time[k] = [goal_,datetime.datetime.now() - datetime.timedelta(seconds=91),None]
                        #判断比分是否改变
                        if goal_ != goal_time[k][0]:
                            pre_h_g,pre_a_g = goal_time[k][0].split("-")
                            now_h_g,now_a_g= goal_.split("-")
                            goal_t = None
                            if pre_h_g!=now_h_g:
                                goal_t = 'Home'
                            if pre_a_g!=now_a_g:
                                goal_t = 'Away'
                            #这里判断是否进行追盘
                            if k in self.zp_dict:
                                for t,send_pan,dec,money_data,zp_rate in self.zp_dict[k]:
                                    #那这里就进行匹配最新相似盘口进行投注 #追涨 追跌设置障碍 最多追两次跌
                                    select_pan = None
                                    select_type = None
                                    min_diff = 100
                                    money,total = money_data
                                    if 'Home' in t and zp_rate[0]: #追利润
                                        if goal_t=='Home':
                                            #追主队
                                            select_type = 'Home'
                                            for host_pan in host_market_data:
                                                diff = abs(host_pan[0]-send_pan[0])
                                                if diff<min_diff:
                                                    select_pan = host_pan
                                                    min_diff = diff
                                        else:
                                            zp_rate[0] = False
                                    else:
                                        if goal_t =='Away' and zp_rate[0]:
                                            select_type = 'Away'
                                            for away_pan in away_market_data:
                                                diff =  abs(away_pan[0]-send_pan[0])
                                                if diff<min_diff:
                                                    select_pan = away_pan
                                                    min_diff = diff
                                        else:
                                            zp_rate[0] = False
                                        #追客队
                                    if select_pan is not None:
                                        if select_pan[0]>=0 or (select_pan[0]>=-0.25 and minute<=75) or (select_pan[0]>=-0.5 and minute<=70) and total>0:
                                            t = f'{select_type}_{select_pan[0]}|{select_pan[1]}'
                                            money_data[1] = total-1
                                            #延时推送
                                            submit_delayed_task(90,g_send_pan,args=(host_goal,away_goal,minute,select_pan,t,k,money,game_data,dec))
                            pre_goal_data = goal_time[k][0].split("-")
                            p_host_goal = int(pre_goal_data[0])
                            p_away_goal = int(pre_goal_data[1])
                            now_goal_data = goal_.split("-")
                            n_host_goal = int(now_goal_data[0])
                            n_away_goal = int(now_goal_data[1])
                            goal_team = None
                            if n_host_goal != p_host_goal:
                                goal_team = 'Home'
                            if n_away_goal !=p_away_goal:
                                goal_team = 'Away'
                            goal_time[k] = [goal_,datetime.datetime.now(),goal_team]#存放进球球队
                        #判断上次比分改变时间
                        n = datetime.datetime.now()
                        diff_time = (n - goal_time[k][1]).total_seconds()
                        if diff_time<60:
                            continue
                        host_target = int(game_data['host_target'])
                        host_off = int(game_data['host_off'])
                        host_danger = int(game_data['host_danger'])
                        away_target = int(game_data['away_target'])
                        away_off = int(game_data['away_off'])
                        away_danger = int(game_data['away_danger'])
                        cs_data = [minute,host_goal,away_goal,host_target,host_off,host_danger,away_target,away_off,away_danger]
                        for i_ in range(0,len(host_market_data)):
                            hostpan = host_market_data[i_]
                            awaypan = away_market_data[i_]
                            append_data = [hostpan[0],hostpan[1],awaypan[0],awaypan[1]]
                            predict_data = cs_data+append_data
                          #  print(predict_data)
                            result = self.predict(predict_data)
                            print([0.95],result)
                            if result is not None and result.get('yll') is not None:
                                #这里进行推送 保存dec
                                yll = result['yll']
                                dec = result['dec']
                                if dec not in ('0.799','0.251','0.351',"0.159"):
                                    continue
                                if k not in self.dec_dict:
                                    self.dec_dict[k] = set()
                                if dec not in self.dec_dict[k]:
                                    self.dec_dict[k].add(dec)
                                    #这里进行推送
                                    zp_rate = yll[2]
                                    money = yll[3]
                                    if yll[0]>=0.05:
                                        send_pan = hostpan
                                        t = f'Home_{send_pan[0]}|{send_pan[1]}'
                                        if k not in self.zp_dict:
                                            self.zp_dict[k] = []
                                        self.zp_dict[k].append([t, send_pan, dec, [2, 2], [True]])
                                    else:
                                        send_pan = awaypan
                                        t = f'Away_{send_pan[0]}|{send_pan[1]}'
                                        if k not in self.zp_dict:
                                            self.zp_dict[k] = []
                                        self.zp_dict[k].append([t, send_pan, dec, [2, 2], [True]])
                                    #这里需要进行判断 因为比赛刚开始阶段
                                    self.send_pan(host_goal,away_goal,minute,send_pan,t,k,money,game_data,dec)
                                else:
                                    continue
                    except Exception as e:
                       # print('error',e)
                        pass
                       # print(e)
            time.sleep(5)


ws_mange.start_account_listen()
auto_push_thread_by_target_off().start()
