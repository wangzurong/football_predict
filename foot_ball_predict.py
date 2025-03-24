import math
import time
from collections import OrderedDict

import oper
import func
# 落后 平局 领先 0  1 2 #浅盘 深盘 0 1  #时间 0 1 2 3 4 5 # 主客 0 1

def detect_penalty_event(latest_odds, odds_history, threshold=0.5):
    """
    判断当前盘口与之前盘口差异是否过大，检测是否可能有点球事件。

    :param latest_odds: 当前盘口值 (float)
    :param odds_history: 保存的盘口历史 (deque)
    :param threshold: 差异阈值 (float)，超过该值认定为点球事件
    :return: 是否可能有点球事件 (bool)
    """
    if not odds_history:
        # 如果没有历史盘口，无法判断
        return False

    # 计算盘口的历史均值
    historical_mean = sum(odds_history) / len(odds_history)

    # 计算当前盘口与历史均值的差异
    difference = abs(latest_odds - historical_mean)
    # 如果差异超过阈值，认为可能有点球事件
    if difference >= threshold:
        return True
    return False
class LimitedSizeDict:
    def __init__(self, max_size):
        self.max_size = max_size
        self.data = OrderedDict()

    def __setitem__(self, key, value):
        if key in self.data:
            self.data.move_to_end(key)  # 移动到最后，表示最近使用
        self.data[key] = value
        if len(self.data) > self.max_size:
            self.data.popitem(last=False)  # 删除最旧的项目
    def get(self, key, default=None):
        return self.data.get(key, default)  # assuming self.data is a dict
    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __repr__(self):
        return repr(self.data)
all_matches_data = LimitedSizeDict(1)

def detect_penalty_event(latest_odds, odds_history, threshold=0.5):
    """
    判断当前盘口与之前盘口差异是否过大，检测是否可能有点球事件。
    """
    if not odds_history:
        return False

    # 计算盘口历史均值
    historical_mean = sum(odds_history) / len(odds_history)

    # 计算当前盘口与历史均值的差异
    difference = abs(latest_odds - historical_mean)
    return difference >= threshold


def update_time_series(match_id, game_time, match_data, current_score,handicap):
    
    if match_id not in all_matches_data:
        all_matches_data[match_id] = {
            "home": {
                "attack_right": [],
                "attack_fail": [],
                "attack_danger": [],
                "corners": [],
            },
            "away": {
                "attack_right": [],
                "attack_fail": [],
                "attack_danger": [],
                "corners": [],
            },
            "previous_home_data": {  # 记录上次比分变化时的主队累计数据
                "attack_right": 0,
                "attack_fail": 0,
                "attack_danger": 0,
                "corners": 0,
            },
            "previous_away_data": {  # 记录上次比分变化时的客队累计数据
                "attack_right": 0,
                "attack_fail": 0,
                "attack_danger": 0,
                "corners": 0,
            },
            "pans": [],
            "time": [],
            "current_score": None,  # 记录当前比分,
            'current_pan':None
        }

    match_data_store = all_matches_data[match_id]

    # 检查比分是否变化
    if match_data_store["current_score"] != current_score:
        # 如果比分发生变化，更新 previous 数据为当前累计数据
        match_data_store["previous_home_data"] = {
            "attack_right": int(match_data["h_attack_right"]),
            "attack_fail": int(match_data["h_attack_fail"]),
            "attack_danger": int(match_data["h_attack_danger"]),
            "corners": int(match_data["h_corners"]),
        }
        match_data_store["previous_away_data"] = {
            "attack_right": int(match_data["a_attack_right"]),
            "attack_fail": int(match_data["a_attack_fail"]),
            "attack_danger": int(match_data["a_attack_danger"]),
            "corners": int(match_data["a_corners"]),

        }
        match_data_store['current_pan'] = [handicap, game_time]
        match_data_store["current_score"] = current_score  # 更新当前比分
    if match_data_store['current_pan'] is None or match_data_store['current_pan'][0]!=handicap:
        #记录盘口变化时间
        match_data_store['current_pan'] = [handicap,game_time]
        '''

        match_data_store["previous_home_data"] = {
            "attack_right": int(match_data["h_attack_right"]),
            "attack_fail": int(match_data["h_attack_fail"]),
            "attack_danger": int(match_data["h_attack_danger"]),
            "corners": int(match_data["h_corners"]),
        }
        match_data_store["previous_away_data"] = {
            "attack_right": int(match_data["a_attack_right"]),
            "attack_fail": int(match_data["a_attack_fail"]),
            "attack_danger": int(match_data["a_attack_danger"]),
            "corners": int(match_data["a_corners"]),

        }
        '''
    # 如果当前时间的数据已存储，则跳过
    if game_time in match_data_store["time"]:
        return

    # 存储当前时间的数据
    match_data_store["time"].append(game_time)
    match_data_store["pans"].append(float(match_data["h_pan"]))

    for key in ["attack_right", "attack_fail", "attack_danger", "corners"]:
        match_data_store["home"][key].append(int(match_data[f"h_{key}"]))
        match_data_store["away"][key].append(int(match_data[f"a_{key}"]))

    # 只保留最近 10 分钟的数据
    while len(match_data_store["time"]) > 10:
        match_data_store["time"].pop(0)
        match_data_store["pans"].pop(0)
        for key in ["attack_right", "attack_fail", "attack_danger", "corners"]:
            match_data_store["home"][key].pop(0)
            match_data_store["away"][key].pop(0)


