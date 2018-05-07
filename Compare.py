import csv
import datetime
import cfg
from Deviations import calc_dev
import os
from Plot import plot_all
from ba import ba_run
from bp import bp_run


# ? Returns only times that are between start and end in lst ? #
def cut_lst(lst, start, end, source='start'):
    i = 0
    res = []
    start, end = to_datetime(start), to_datetime(end)
    if source == 'stamp':
        start = end - datetime.timedelta(0, cfg.plt_len)
    while i < len(lst) and lst[i][0] <= start:
        i += 1
    while i < len(lst) and lst[i][0] < end:
        res.append(lst[i])
        i += 1
    return res


def import_cu_ibi():
    for i in cfg.dic_names_time:
        dbl_lst = cut_lst(cfg.data['CUBX']['IBI'], cfg.starts[i], cfg.ends[i])
        cfg.ibi['CUBX'][cfg.dic_names_time[i]] = [val[1] for val in dbl_lst]
        if not os.path.isdir(cfg.CU_RR_PATH[:-1]):
            os.makedirs(cfg.CU_RR_PATH[:-1])
        with open(cfg.CU_RR_PATH + cfg.dic_names_time[i] + '.csv', 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(cfg.ibi['CUBX'][cfg.dic_names_time[i]])
    return


def to_datetime(ts):
    return datetime.datetime(int(ts[0:4]), int(ts[5:7]), int(ts[8:10]), int(ts[11:13]), int(ts[14:16]), int(ts[17:19]))


# ? Returns a list of Stamper events after ? #
# ? timestamp was changed to an index, relative to end ? #
def stp_ts_to_idx(stp, end):
    lst = []
    end = to_datetime(end)
    start = end - datetime.timedelta(0, cfg.plt_len)
    for event in stp:
        e = to_datetime(event[0])
        if start < e < end:
            lst.append([(e-start).seconds, event[1]])
    return lst


def bok_csv(lsts={}, param='', name='', blandaltman=False):
    csv_lst = []
    columns = ['index']
    if blandaltman:
        path = cfg.PATH + 'BlandAltman/' + param
    else:
        path = cfg.PATH + param
    for device in lsts:
        if len(lsts[device]) != 0:
            delta = len(lsts['CUBX']) - len(lsts[device])
            if len(lsts[device]) < len(lsts['CUBX']):
                lsts[device] += [[lsts['CUBX'][-x][0], 0] for x in range(delta)]
            columns.append(device)
    for i in range(len(lsts['CUBX'])):
        csv_lst.append([lsts['CUBX'][i][0]] + [lsts[lst][i][1] for lst in lsts])
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(path + '/' + name + '.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(csv_lst)
    return


def show_plot(plot):
    for param in plot:
        print param
        for record in plot[param]:
            print record
            print 'Stamper: ' + str([a[0]+', '+a[1][:-1] for a in plot[param][record]['stamp']])
            for device in plot[param][record]['lines']:
                print device
                print plot[param][record]['lines'][device]
                if device != 'CUBX':
                    print plot[param][record]['annots'][device]
    return


def create_ba_csv(plot, per_subject):
    for param in plot:
        if param in cfg.ba_param:
            for subject in per_subject[param]:
                bok_csv(per_subject[param][subject]['lines'], param, subject, True)
