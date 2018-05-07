import tkFileDialog
import tkMessageBox
from shutil import copyfile
from Tkinter import *
from tkColorChooser import askcolor
from AggregateZeph import sorted_sum_files, unite_summaries
from ttk import Separator
import Imports
from Times import retrieve_times
import cfg
import os

root = Tk()
root.iconbitmap(default='logo.ico')
root.title('Compariuse')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| Functions |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# ? Creates count lbl from cfg.times length ? #
def gen_count():
    lbl_num_count = Label(root, text=str(len(cfg.times)))
    lbl_num_count.grid(row=11, column=1, sticky=W, padx=5)
    return


# ? Populates cfg.times with ['start timestamp-end timestamp'] elements from cu report ? #
# ? Adds times from cfg.times to the listbox                                           ? #
# ? Creates name enter lbl, entry and button                                           ? #
# ? Creates cfg.dic_names_time dictionary with {timestamp.id: timestamp}               ? #
def gen_times():
    cfg.times = retrieve_times()
    for item in cfg.times:
        lst_times.insert(END, item)
    lst_times.grid(row=12, column=0, sticky=W, rowspan=5, columnspan=1)
    Label(root, text='Name this record: ').grid(row=12, column=1, sticky=E, columnspan=1)
    Label(root, text='Start: ').grid(row=13, column=1, sticky=E, columnspan=1)
    Label(root, text='End:').grid(row=14, column=1, sticky=E, columnspan=1)
    entry_start.grid(row=13, column=2, sticky=W, columnspan=1)
    entry_end.grid(row=14, column=2, sticky=W, columnspan=1)
    entry_name.grid(row=12, column=2, sticky=W, columnspan=1)
    for i, time in enumerate(cfg.times):
        cfg.dic_names_time[i] = time[0:4] + time[5:7] + time[8:10] + time[11:13] + time[14:16] + time[17:19]
    Button(root, text='Submit Name', command=submit_name).grid(row=15, column=1, sticky=E, columnspan=1)
    Button(root, text='Submit List', command=submit_list).grid(row=15, column=2, sticky=W, columnspan=1)
    Button(root, text='Update', command=update_times).grid(row=16, column=1, sticky=E, columnspan=1)
    Button(root, text='Delete', command=delete_rec).grid(row=16, column=2, sticky=W, columnspan=1)
    separate_times_lst()
    root.bind("<<ListboxSelect>>", update_entries)
    lst_times.selection_set(0)
    update_entries()
    return


# ? Splits cfg.times to cfg.starts and cfg.ends ? #
def separate_times_lst():
    cfg.ends, cfg.starts = [], []
    for time in cfg.times:
        cfg.starts.append(time[0:19])
        cfg.ends.append(time[22:41])
    return


def delete_rec():
    if (lst_times.curselection()) == ():
        tkMessageBox.showinfo("Error", "Select a record to delete")
    else:
        curr = lst_times.curselection()[0]
        cfg.dic_names_time.pop(lst_times.curselection()[0])
        lst_times.delete(curr, curr)
        lst_times.insert(curr, ' ')


# ? Changes cfg.dic_names_time in the listbox's current selection as key, ? #
# ? entry as value if not none                                            ? #
def submit_name():
    if entry_name.get() == '':
        tkMessageBox.showinfo("Error", "Enter a name")
    elif (lst_times.curselection()) == ():
        tkMessageBox.showinfo("Error", "Select a time")
    else:
        cfg.dic_names_time[int(lst_times.curselection()[0])] = entry_name.get().capitalize()
        curr = int(lst_times.curselection()[0])
        start = '   (' + lst_times.get(curr).split(' - ')[0][5:] + ')'
        lst_times.delete(curr, curr)
        lst_times.insert(curr, entry_name.get().capitalize()+start)
    entry_name.delete(0, 'end')
    return


