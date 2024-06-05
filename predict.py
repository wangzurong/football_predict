import json
import pickle
two_four_Home_set = ('0.32', '0.353', '0.098', '0.642', '0.964', '0.421', '0.294', '0.167', '0.746', '0.492', '0.174', '0.463', '0.048', '0.181', '0.024', '0.252', '0.83', '0.063')
two_four_Away_set=  ('0.802', '0.547', '0.356', '0.997', '0.678', '0.231', '0.425', '0.202', '0.298', '0.650', '0.109', '0.812', '0.216', '0.542')
four_eight_Home_set = ('0.387', '0.132', '0.936', '0.33', '0.666', '0.443', '0.253', '0.958', '0.223')
four_eight_Away_set = ('0.8')

with open('kmeans_model.pkl', 'rb') as file:
    kmeans = pickle.load(file)
with open('two_four_kmeans_Home.pkl', 'rb') as file:
    two_four_Home_kmeans = pickle.load(file)
with open("two_four_scaler_Home.pkl",'rb') as file:
    two_four_Home_scaler = pickle.load(file)
with open('two_four_kmeans_Away.pkl', 'rb') as file:
    two_four_Away_kmeans = pickle.load(file)
with open("two_four_scaler_Away.pkl",'rb') as file:
    two_four_Away_scaler = pickle.load(file)
with open('four_eight_kmeans_Home.pkl', 'rb') as file:
    four_eight_Home_kmeans = pickle.load(file)
with open("four_eight_scaler_Home.pkl",'rb') as file:
    four_eight_Home_scaler = pickle.load(file)
with open('four_eight_kmeans_Away.pkl', 'rb') as file:
    four_eight_Away_kmeans = pickle.load(file)
with open("four_eight_scaler_Away.pkl",'rb') as file:
    four_eight_Away_scaler = pickle.load(file)
start = 0
end = 0
print('load kemeas success')
with open('scaler.pkl', 'rb') as f:
    loaded_scaler = pickle.load(f)
yll_json = None
with open('./yll.txt',mode='r',encoding='utf-8') as f:
    yll_json = json.loads(f.read())
two_four_home_json = None
with open('./two_four_Home.txt',mode='r',encoding='utf-8') as f:
    two_four_home_json = json.loads(f.read())
with open('./two_four_Away.txt',mode='r',encoding='utf-8') as f:
    two_four_away_json = json.loads(f.read())
with open('./four_eight_Home.txt',mode='r',encoding='utf-8') as f:
    four_eight_home_json = json.loads(f.read())
with open('./four_eight_Away.txt', mode='r', encoding='utf-8') as f:
    four_eight_away_json = json.loads(f.read())
def predict_yll(minute,now_host_goal,now_away_goal,host_target,host_off,host_danger,away_target,away_off,away_danger,host_pan,host_odd,away_pan,away_odd):
    try:
        host_pro = round((host_target / (host_target + away_target) + (host_target + host_off) / (
                host_target + host_off + away_target + away_off) + (
                                  host_target + host_off + host_danger) / (
                                  host_target + host_off + away_target + away_off + host_danger + away_danger)) / 3,
                         2)
        away_pro = round((away_target / (host_target + away_target) + (away_off + away_target) / (
                host_target + host_off + away_target + away_off) + (
                                  away_target + away_off + away_danger) / (
                                  host_target + host_off + away_target + away_off + host_danger + away_danger)) / 3,
                         2)
        #当前局势
        js = 0
        if now_host_goal - now_away_goal > 0:
            js = 1
        elif now_host_goal - now_away_goal == 0:
            js = 0
        elif now_host_goal - now_away_goal < 0:
            js = -1
        if host_pan < -3 or host_odd > 3 or away_pan < -3 or away_odd > 3:
            return None
        if host_odd < 1.6 or host_odd > 2.5 or away_odd < 1.6 or away_odd > 2.5:
            return None
        n_host_odd = int((host_odd - 1) * 100)
        n_away_odd = int((away_odd - 1) * 100)
        n_host_pan = int(host_pan / 0.25)
        n_away_pan = int(away_pan / 0.25)
        diff_sl = int(round(host_pro - away_pro, 2) * 100)
        fit_data = [[minute, js, n_host_pan, n_host_odd, n_away_pan, n_away_odd, diff_sl]]
        fit_data = loaded_scaler.transform(fit_data)
        print(fit_data)
        new_match_cluster = kmeans.predict(fit_data)
        dec = str(round(new_match_cluster[0] / 1000, 3))
        return [yll_json.get(dec),dec]
    except Exception as e:
        print(e)
        print('predict error')
        return None