# 修改后的 calculate_real_handicap 函数
def calculate_real_handicap(initial_handicap, current_handicap, home_data, away_data, now_time, pre_pan, hc, ac,
                            weights=None):
    联系作者 qq 2824498290 wx zuonwang
    return 联系作者 qq 2824498290 wx zuonwang

# 修改后的 bet_value 函数
def bet_value(match,weights):
    try:
        # 提取比赛数据
        matchid = match['id']

        current_home_goals = int(match['h_score'])
        current_away_goals = int(match['a_score'])
     #   save_match_score(matchid, current_home_goals, current_away_goals)
        current_score = f"{current_home_goals}_{current_away_goals}"  # 当前比分

        # 获取累计数据


        current_handicap = float(match["h_pan"])

        update_time_series(matchid, int(match['game_time']), match, current_score,current_handicap)
        match_data_store = all_matches_data.get(matchid, {})
        previous_home_data = 联系作者 qq 2824498290 wx zuonwang
        previous_away_data = 联系作者 qq 2824498290 wx zuonwang
        # 当前比赛数据
        home_data = 联系作者 qq 2824498290 wx zuonwang
        away_data = 联系作者 qq 2824498290 wx zuonwang

        # 获取初盘
        initial_handicap = match['cp']

        if initial_handicap is None:
          #  print(f"未能获取初盘，跳过比赛 {matchid}")
            return None

        # 获取当前盘口

  #      print(f"比赛 {matchid} 的初盘: {initial_handicap}, 当前盘口: {current_handicap}")
  #      print(f"比赛 {matchid} 的初盘: {initial_handicap}, 当前盘口: {current_handicap}")

        # 更新时间序列，并检测比分变化

        # 调用计算真实盘口的函数
        hostname, awayname = match['game_name'].split(" v ")
        #这里获取之前盘口
        pre_pan = all_matches_data.get(matchid)
        if pre_pan is not None:
            pre_pan = all_matches_data[matchid].get('current_pan')
       # pans_history = match_data_store.get("pans", [])
        real_handicap = calculate_real_handicap(initial_handicap, current_handicap, home_data, away_data,int(match['game_time']),pre_pan,current_home_goals,current_away_goals,weights=weights)
        insert_data = f'{round(current_handicap, 2)}_{round(real_handicap, 2)}_{current_home_goals}_{current_away_goals}'
      #  save_match_data(matchid, current_home_goals, current_away_goals, hostname, awayname, match['lea_name'],
     #                   int(match['game_time']), insert_data)
      #  print(f"初盘: {initial_handicap}, 当前盘口: {current_handicap}, 计算出的真实盘口: {real_handicap}")
        #这里盘口盘口差
        pan_cha = current_handicap-real_handicap
        if match['h_red']!=0 or match['a_red']!=0:
            return None
        if matchid in all_matches_data:
            if detect_penalty_event(current_handicap,all_matches_data[matchid]['pans']):
             #   print("penalty")
                return None
     

        yz = 联系作者 qq 2824498290 wx zuonwang
        jg = 联系作者 qq 2824498290 wx zuonwang
        if pan_cha > 0:
            if initial_handicap != 0 and current_handicap == 0:
                return None
            if current_home_goals<current_away_goals:
                yz = max(0.05,yz - 0.05)

            # 落后 平局 领先 0  1 2 #浅盘 深盘 0 1  #时间 0 1 2 3 4 5 # 主客 0 1

            if current_home_goals>current_away_goals:
                p1 = 2
            elif current_home_goals==current_away_goals:
                p1 = 1
            else:
                p1 = 0
            if abs(current_handicap) <=0.5:
                p2 = 0
            else:
                p2 = 1
            p3 =  int(match['game_time'])//15
            p4 = 0
            p_id = f'{p1}_{p2}_{p3}_{p4}'
            yl = [(abs(pan_cha) - yz) // jg* 0.1 + 0.1, 0,p_id]
        else:
            if initial_handicap != 0 and current_handicap == 0:
                return None
            if current_home_goals>current_away_goals:
                yz = max(0.05,yz - 0.05)

            # if abs(pan_cha)<
            if current_home_goals > current_away_goals:
                p1 = 0
            elif current_home_goals == current_away_goals:
                p1 = 1
            else:
                p1 = 2
            if abs(current_handicap) <= 0.5:
                p2 = 0
            else:
                p2 = 1
            p3 = int(match['game_time']) // 15
            p4 = 1
            p_id = f'{p1}_{p2}_{p3}_{p4}'

            yl = [0, (abs(pan_cha) - yz) // jg* 0.1 + 0.1,p_id]
        return yl
    except Exception as e:
     #   print(f"Error processing match: {e}")
        return None

def cal_match(match,w):
    try:
        return bet_value(match,w)
    except Exception as e:
     #   print(f"Error in cal_match: {e}")
        return None