def submit_list():
    if entry_name.get() == '':
        update_entries()
        #tkMessageBox.showinfo("Error", "Enter a list of names separated by commas")
    else:
        lst = entry_name.get().split(",")
        if len(lst) != len(cfg.dic_names_time):
            tkMessageBox.showinfo("Error", "Please enter a list of " + str(len(cfg.dic_names_time)) + " names. Entered " + str(len(lst)))
        else:
            for i in range(len(cfg.dic_names_time)):
                cfg.dic_names_time[i] = lst[i].capitalize()
                start = '   (' + lst_times.get(i).split(' - ')[0][5:] + ')'
                lst_times.delete(i, i)
                lst_times.insert(i, lst[i].capitalize()+start)
    entry_name.delete(0, 'end')
    return


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| CSV Browsers |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def update_entries(event=None):
    cfg.CURR_LST_SELECT = 0
    if len(lst_times.curselection()) > 0:
        cfg.CURR_LST_SELECT = int(lst_times.curselection()[0])
    curr_start.set(cfg.starts[cfg.CURR_LST_SELECT])
    curr_end.set(cfg.ends[cfg.CURR_LST_SELECT])
    curr_name.set(cfg.dic_names_time[cfg.CURR_LST_SELECT])


def update_times():
    curr = cfg.CURR_LST_SELECT
    cfg.starts[curr] = entry_start.get()
    cfg.ends[curr] = entry_end.get()
    print cfg.dic_names_time[curr]


def browse_cu_csv():
    if min_len_ent.get() != str(cfg.MIN_REC_LEN):
        cfg.MIN_REC_LEN = int(min_len_ent.get())
    cfg.cu_csv_file = tkFileDialog.askopenfile(parent=root, mode='rb', title='Continuse Biometrics Report')
    if cfg.cu_csv_file is not None:
        gen_times()
        but_cu_browse.config(background='green')
        copyfile(cfg.cu_csv_file.name, 'Results/' + cfg.cu_csv_file.name.split('/')[-1])


def browse_zephyr_rri():
    rr_path = tkFileDialog.askdirectory(parent=root, initialdir="/", title='Zephyr IBI')
    if rr_path != '':
        cfg.RR_PATH = rr_path + '/'


def browse_zephyr():
    zep_path = tkFileDialog.askdirectory(parent=root, initialdir="/", title='Zephyr Imported Folder')
    if zep_path != '':
        cfg.ref_zep = zep_path + '/'
        collect_zep_files(cfg.ref_zep)
        but_zephyr.config(background='green')


def aggregate(src_path=cfg.SUMMARY_PATH, res_path=cfg.AGGREGATE_PATH, head_len=1):
    unite_summaries(sorted_sum_files(src_path), res_path, src_path, head_len)


def collect_zep_files(path):
    print path
    for fo in os.listdir(path):
        print fo
        for fi in os.listdir(path + '/' + fo):
            if '_Summary.Csv' in fi.title():
                if not os.path.isdir(cfg.SUMMARY_PATH):
                    os.makedirs(cfg.SUMMARY_PATH)
                copyfile(path + '/' + fo + '/' + fi, cfg.SUMMARY_PATH + fi.title())
            if '_Rr.Csv' in fi.title():
                if not os.path.isdir(cfg.RR_PATH):
                    os.makedirs(cfg.RR_PATH)
                copyfile(path + '/' + fo + '/' + fi, cfg.RR_PATH + fi.title())
    aggregate()


def browse_capno():
    ref_capno = tkFileDialog.askopenfile(parent=root, mode='rb', title='Oridion Capnograph Report')
    if ref_capno is not None:
        cfg.ref_capno = ref_capno
        but_capno.config(background='green')


def browse_nellcor():
    ref_nellcor = tkFileDialog.askopenfile(parent=root, mode='rb', title='Nellcor PPG Report')
    if ref_nellcor is not None:
        cfg.ref_nellcor = ref_nellcor
        but_nellcor.config(background='green')


def browse_mindray():
    ref_mindray = tkFileDialog.askopenfile(parent=root, mode='rb', title='Mindray Monitor Report')
    if ref_mindray is not None:
        cfg.ref_mindray = ref_mindray
        but_mindray.config(background='green')


