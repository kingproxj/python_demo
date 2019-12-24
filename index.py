# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import time
from datetime import datetime
import os
# from utils.log import init_log, logger
import joblib
import re

DataClean_FOLDER = './model_file/loan/'
MODEL_FOLDER = './model_pkl/loan/'

startTime = time.time()
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

data_train = pd.read_pickle(DataClean_FOLDER + 'train_x.pkl')

dump_raw_etc = joblib.load(MODEL_FOLDER + 'dump_raw_etc.pkl')
dump_raw_gbc = joblib.load(MODEL_FOLDER + 'dump_raw_gbc.pkl')
dump_raw_xgb = joblib.load(MODEL_FOLDER + 'dump_raw_xgb.pkl')


def get_date(x):
    if pd.isnull(x):
        return np.nan
    elif x not in ['null', '']:
        time_num = int(x)
        time_local = time.localtime(float(time_num/1000))

        dt = time.strftime("%Y-%m-%d", time_local)
        return dt
    else:
        return np.nan

def join_all(ent_proc_dir, entname):
    """
    链接所有数据
    :return:
    """
    files = os.listdir(ent_proc_dir)
    # logger.info('文件数量 -- %d\n\t\t%s' % (len(files), '\n\t\t'.join(files)))

    all_data: pd.DataFrame = None
    for file in files[:]:
        if file == 'jinan_good_bad_data_all.csv':
            continue
        if file == 'jinan_good_bad_data_all.pkl':
            continue
        if file == 'test_x.pkl':
            continue
        if file == 'train_x.pkl':
            continue
        data = pd.read_csv(ent_proc_dir + file, encoding='gbk')

        if all_data is None:
            all_data = data
        else:

            # 去除重复的列名
            a = all_data.columns.tolist()
            b = data.columns.tolist()
            cols_in_use = list(set(b).difference(set(a)))
            if cols_in_use is None:
                cols_in_use = ['entname']

            if 'entname' not in cols_in_use:
                cols_in_use.append('entname')

            data = data[cols_in_use]

            data['entname'] = entname
            all_data['entname'] = entname
            # print(all_data.columns.tolist())
            # print(data.columns.tolist())
            all_data = pd.merge(all_data, data,  on='entname', how='inner')

    all_data = all_data.dropna(axis=0, subset=['entname'])

    def sub_time(row):

        accondate = row['accondate']
        if not pd.isnull(accondate) and not isinstance(accondate, float):
            accondate = datetime.strptime(row['accondate'], "%Y-%m-%d")

        opfrom = row['opfrom']
        opfrom_year = None
        if not pd.isnull(opfrom) and not isinstance(opfrom, float):
            opfrom_year = opfrom[0:4]

        estdate = row['estdate']
        if not pd.isnull(estdate) and not isinstance(estdate, float):
            estdate = datetime.strptime(row['estdate'], "%Y-%m-%d")

        day = None
        if not pd.isnull(accondate) \
                and not pd.isnull(estdate) \
                and not isinstance(accondate, float) \
                and not isinstance(estdate, float):
            day = (accondate - estdate).days

        return pd.Series([
            opfrom_year,
            row['estdate'],
            day
        ],
            index=['opfrom', 'estdate', 'accondate'])

    all_data[['opfrom', 'estdate', 'accondate']] = all_data[['opfrom', 'estdate', 'accondate']].apply(sub_time, axis=1)

    # print(all_data[['opfrom', 'estdate', 'accondate']])

    all_data.drop(['subcondate'], axis=1, inplace=True)

    all_data.to_csv(ent_proc_dir + 'jinan_good_bad_data_all.csv', encoding="gbk", index=False)

    return all_data