def browse_auth_report():
    auth_report = tkFileDialog.askopenfile(parent=root, mode='rb', title='Authentication Report')
    if auth_report is not None:
        cfg.auth_report = auth_report
        but_auth_report.config(background='green')


def browse_bp_report():
    bp_report = tkFileDialog.askopenfile(parent=root, mode='rb', title='BP Report')
    if bp_report is not None:
        cfg.bp_report = bp_report
        but_bp_report.config(background='green')


def browse_bp_trends():
    bp_trends = tkFileDialog.askopenfile(parent=root, mode='rb', title='BP Trends')
    if bp_trends is not None:
        cfg.bp_trends = bp_trends
        but_bp_trends.config(background='green')


def browse_stamper():
    stamper = tkFileDialog.askopenfile(parent=root, mode='rb', title='Stamper')
    if stamper is not None:
        cfg.ref_stamp = stamper
        but_stamper.config(background='green')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| Color setters |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

def zep_col():
    (triple, hexstr) = askcolor()
    if hexstr:
        col_but_zep.config(bg=hexstr)
        cfg.col['Zeph'] = hexstr


def cu_col():
    (triple, hexstr) = askcolor()
    if hexstr:
        col_but_cu.config(bg=hexstr)
        cfg.col['CUBX'] = hexstr


def cap_col():
    (triple, hexstr) = askcolor()
    if hexstr:
        col_but_cap.config(bg=hexstr)
        cfg.col['Cap'] = hexstr


def nel_col():
    (triple, hexstr) = askcolor()
    if hexstr:
        col_but_nellcor.config(bg=hexstr)
        cfg.col['Nel'] = hexstr


def mry_col():
    (triple, hexstr) = askcolor()
    if hexstr:
        col_but_mindray.config(bg=hexstr)
        cfg.col['Mry'] = hexstr


def mryecg_col():
    (triple, hexstr) = askcolor()
    if hexstr:
        col_but_mindrayecg.config(bg=hexstr)
        cfg.col['MryECG'] = hexstr


def build_plot_dic():
    plot = {}
    if is_rr.get() == 1:
        plot['RR'] = {}
    if is_hr.get() == 1:
        plot['HR'] = {}
    if is_sys.get() == 1:
        plot['Sys'] = {}
    if is_dia.get() == 1:
        plot['Dia'] = {}
    return plot


def barun():
    cfg.is_ba = True
    compariuse()


def compariuse():
    Imports.import_ref()
    if plt_len_entry.get() != '':
        cfg.plt_len = int(plt_len_entry.get())
    if success_criteria_entry.get() != str(cfg.success_criteria):
        cfg.success_criteria = int(success_criteria_entry.get())
    if romi_ver_ent.get() != cfg.romi_ver:
        cfg.romi_ver = romi_ver_ent.get()
    if bp_ent_mean_dia.get() != '':
        cfg.bp_mean_dia = float(bp_ent_mean_dia.get())
    if bp_ent_mean_sys.get() != '':
        cfg.bp_mean_sys = float(bp_ent_mean_sys.get())
    if bp_ent_std_sys.get() != '':
        cfg.bp_std_sys = float(bp_ent_std_sys.get())
    if bp_ent_std_dia.get() != '':
        cfg.bp_std_dia = float(bp_ent_std_dia.get())
    if auth_ent_subjects.get() != '':
        cfg.auth_subjects = int(auth_ent_subjects.get())
    if auth_ent_fp.get() != '':
        cfg.auth_fp = float(auth_ent_fp.get())
    if auth_ent_fn.get() != '':
        cfg.auth_fn = float(auth_ent_fn.get())
    if int(rr_pct_ent.get()) != cfg.devs['RR'][0]:
        cfg.devs['RR'][0] = int(rr_pct_ent.get())
    if int(rr_unit_ent.get()) != cfg.devs['RR'][1]:
        cfg.devs['RR'][1] = int(rr_unit_ent.get())
    if int(hr_pct_ent.get()) != cfg.devs['HR'][0]:
        cfg.devs['HR'][0] = int(hr_pct_ent.get())
    if int(hr_unit_ent.get()) != cfg.devs['HR'][1]:
        cfg.devs['HR'][1] = int(hr_unit_ent.get())
    if title_entry.get() != '':
        cfg.title = title_entry.get()
    if sub_title_entry.get() != '':
        cfg.sub_title = sub_title_entry.get()
    if show_annot.get() == 0:
        cfg.show_dev = False
    if count_annot.get() == 0:
        cfg.count_dev = False
    if report_37.get() == 0:
        cfg.report_37 = False
    if show_sum.get() == 0:
        cfg.show_summary = False
    plot = build_plot_dic()
    print('Compariusing...')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| Widgets |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

head_font = "sans-serif 10 bold"

#   -------------------------   Row 0   -------------------------   #
lbl_cu_file = Label(root, text="CUBX Report:", font=head_font)
but_cu_browse = Button(root, text='Browse', command=browse_cu_csv)
col_but_cu = Button(root, text='', command=cu_col, background=cfg.col['CUBX'])
but_stamper = Button(root, text='Stamper', command=browse_stamper)
show_annot = IntVar()
show_dev_check = Checkbutton(root, text='Show deviations on graph', variable=show_annot)
show_dev_check.select()
count_annot = IntVar()
count_dev_check = Checkbutton(root, text='Show number of deviations', variable=count_annot)
count_dev_check.select()
default_success_criteria = StringVar(root, value=str(cfg.success_criteria))
success_criteria_lbl = Label(root, text="Success criteria (% pass per graph):")
success_criteria_entry = Entry(root, textvariable=default_success_criteria)

romi_ver_val = StringVar(root, value=str(cfg.romi_ver))
romi_ver_lbl = Label(root, text="Romi version:")
romi_ver_ent = Entry(root, textvariable=romi_ver_val)

#   -------------------------   Row 1   -------------------------   #
lbl_rec_count = Label(root, text="Records ( >   ")
lbl_rec_countsec = Label(root, text="Seconds):")
min_len_val = StringVar(root, value=str(cfg.MIN_REC_LEN))
min_len_ent = Entry(root, textvariable=min_len_val, width=8, justify=CENTER)

#   -------------------------   Row 2   -------------------------   #

scrollbar = Scrollbar(root, orient=VERTICAL)
lst_times = Listbox(root, width=36, bd=0, yscrollcommand=scrollbar.set)
lst_times.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=lst_times.yview)
curr_start = StringVar(root, value='')
curr_end = StringVar(root, value='')
curr_name = StringVar(root, value='')
entry_name = Entry(root, textvariable=curr_name)
entry_start = Entry(root, textvariable=curr_start)
entry_end = Entry(root, textvariable=curr_end)

#   ------------------------   Row 3-12   ------------------------   #

default_pltlen = StringVar(root, value=str(cfg.plt_len))
plt_len_lbl = Label(root, text="Plot Length:")
plt_len_entry = Entry(root, textvariable=default_pltlen)

lbl_stamper = Label(root, text="Stamper Report:", font=head_font)
lbl_capno = Label(root, text="Capnograph Report:", font=head_font)
but_capno = Button(root, text='Browse', command=browse_capno)
col_but_cap = Button(root, text='', command=cap_col, background=cfg.col['Cap'])

lbl_nellcor = Label(root, text="Nellcor Report:", font=head_font)
but_nellcor = Button(root, text='Browse', command=browse_nellcor)
col_but_nellcor = Button(root, text='', command=nel_col, background=cfg.col['Nel'])


lbl_mindray = Label(root, text="Mindray Report:", font=head_font)
but_mindray = Button(root, text='Browse', command=browse_mindray)
col_but_mindray = Button(root, text='', command=mry_col, background=cfg.col['Mry'])
col_but_mindrayecg = Button(root, text='', command=mryecg_col, background=cfg.col['MryECG'])
lbl_mindrayecg = Label(root, text="ECG:", font=head_font)