def proc_allow_func(data):

    # 数据预处理 及 准入

    # accondate字段处理为绝对值，并增加字段is_date_neg标记是否为负数
    data['is_date_neg'] = data['accondate'].apply(lambda x: 1 if x and x < 0 else 0)
    data['accondate'] = data['accondate'].apply(lambda x: abs(x) if x and str(x) else np.nan)

    # 雇员人数异常值检测
    # 高中雇员人数>总雇员人数，高中雇员人数处理为空
    # print(data)
    data['colemplnum'] = data[['empnum', 'colemplnum']].apply(lambda x: np.nan if x['colemplnum'] and x['empnum'] and x['colemplnum'] > x['empnum'] else x, axis=1)

    # 判断数据是否准入

    data['is_geti'] = 0

    # 如果基础信息不存在，则不此项在数据传入时判断准入
    #

    # 判断企业状态
    entstatus = re.search(r'营业|开业|存续|在营|在册|登记|正常|1', str(data['entstatus']))
    if entstatus:
        pass
    else:
        return data, {'stat': 5000, 'msg': '请求失败！',
                      'allow': {'code': 5000, 'msg': '企业不符合准入，企业状态异常！'}
                      }

    # # 判断企业类型，分公司不具备银行贷款资质
    # enttype = re.search(r'分公司|非法人', str(data['enttype']))
    # if enttype:
    #     return data, {'stat': 2000, 'msg': '请求成功！',
    #      'allow': {'code': 5000, 'msg': '企业不符合准入，分公司或非法人不具备银行贷款资质！'}
    #      }

    # 注册资本信息是否存在
    data['regcap'] = data['regcap'].fillna('null')
    data_allow = data[data['regcap'].isin(['null'])]
    if data_allow.shape[0]:
        return data, {'stat': 5000, 'msg': '请求失败！',
                      'allow': {'code': 5000, 'msg': '企业不符合准入，注册资本信息不完整！'}
                      }

    # 数据存在单位异常，不符合小微企业筛选条件
    col_list = ['regcap', 'max_to_num', 'min_to_num', 'liacconam', 'lisubconam']
    for c in col_list:
        # 对应的是万单位， 标记数值大于1000 < 10000的数据并删除
        data['ab_delete'] = data[c].apply(lambda x: 1 if 1000 < x <= 10000 else 0)
        data['unit_convert_'+c] = data[c].apply(lambda x: x/10000 if x>10000 else x)
        # 对应的是万元单位, 删除x>1000的数据
        data['unit_delete'] = data['unit_convert_'+c].apply(lambda x: 1 if 1000<x else 0)
        # delete samples
        data['ab_delete'] = data['ab_delete'].apply(lambda x: 'null' if x==1 else x)
        data_delete = data[data['ab_delete'].isin(['null'])]
        data['unit_delete'] = data['unit_delete'].apply(lambda x: 'null' if x==1 else x)
        data_unit_delete = data[data['unit_delete'].isin(['null'])]

        # 删除一遍创造特征
        data = data.drop(c, axis=1)

        # 去除小微企业单位异常筛选
        # if data_delete.shape[0] or data_unit_delete.shape[0]:
        #     return data, {'stat': 2000, 'msg': '请求成功！',
        #         'allow': {'code': 5000, 'msg': '企业不符合准入，数据存在单位异常，不符合小微企业筛选条件!'}
        #         }

    # 判断注册资本< 1000万，从业人数小于10
    # 不满足小微企业条件
    data_allow = data[(data['unit_convert_regcap'] <= 50000) & (data['empnum'] <= 10000)]
    if data_allow.shape[0] == 0:
        return data, {'stat': 5000, 'msg': '请求失败！',
                      'allow': {'code': 5000, 'msg': '企业不符合准入，注册资本或从业人数不符合小微企业筛选条件！'}
                      }

    return data, None


def keep_and_norml(data):

    data.drop(['industryphy', 'dom', 'time'], axis=1, inplace=True)
    data.drop(['entname', 'apprdate', 'estdate', 'sum_to_num', 'opfrom', 'entstatus', 'enttype'], axis=1, inplace=True)

    data = data.drop(['type_alt', 'time_alt', 'is_shizhong_area', 'is_ts_indus',
                      'is_tianqiao_area','name_alt', 'is_manu_indus', 'is_lixia_area', 'is_shanghe_area',
                      'is_pingyin_area', 'is_jiyang_area',
                      'is_sw_indus', 'inv_alt','is_licheng_area', 'bus_alt', 'is_nlmy_indus',
                      'is_food_indus', 'share_alt', 'is_ps_indus'], axis=1)
    data = data.drop(['ab_delete', 'unit_delete'], axis=1)

    list_ = data.columns.tolist()
    list_.sort(reverse=True)

    # 数值变量标准化
    col_list = ['alt_count', 'empnum', 'inv_count', 'min_share', 'max_share',
                'accondate', 'subcount','subcount', 'colemplnum',
                'so310', 'so210', 'so510', 'so110', 'so410',
                'unit_convert_regcap', 'unit_convert_max_to_num', 'unit_convert_min_to_num',
                'unit_convert_liacconam', 'unit_convert_lisubconam']

    # 读取测试集数据 训练测试集总体样本
    data_test = pd.read_pickle(DataClean_FOLDER + 'test_x.pkl')

    data_test = data_test.append(data_train, ignore_index=True)
    #data_test = data_test.append(data, ignore_index=True)

    for c in col_list:
        min = data_test[c].min()
        max = data_test[c].max()
        data_test[c] = data_test[c].apply(lambda x: (x-min)/(max-min))

    data = data_test.iloc[-1:]
    # print('单一', data.shape)
    return data