lbl_bp_report = Label(root, text="Blood Pressure Reoport:", font=head_font)
but_bp_report = Button(root, text='BP Report', command=browse_bp_report)
but_bp_trends = Button(root, text='BP Trends', command=browse_bp_trends)
bp_lbl_std_sys = Label(root, text="Std Sys:")
bp_ent_std_sys = Entry(root)
bp_lbl_std_dia = Label(root, text="Std Dia:")
bp_ent_std_dia = Entry(root)
bp_lbl_mean_sys = Label(root, text="Mean Sys:")
bp_ent_mean_sys = Entry(root)
bp_lbl_mean_dia = Label(root, text="Mean Dia:")
bp_ent_mean_dia = Entry(root)


lbl_auth_report = Label(root, text="Authentication Reoport:", font=head_font)
but_auth_report = Button(root, text='Auth report', command=browse_auth_report)
auth_lbl_subjects = Label(root, text="Subjects:")
auth_ent_subjects = Entry(root)
auth_lbl_fp = Label(root, text="FP Success %:")
auth_ent_fp = Entry(root)
auth_lbl_fn = Label(root, text="FN Success %:")
auth_ent_fn = Entry(root)


lbl_zephyr_summaries = Label(root, text="Zephyr Folder:", font=head_font)
but_zephyr = Button(root, text='Browse', command=browse_zephyr)
col_but_zep = Button(root, text='', command=zep_col, background=cfg.col['Zeph'])
multi_var = IntVar()
multi_recs_check = Checkbutton(root, text='Multiple recordings per subject', variable=multi_var)
zep_stabilize_lbl = Label(root, text="Stabilize length (Seconds):")
zep_stabilize_entry = Entry(root)
zep_recs_count_lbl = Label(root, text="Number of recordings per subject:")
zep_recs_count_entry = Entry(root)

#   -------------------------   Deviations   -------------------------   #
deviation_lbl = Label(root, text="Deviations:", font=head_font)
rr_pct_val = StringVar(root, value=str(cfg.devs['RR'][0]))
rr_pct_lbl = Label(root, text="Respiration Rate %:")
rr_pct_ent = Entry(root, textvariable=rr_pct_val)

rr_unit_val = StringVar(root, value=str(cfg.devs['RR'][1]))
rr_unit_lbl = Label(root, text="Units:")
rr_unit_ent = Entry(root, textvariable=rr_unit_val)

hr_pct_val = StringVar(root, value=str(cfg.devs['HR'][0]))
hr_pct_lbl = Label(root, text="Heart Rate %:")
hr_pct_ent = Entry(root, textvariable=hr_pct_val)

hr_unit_val = StringVar(root, value=str(cfg.devs['HR'][1]))
hr_unit_lbl = Label(root, text="Units:")
hr_unit_ent = Entry(root, textvariable=hr_unit_val)


#   -------------------------   Row 13   -------------------------   #
is_hr = IntVar()
is_hr_check = Checkbutton(root, text='Heart Rate', variable=is_hr)
is_hr_check.select()

is_rr = IntVar()
is_rr_check = Checkbutton(root, text='Respiration Rate', variable=is_rr)
is_rr_check.deselect()

is_sys = IntVar()
is_sys_check = Checkbutton(root, text='Systolic BP', variable=is_sys)
is_sys_check.deselect()

is_dia = IntVar()
is_dia_check = Checkbutton(root, text='Diastolic BP', variable=is_dia)
is_dia_check.deselect()

report_37 = IntVar()
is_37 = Checkbutton(root, text='3.7 Report', variable=report_37)
is_37.select()

show_sum = IntVar()
but_show_sum = Checkbutton(root, text='Summary', variable=show_sum)
but_show_sum.select()


title_lbl = Label(root, text="Title:")
title_entry = Entry(root)
sub_title_lbl = Label(root, text="Sub-Title:")
sub_title_entry = Entry(root)

but_ba = Button(root, text='Bland Altman', command=barun)
but_compare = Button(root, text='Compare', command=compariuse)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| Grid |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

lbl_cu_file.grid(row=10, column=0, sticky=W, padx=10, pady=10)
but_cu_browse.grid(row=10, column=0, sticky=E)
col_but_cu.grid(row=10, column=1, sticky=W, pady=5)


lbl_rec_count.grid(row=11, column=0, sticky=W, padx=10)
min_len_ent.grid(row=11, column=0, padx=5)
lbl_rec_countsec.grid(row=11, column=0, sticky=E, padx=5)


plt_len_lbl.grid(row=10, column=4, sticky=W, pady=5, padx=5)
plt_len_entry.grid(row=11, column=4, sticky=W, pady=5, padx=5)
success_criteria_lbl.grid(row=12, column=4, sticky=W, pady=5, padx=5)
success_criteria_entry.grid(row=13, column=4, sticky=W, pady=5, padx=5)
romi_ver_lbl.grid(row=14, column=4, sticky=W, pady=5, padx=5)
romi_ver_ent.grid(row=15, column=4, sticky=W, pady=5, padx=5)

lst_times.grid(row=12, column=0, sticky=W, rowspan=5, columnspan=2, padx=10)
scrollbar.grid(row=12, column=0, sticky=N+E+S, rowspan=5, padx=1)

Separator(root, orient=HORIZONTAL).grid(row=18, columnspan=6, sticky="ew", pady=10, padx=10)

lbl_capno.grid(row=19, column=0, sticky=W, pady=10, padx=10)
but_capno.grid(row=19, column=0, sticky=E, pady=10)
col_but_cap.grid(row=19, column=1, sticky=W, pady=5)


lbl_nellcor.grid(row=110, column=0, sticky=W, padx=10, pady=10)
but_nellcor.grid(row=110, column=0, sticky=E, pady=10)
col_but_nellcor.grid(row=110, column=1, sticky=W, pady=10)

lbl_stamper.grid(row=19, column=2, sticky=W, padx=10, pady=10)
but_stamper.grid(row=19, column=2, sticky=E, pady=10)
lbl_mindray.grid(row=110, column=2, sticky=W, padx=10, pady=10)
but_mindray.grid(row=110, column=2, sticky=E, pady=10)
col_but_mindray.grid(row=110, column=3, sticky=W, pady=10)
lbl_mindrayecg.grid(row=110, column=3, sticky=E, pady=5, padx=5)
col_but_mindrayecg.grid(row=110, column=4, sticky=W, pady=10)

Separator(root, orient=HORIZONTAL).grid(row=111, columnspan=6, sticky="ew", pady=10, padx=10)

lbl_bp_report.grid(row=112, column=0, sticky=W, padx=10)
but_bp_report.grid(row=112, column=1, sticky=W, pady=5)
but_bp_trends.grid(row=112, column=1, sticky=E, pady=5)

bp_lbl_std_sys.grid(row=113, column=0, sticky=W, pady=5, padx=5)
bp_ent_std_sys.grid(row=113, column=1, sticky=W, pady=5, padx=5)
bp_lbl_std_dia.grid(row=113, column=2, sticky=W, pady=5, padx=5)
bp_ent_std_dia.grid(row=113, column=3, sticky=W, pady=5, padx=5)


bp_lbl_mean_sys.grid(row=114, column=0, sticky=W, pady=5, padx=5)
bp_ent_mean_sys.grid(row=114, column=1, sticky=W, pady=5, padx=5)
bp_lbl_mean_dia.grid(row=114, column=2, sticky=W, pady=5, padx=5)
bp_ent_mean_dia.grid(row=114, column=3, sticky=W, pady=5, padx=5)

Separator(root, orient=HORIZONTAL).grid(row=115, columnspan=6, sticky="ew", pady=10, padx=10)