def model_predict(data):

    data = data.fillna(-999)

    col_list = ['alt_count', 'gs_alt', 'is_ent_indus', 'is_zhangqiu_area', 'is_traf_indus', 'is_geti', 'is_finance_indus', 'is_retail_indus', 'is_huaiyin_area', 'is_cons_indus', 'is_bldg_indus', 'is_bs_indus', 'is_gaoxin_area', 'is_power_indus', 'is_os_indus', 'empnum', 'inv_count', 'min_share', 'max_share', 'accondate', 'subcount', 'colemplnum', 'so310', 'so210', 'so510', 'so110', 'so410', 'is_date_neg', 'unit_convert_regcap', 'unit_convert_max_to_num', 'unit_convert_min_to_num', 'unit_convert_liacconam', 'unit_convert_lisubconam']
    data = data[col_list]
    score_list = []

    # 0 概率 1 概率 模型预测
    score_df = pd.DataFrame(columns=['etc', 'gbc', 'xgb'],index=[0])

    result_etc = dump_raw_etc.predict_proba(data)   # 0 概率 1 概率 取第二个
    # print(result_etc)
    score_df['etc'] = result_etc[0][1]
    score_list.append(list(result_etc[0]))

    result_gbc = dump_raw_gbc.predict_proba(data)
    # print(result_gbc)
    score_df['gbc'] = result_gbc[0][1]
    score_list.append(list(result_gbc[0]))

    # data.sort_index(axis=1, inplace=True)

    result_xgb = dump_raw_xgb.predict_proba(data)
    # print(result_xgb)
    score_df['xgb'] = result_xgb[0][1]
    score_list.append(list(result_xgb[0]))

    # print(score_list)
    # score_array = np.mat(score_list)
    # score_array = score_array[:, 1].T
    # print(score_array)
    # # score_array = pd.DataFrame(score_array)
    # # 预测标签好坏
    # Ridge_Blend = joblib.load(MODEL_FOLDER + 'Ridge_Blend.pkl')
    # # data.sort_index(axis=1, inplace=True)
    #
    # result_rb = Ridge_Blend.predict(score_array)
    # print(result_rb)
    # score_df['result'] = result_rb[0]

    score_df['xgb_score'] = score_df['xgb'].apply(
        lambda x: 42.16  if     x<=0.011463
        else 26.60  if 0.011463<x<=0.024835
        else 23.33  if 0.024842<x<=0.048009
        else 9.21  if 0.0481<x<=0.090388
        else 0.41  if 0.090659<x<=0.15708
        else -3.68  if 0.157416<x<=0.304551
        else -13.10  if 0.305313<x<=0.591026
        else -30.70
    )
    score_df['etc_score'] = score_df['etc'].apply(
        lambda x: 12.18  if     x<=0.276036
        else 11.17  if 0.276036<x<=0.338471
        else 11.17  if 0.339242<x<=0.411589
        else 5.90  if 0.411652<x<=0.440614
        else 0.16  if 0.440681<x<=0.506886
        else -2.87  if 0.506937<x<=0.580372
        else -15.36
    )
    score_df['gbc_score'] = score_df['gbc'].apply(
        lambda x: 31.44  if     x<=0.001431
        else 27.22  if 0.001431<x<=0.00496
        else 14.08  if 0.004978<x<=0.014715
        else 8.68  if 0.014738<x<=0.075982
        else -6.33  if 0.076599<x<=0.38126
        else -36.13
    )

    score_df['total_score'] = score_df[['xgb_score', 'etc_score', 'gbc_score']].apply(lambda x: x.sum() + 578, axis=1)

    return score_df['total_score'].values[0]


def calc_main_feature(entname):

    # try:
    print("loading outside csv file of "+entname)
    # 合并文件
    ent_proc_dir = DataClean_FOLDER
    all_data = join_all(ent_proc_dir,entname)
    #all_data = pd.read_csv(outfilename,encoding='gbk')
    # all_data = pd.read_csv(DataClean_FOLDER + 'jinan_good_bad_data_all.csv', encoding='gbk')

    # print(all_data.shape)
    if all_data.shape[0] != 1:
        return {'stat': 5000, 'msg': '数据异常,请反馈！'}

    # 数据预处理 特征工程数据清洗 数据准入判断
    all_data, allow_msg = proc_allow_func(all_data)

    if allow_msg:
        # print(allow_msg)
        return allow_msg

    # 保留重要特征值、标准化
    all_data = keep_and_norml(all_data)

    # 入模预测得出评分
    total_score = model_predict(all_data)

    # print('total_score', total_score)
    return {'stat': 2000, 'msg': '请求成功！',
            'allow': {'code': 2000, 'msg': '该企业符合准入条件！'},
            'result': {'companyname': entname, 'score': int(total_score)}
            }
    # except Exception as e:
    #     return {
    #         "stat": 5000,
    #         'msg': '请求失败！',
    #         'Exception': str(e)
    #     }
    # return total_score


def application(environ, start_response):
    print("==========================")
    print("params is",environ["QUERY_STRING"])
    print("==========================")
    entname = '山东惠硕信息技术有限公司'
    result = calc_main_feature(entname)
    print(result)
    responsebody = str(result)
    start_response('200 OK', [('Content-Type','application/json')])
    return [bytes(responsebody, encoding = "utf8")]