# lbl_auth_report.grid(row=116, column=0, sticky=W, padx=10)
# but_auth_report.grid(row=116, column=1, sticky=W, pady=5)
# auth_lbl_subjects.grid(row=117, column=0, sticky=W, pady=5, padx=5)
# auth_ent_subjects.grid(row=117, column=1, sticky=W, pady=5, padx=5)
# auth_lbl_fp.grid(row=118, column=0, sticky=W, pady=5, padx=5)
# auth_ent_fp.grid(row=118, column=1, sticky=W, pady=5, padx=5)
# auth_lbl_fn.grid(row=118, column=2, sticky=W, pady=5, padx=5)
# auth_ent_fn.grid(row=118, column=3, sticky=W, pady=5, padx=5)

# Separator(root, orient=HORIZONTAL).grid(row=119, columnspan=6, sticky="ew", pady=10, padx=10)
'''
lbl_zephyr_summaries.grid(row=120, column=0, sticky=W, padx=10)
but_zephyr.grid(row=120, column=0, sticky=E, pady=5)
col_but_zep.grid(row=120, column=1, sticky=W, pady=5)

multi_recs_check.grid(row=120, column=2, sticky=W, pady=5, padx=5)
zep_stabilize_lbl.grid(row=121, column=0, sticky=W, pady=5, padx=5)
zep_stabilize_entry.grid(row=121, column=1, sticky=W, pady=5, padx=5)
zep_recs_count_lbl.grid(row=121, column=2, sticky=W, pady=5, padx=5)
zep_recs_count_entry.grid(row=121, column=3, sticky=W, pady=5, padx=5)

Separator(root, orient=HORIZONTAL).grid(row=122, columnspan=6, sticky="ew", pady=10, padx=10)
'''
deviation_lbl.grid(row=123, column=0, sticky=W, pady=5, padx=10)
show_dev_check.grid(row=124, column=0, sticky=W, pady=5, padx=5)
count_dev_check.grid(row=124, column=1, sticky=W, pady=5, padx=5)

rr_pct_lbl.grid(row=125, column=0, sticky=W, pady=5, padx=10)
rr_pct_ent.grid(row=125, column=1, sticky=W, pady=5, padx=10)
rr_unit_lbl.grid(row=125, column=2, sticky=E, pady=5, padx=10)
rr_unit_ent.grid(row=125, column=3, sticky=W, pady=5, padx=10)

hr_pct_lbl.grid(row=126, column=0, sticky=W, pady=5, padx=10)
hr_pct_ent.grid(row=126, column=1, sticky=W, pady=5, padx=10)
hr_unit_lbl.grid(row=126, column=2, sticky=E, pady=5, padx=10)
hr_unit_ent.grid(row=126, column=3, sticky=W, pady=5, padx=10)

Separator(root, orient=HORIZONTAL).grid(row=127, columnspan=6, sticky="ew", pady=10, padx=10)

is_hr_check.grid(row=128, column=0, sticky=W, pady=5, padx=5)
is_rr_check.grid(row=128, column=1, sticky=W, pady=5, padx=5)
is_sys_check.grid(row=128, column=2, sticky=W, pady=5, padx=5)
is_dia_check.grid(row=128, column=3, sticky=W, pady=5, padx=5)

is_37.grid(row=128, column=4, sticky=E, pady=5, padx=5)
but_show_sum.grid(row=128, column=5, sticky=E, pady=5, padx=5)

title_lbl.grid(row=129, column=0, columnspan=1, sticky=W, padx=10, pady=5)
title_entry.grid(row=129, column=1, columnspan=1, sticky=W, padx=10, pady=5)
sub_title_lbl.grid(row=129, column=2, columnspan=1, sticky=E, padx=10, pady=5)
sub_title_entry.grid(row=129, column=3, columnspan=1, sticky=E, padx=10, pady=5)

but_ba.grid(row=129, column=4, columnspan=1, sticky=E, padx=10, pady=5)
but_compare.grid(row=129, column=5, columnspan=1, sticky=E, padx=10, pady=5)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| Run |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


root.update_idletasks()
root.mainloop()
