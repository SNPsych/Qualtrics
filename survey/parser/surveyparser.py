__author__ = 'simonyu'

from datetime import datetime, timedelta
from io import StringIO
import uuid
import shutil
import os

import pandas as pd
from pandas.core.frame import DataFrame
from mako.template import Template
from mako.runtime import Context
import simplejson

from sleepvl.settings import BASE_DIR

BLANK_E = '.E'
BLANK_B = '.B'
BLANK_VALUE = ''
BLANK_NA = 'NA'
MM_ZERO = '00'


def hour_to_mins(x):
    return int(x) * 60


def str_to_int(x):
    return int(x)


def find_weekday_ymdhms(x):
    an_date = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    day = an_date.weekday()
    return day + 1


def find_weekday_ymd(x):
    an_date = datetime.strptime(x, '%Y-%m-%d')
    day = an_date.weekday()
    return day + 1


def reduce_one_day(x):
    an_date = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    return (an_date + timedelta(days=-1)).strftime('%Y-%m-%d %H:%M:%S')


def fill_for_hhmm(x):
    # If hh is blank, return .E
    if x.find('NA:') != -1:
        x = BLANK_E
    return x


def fill_for_yesno(x):
    if x == 'Yes':
        x = 1
    elif x == 'No':
        x = 0
    else:
        x = BLANK_E
    return x


def fill_for_rank(x):
    if x == 'Very Poor' or x == 'Not at all rested':
        x = 1
    elif x == 'Poor' or x == 'Slightly rested':
        x = 2
    elif x == 'Fair' or x == 'Somewhat rested':
        x = 3
    elif x == 'Good' or x == 'Well rested':
        x = 4
    elif x == 'Very Good' or x == 'Very well rested':
        x = 5
    else:
        x = BLANK_E
    return x


def check_for_attempt(x):
    if x == 'Yes':
        x = 1
    else:
        x = 0
    return x


def process_smed(x):
    smed = x['SMED']

    if smed == 'Yes':
        smed = 1
        # smed1 = x['SMED1'] don't need to change as SMED1 already fillna with .E
        # smed2 = x['SMED2'] don't need to change as SMED2 already fillna with .E
        # smed3 = x['SMED3'] don't need to change as SMED3 already fillna with .E
        smed1t = x['SMED1T_HH'] + ":" + x['SMED1T_MM']

        if smed1t.find('NA:') != -1:
            x['SMED1T'] = BLANK_E
        else:
            x['SMED1T'] = smed1t

        smed2t = x['SMED2T_HH'] + ":" + x['SMED2T_MM']
        if smed2t.find('NA:') != -1:
            x['SMED2T'] = BLANK_E
        else:
            x['SMED2T'] = smed2t

        smed3t = x['SMED3T_HH'] + ":" + x['SMED3T_MM']
        if smed3t.find('NA:') != -1:
            x['SMED3T'] = BLANK_E
        else:
            x['SMED3T'] = smed3t
    else:
        smed = 0
        x['SMED1'] = BLANK_B
        x['SMED2'] = BLANK_B
        x['SMED3'] = BLANK_B

        x['SMED1T'] = BLANK_B
        x['SMED2T'] = BLANK_B
        x['SMED3T'] = BLANK_B
    x['SMED'] = smed
    return x


def to_ymdstr(x):
    an_date = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    return an_date.strftime('%Y-%m-%d')


def reduce_one_day_ymdstr(x):
    an_date = datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
    return (an_date + timedelta(days=-1)).strftime('%Y-%m-%d')


def process_awaken(x):
    attempt = x['ATTEMPT']
    if attempt:
        x['BT'] = fill_for_hhmm(x['BT'])
        x['LO'] = fill_for_hhmm(x['LO'])
        x['WT'] = fill_for_hhmm(x['WT'])
        x['RT'] = fill_for_hhmm(x['RT'])
        current_date_str = x['Date']
        bt_time_str = x['BT']
        lo_time_str = x['LO']
        wt_time_str = x['WT']
        rt_time_str = x['RT']
        bt_datetime_str = current_date_str + ' ' + bt_time_str
        lo_datetime_str = current_date_str + ' ' + lo_time_str
        wt_datetime_str = current_date_str + ' ' + wt_time_str
        rt_datetime_str = current_date_str + ' ' + rt_time_str

        # calculate the TIB first
        if bt_datetime_str.find(BLANK_E) != -1 or rt_datetime_str.find(BLANK_E) != -1:
            x['TIB'] = BLANK_B
        else:
            bt_time = datetime.strptime(bt_datetime_str, '%Y-%m-%d %H:%M')
            rt_time = datetime.strptime(rt_datetime_str, '%Y-%m-%d %H:%M')

            if rt_time < bt_time:
                rt_time = rt_time + timedelta(days=1)
            x['TIB'] = '{0:.2f}'.format((rt_time - bt_time).total_seconds() / 60)

        # calculate SE1 and SE2
        # if TIB is .B or TIB is zero. just set SE1 = .B
        if x['TIB'] == BLANK_B or float(x['TIB']) == 0:
            x['SE1'] = BLANK_B
            x['SE2'] = BLANK_B
        else:
            x['SE1'] = '{0:.2f}'.format(float(x['TST']) / float(x['TIB']))
            if lo_datetime_str.find(BLANK_E) != -1 or wt_datetime_str.find(BLANK_E) != -1:
                x['SE2'] = BLANK_B
            else:
                bt_time = datetime.strptime(bt_datetime_str, '%Y-%m-%d %H:%M')
                lo_time = datetime.strptime(lo_datetime_str, '%Y-%m-%d %H:%M')
                rt_time = datetime.strptime(rt_datetime_str, '%Y-%m-%d %H:%M')
                wt_time = datetime.strptime(wt_datetime_str, '%Y-%m-%d %H:%M')

                if lo_time < bt_time:
                    lo_time = lo_time + timedelta(days=1)
                if rt_time < wt_time:
                    rt_time = rt_time + timedelta(days=1)

                lo_bt = (lo_time - bt_time).total_seconds() / 60
                rt_wt = (rt_time - wt_time).total_seconds() / 60

                sol = float(x['SOL'])
                wasot = float(x['WASOT'])
                tib = float(x['TIB'])
                # [TIB - (( LO-BT )+( RT - WT ) + SOL + WASOT ) ]/TIB
                x['SE2'] = '{0:.2f}'.format((tib - (lo_bt + rt_wt + sol + wasot)) / tib)
                # print('-------- SE2 : [{} - ({} + {} + {} + {})] / {} = {}'.format(tib, lo_bt, rt_wt, sol, wasot, tib, x['SE2']))

        # parse the EA
        ea = x['EA']
        if ea == 'Yes':
            x['EA'] = 1
        elif ea == 'No':
            x['EA'] = 0
        else:
            x['EA'] = BLANK_E
        # adjust the EA for old record, if EAT is not 0, then for any blank EA should be 1
        eat = x['EAT']
        if eat != 0:
            if x['EA'] == BLANK_E:
                x['EA'] = 1
        # finally we parse the EAT
        if x['EA'] == 0:
            x['EAT'] = BLANK_B
    else:
        x['BT'] = BLANK_B
        x['LO'] = BLANK_B
        x['WT'] = BLANK_B
        x['RT'] = BLANK_B
        x['SOL'] = BLANK_B
        x['SNZ'] = BLANK_B
        x['TST'] = BLANK_B
        x['WASON'] = BLANK_B
        x['WASOT'] = BLANK_B
        x['EA'] = BLANK_B
        x['EAT'] = BLANK_B
        x['SQ'] = BLANK_B
        x['REST'] = BLANK_B
        x['TIB'] = BLANK_B
        x['SE1'] = BLANK_B
        x['SE2'] = BLANK_B
    return x


class SurveyParser(object):
    def __init__(self, in_filename, out_filename):
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.survey_new_csv = DataFrame()
        self.survey_tmp_dict = {}
        self.patient_ids = []
        self.survey_patients = []
        self._init_load_all_patient_ids()

    def _init_load_all_patient_ids(self):
        base_patient_store_dir = os.path.join(BASE_DIR, 'id_store')
        patient_id_xls_file = os.path.join(base_patient_store_dir, 'IDs.xlsx')
        # load the excel file
        id_xls = pd.ExcelFile(patient_id_xls_file)
        # parse the excel file by pandas
        id_dataframe = id_xls.parse(id_xls.sheet_names[0])
        # get a list of patient ids
        patient_id_list = id_dataframe.ID.unique().tolist()

        # create empty list for all patients to store patient id json
        self.all_patient_id_json_store = []
        # check the id store exists
        if os.path.isfile(BASE_DIR + '/id_store/idstore.json'):
            store_json = open(BASE_DIR + '/id_store/idstore.json')
            self.all_patient_id_json_store = simplejson.load(store_json)


        for pid in patient_id_list:
            patient = {}
            patientids = self.get_patient_by_id(str(pid))
            # if not found
            if len(patientids) == 0:
                uuid = self.generate_uuid()
                patient['id'] = str(pid)
                patient['uuid'] = uuid
                self.all_patient_id_json_store.append(patient)

        # save all patient json id into json file
        with open(os.path.join(base_patient_store_dir, 'idstore.json'), 'w') as f:
            simplejson.dump(self.all_patient_id_json_store, f)

    def get_patient_by_id(self, patient_id):
        return [patient for patient in self.all_patient_id_json_store if patient['id'] == patient_id]

    def get_survey_data_from_dict(self, key):
        return self.survey_tmp_dict.get(key)

    def set_survey_data_in_dict(self, key, value):
        self.survey_tmp_dict[key] = value

    def clean_survey_data_dict(self):
        self.survey_tmp_dict.clear()

    def parse_csv(self):
        # Read the csv file, and skip the first row as it's a long string label name
        survey_data = pd.read_csv(self.in_filename)[1:]

        bb_survey_flags = ['2', '<strong>B. I want to record my experiences during the day today (please complete before going to bed).</strong>']
        # Before sleep survey data
        bb_survey = survey_data.loc[
            survey_data['QID20'] != '<strong>A. I want to record my sleep last night (please complete upon awakening).</strong>']


        # Upon awakening survey data
        ab_survey = survey_data.loc[
            survey_data['QID20'] == '<strong>A. I want to record my sleep last night (please complete upon awakening).</strong>']

        # Define a before sleep DataFrame
        bb_df = DataFrame()
        bb_df['User'] = bb_survey['V3']
        bb_df['Date'] = bb_survey['V8'].apply(to_ymdstr)
        bb_df['Day'] = bb_survey['V8'].apply(find_weekday_ymdhms)
        # Create empty submission times first, fill it later
        bb_df['MULT'] = ''
        bb_df['NAPN'] = bb_survey['QID27'].fillna(BLANK_E)
        bb_df['NAPT'] = bb_survey['QID11#2_1'].fillna(0).apply(hour_to_mins) + bb_survey['QID11#1_1'].fillna(0).apply(str_to_int)
        bb_df['ALN'] = bb_survey['QID15#3_1_1_TEXT'].fillna(BLANK_E)

        # ALT
        alt_series = bb_survey['QID15#2_1'].fillna(BLANK_NA) + ":" + bb_survey['QID15#1_1'].fillna(MM_ZERO)
        bb_df['ALT'] = alt_series.apply(fill_for_hhmm)

        bb_df['CAFN'] = bb_survey['QID23#3_1_1_TEXT'].fillna(BLANK_E)

        # CAFT
        caft_series = bb_survey['QID23#2_1'].fillna(BLANK_NA) + ":" + bb_survey['QID23#1_1'].fillna(MM_ZERO)
        bb_df['CAFT'] = caft_series.apply(fill_for_hhmm)

        # Parse SMED
        smed_df = DataFrame()
        smed_df['SMED'] = bb_survey['QID18']

        smed_df['SMED1'] = bb_survey['QID17#3_1_1_TEXT'].fillna(BLANK_E)
        smed_df['SMED1T_HH'] = bb_survey['QID17#2_1'].fillna(BLANK_NA)
        smed_df['SMED1T_MM'] = bb_survey['QID17#1_1'].fillna(MM_ZERO)

        smed_df['SMED2'] = bb_survey['QID17#3_2_1_TEXT'].fillna(BLANK_E)
        smed_df['SMED2T_HH'] = bb_survey['QID17#2_2'].fillna(BLANK_NA)
        smed_df['SMED2T_MM'] = bb_survey['QID17#1_2'].fillna(MM_ZERO)

        smed_df['SMED3'] = bb_survey['QID17#3_3_1_TEXT'].fillna(BLANK_E)
        smed_df['SMED3T_HH'] = bb_survey['QID17#2_3'].fillna(BLANK_NA)
        smed_df['SMED3T_MM'] = bb_survey['QID17#1_3'].fillna(MM_ZERO)
        smed_df = smed_df.apply(process_smed, axis=1)

        bb_df['SMED'] = smed_df['SMED']
        bb_df['SMED1'] = smed_df['SMED1']
        bb_df['SMED1T'] = smed_df['SMED1T']
        bb_df['SMED2'] = smed_df['SMED2']
        bb_df['SMED2T'] = smed_df['SMED2T']
        bb_df['SMED3'] = smed_df['SMED3']
        bb_df['SMED3T'] = smed_df['SMED3T']
        bb_df['NOTEBB'] = bb_survey['QID19'].fillna(BLANK_E)
        bb_df['ATTEMPT'] = ''
        bb_df['BT'] = ''
        bb_df['LO'] = ''
        bb_df['WT'] = ''
        bb_df['RT'] = ''
        bb_df['SOL'] = ''
        bb_df['SNZ'] = ''
        bb_df['TST'] = ''
        bb_df['WASON'] = ''
        bb_df['WASOT'] = ''
        bb_df['EA'] = ''
        bb_df['EAT'] = ''
        bb_df['SQ'] = ''
        bb_df['REST'] = ''
        bb_df['NOTEWU'] = ''
        bb_df['TIB'] = ''
        bb_df['SE1'] = ''
        bb_df['SE2'] = ''
        # process MULT
        bb_df['MULT'] = self.process_mult(bb_df)
        # test code
        # bb_df.to_csv('before_bed_survey.csv', index=False)
        # End of before sleep

        # Start for Upon awakening
        ab_df = DataFrame()
        ab_df['User'] = ab_survey['V3']
        ab_df['Date'] = ab_survey['V8'].apply(reduce_one_day_ymdstr)
        ab_df['Day'] = ab_df['Date'].apply(find_weekday_ymd)
        # submission times
        ab_df['MULT'] = ''
        ab_df['NAPN'] = ''
        ab_df['NAPT'] = ''
        ab_df['ALN'] = ''
        ab_df['ALT'] = ''
        ab_df['CAFN'] = ''
        ab_df['CAFT'] = ''
        ab_df['SMED'] = ''
        ab_df['SMED1'] = ''
        ab_df['SMED1T'] = ''
        ab_df['SMED2'] = ''
        ab_df['SMED2T'] = ''
        ab_df['SMED3'] = ''
        ab_df['SMED3T'] = ''
        ab_df['NOTEBB'] = ''

        tmp_ab_df = DataFrame()
        tmp_ab_df['Date'] = ab_df['Date']
        tmp_ab_df['ATTEMPT'] = ab_survey['QID24'].fillna('Yes').apply(check_for_attempt)
        tmp_ab_df['BT'] = ab_survey['QID2#2_1'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_1'].fillna(MM_ZERO)
        tmp_ab_df['LO'] = ab_survey['QID2#2_2'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_2'].fillna(MM_ZERO)
        tmp_ab_df['WT'] = ab_survey['QID2#2_3'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_3'].fillna(MM_ZERO)
        tmp_ab_df['RT'] = ab_survey['QID2#2_4'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_4'].fillna(MM_ZERO)
        tmp_ab_df['SOL'] = ab_survey['QID3#2_1'].fillna(0).apply(hour_to_mins) + ab_survey['QID3#1_1'].fillna(0).apply(str_to_int)
        tmp_ab_df['SNZ'] = ab_survey['QID3#2_2'].fillna(0).apply(hour_to_mins) + ab_survey['QID3#1_2'].fillna(0).apply(str_to_int)
        tmp_ab_df['TST'] = ab_survey['QID3#2_3'].fillna(0).apply(hour_to_mins) + ab_survey['QID3#1_3'].fillna(0).apply(str_to_int)
        tmp_ab_df['WASON'] = ab_survey['QID6#3_1_1_TEXT'].fillna(BLANK_E)
        tmp_ab_df['WASOT'] = ab_survey['QID6#2_1'].fillna(0).apply(hour_to_mins) + ab_survey['QID6#1_1'].fillna(0).apply(str_to_int)

        tmp_ab_df['EA'] = ab_survey['QID26'].fillna(BLANK_E)

        tmp_ab_df['EAT'] = ab_survey['QID7#2_1'].fillna(0).apply(hour_to_mins) + ab_survey['QID7#1_1'].fillna(0).apply(str_to_int)

        tmp_ab_df['SQ'] = ab_survey['QID5'].apply(fill_for_rank)
        tmp_ab_df['REST'] = ab_survey['QID8'].apply(fill_for_rank)

        tmp_ab_df = tmp_ab_df.apply(process_awaken, axis=1)

        ab_df['ATTEMPT'] = tmp_ab_df['ATTEMPT']
        ab_df['BT'] = tmp_ab_df['BT']
        ab_df['LO'] = tmp_ab_df['LO']
        ab_df['WT'] = tmp_ab_df['WT']
        ab_df['RT'] = tmp_ab_df['RT']
        ab_df['SOL'] = tmp_ab_df['SOL']
        ab_df['SNZ'] = tmp_ab_df['SNZ']
        ab_df['TST'] = tmp_ab_df['TST']
        ab_df['WASON'] = tmp_ab_df['WASON']
        ab_df['WASOT'] = tmp_ab_df['WASOT']
        ab_df['EA'] = tmp_ab_df['EA']
        ab_df['EAT'] = tmp_ab_df['EAT']
        ab_df['SQ'] = tmp_ab_df['SQ']
        ab_df['REST'] = tmp_ab_df['REST']
        ab_df['NOTEWU'] = ab_survey['QID28'].fillna(BLANK_E)
        ab_df['TIB'] = tmp_ab_df['TIB']
        ab_df['SE1'] = tmp_ab_df['SE1']
        ab_df['SE2'] = tmp_ab_df['SE2']

        # test code
        # ab_df.to_csv('after_bed_survey.csv', index=False)

        # Process MULT
        ab_df['MULT'] = self.process_mult(ab_df)

        # Merge two types of surveys together
        self.survey_new_csv = bb_df.append(ab_df, ignore_index=True)

        # sorting it first
        self.survey_new_csv = self.survey_new_csv.sort(['User', 'Date'], ascending=[1, 1])

        # the combined_dulicated_dfs will hold the combined duplicated records
        combined_duplicated_dfs = []
        #  get all unique patient ids
        self.patient_ids = self.survey_new_csv.User.unique().tolist()

        for index, row in self.survey_new_csv.iterrows():
            user_id = row['User']
            date = row['Date']
            mult = row['MULT']
            key = '{}'.format(user_id) + '{}'.format(date) + '{}'.format(mult)
            found_index = self.get_survey_data_from_dict(key)
            # TODO: remove this temporary solution
            if user_id == '1504':
                print('-- Removed the USER ID 1504 Record temporarily due to generate pdf error in R')
                self.survey_new_csv.drop([index], inplace=True)

            if found_index is None:
                self.set_survey_data_in_dict(key, index)
            else:
                duplicated_df = DataFrame(self.survey_new_csv, index=[found_index, index])
                # print('------ duplicated df: {}'.format(duplicated_df))
                # we drop these duplicated df recordes
                self.survey_new_csv.drop([found_index, index], inplace=True)

                # combines these two duplicated dfs into one
                combined_df = self.combine_rows(duplicated_df)
                # print('------ combined df: {}'.format(combined_df))
                #  append this into combined_duplicated_dfs list
                combined_duplicated_dfs.append(combined_df)
        # concat these combined duplicated df list
        all_duplicated = pd.concat(combined_duplicated_dfs)
        # append it into survey new csv file
        self.survey_new_csv = self.survey_new_csv.append(all_duplicated, ignore_index=True)

    def create_csv(self):
        """
        create new csv file
        """
        self.survey_new_csv = self.survey_new_csv.sort(['User', 'Date'], ascending=[1, 1])
        self.survey_new_csv.to_csv(self.out_filename, index=False)
        print('--- Finished to create a new csv file.')

    def process_mult(self, survey_df):
        self.clean_survey_data_dict()

        mult_list = []
        index_list = []
        df = survey_df.sort(['User', 'Date'], ascending=[1, 1])
        for index, row in df.iterrows():
            key = row['User'] + '-' + row['Date']
            mult = self.get_survey_data_from_dict(key)
            if mult is None:
                mult = 0
            mult += 1
            self.set_survey_data_in_dict(key, mult)
            mult_list.append(str(mult))
            index_list.append(index)
        mult_df = DataFrame({'MULT': mult_list}, index=index_list)

        return mult_df['MULT']

    def combine_rows(self, to_combined_df):
        tmp_df = DataFrame()
        tmp_df['User'] = to_combined_df['User'].values[:1]
        tmp_df['Date'] = to_combined_df['Date'].values[:1]
        tmp_df['Day'] = to_combined_df['Day'].values[:1]
        tmp_df['MULT'] = to_combined_df['MULT'].values[:1]
        napn = to_combined_df['NAPN'].fillna('').values
        if napn[0] != '':
            tmp_df['NAPN'] = napn[0]
        else:
            tmp_df['NAPN'] = napn[1]

        napt = to_combined_df['NAPT'].fillna('').values
        if napt[0] != '':
            tmp_df['NAPT'] = napt[0]
        else:
            tmp_df['NAPT'] = napt[1]

        aln = to_combined_df['ALN'].fillna('').values
        if aln[0] != '':
            tmp_df['ALN'] = aln[0]
        else:
            tmp_df['ALN'] = aln[1]

        alt = to_combined_df['ALT'].fillna('').values
        if alt[0] != '':
            tmp_df['ALT'] = alt[0]
        else:
            tmp_df['ALT'] = alt[1]

        cafn = to_combined_df['CAFN'].fillna('').values
        if cafn[0] != '':
            tmp_df['CAFN'] = cafn[0]
        else:
            tmp_df['CAFN'] = cafn[1]

        caft = to_combined_df['CAFT'].fillna('').values
        if caft[0] != '':
            tmp_df['CAFT'] = caft[0]
        else:
            tmp_df['CAFT'] = caft[1]

        smed = to_combined_df['SMED'].fillna('').values
        if smed[0] != '':
            tmp_df['SMED'] = smed[0]
        else:
            tmp_df['SMED'] = smed[1]

        smed1 = to_combined_df['SMED1'].fillna('').values
        if smed1[0] != '':
            tmp_df['SMED1'] = smed1[0]
        else:
            tmp_df['SMED1'] = smed1[1]

        smed1t = to_combined_df['SMED1T'].fillna('').values
        if smed1t[0] != '':
            tmp_df['SMED1T'] = smed1t[0]
        else:
            tmp_df['SMED1T'] = smed1t[1]

        smed2 = to_combined_df['SMED2'].fillna('').values
        if smed2[0] != '':
            tmp_df['SMED2'] = smed2[0]
        else:
            tmp_df['SMED2'] = smed2[1]

        smed2t = to_combined_df['SMED2T'].fillna('').values
        if smed2t[0] != '':
            tmp_df['SMED2T'] = smed2t[0]
        else:
            tmp_df['SMED2T'] = smed2t[1]

        smed3 = to_combined_df['SMED3'].fillna('').values
        if smed3[0] != '':
            tmp_df['SMED3'] = smed3[0]
        else:
            tmp_df['SMED3'] = smed3[1]

        smed3t = to_combined_df['SMED3T'].fillna('').values
        if smed3t[0] != '':
            tmp_df['SMED3T'] = smed3t[0]
        else:
            tmp_df['SMED3T'] = smed3t[1]

        notebb = to_combined_df['NOTEBB'].fillna('').values
        if notebb[0] != '':
            tmp_df['NOTEBB'] = notebb[0]
        else:
            tmp_df['NOTEBB'] = notebb[1]

        attempt = to_combined_df['ATTEMPT'].fillna('').values
        if attempt[0] != '':
            tmp_df['ATTEMPT'] = attempt[0]
        else:
            tmp_df['ATTEMPT'] = attempt[1]

        bt = to_combined_df['BT'].fillna('').values
        if bt[0] != '':
            tmp_df['BT'] = bt[0]
        else:
            tmp_df['BT'] = bt[1]

        lo = to_combined_df['LO'].fillna('').values
        if lo[0] != '':
            tmp_df['LO'] = lo[0]
        else:
            tmp_df['LO'] = lo[1]

        wt = to_combined_df['WT'].fillna('').values
        if wt[0] != '':
            tmp_df['WT'] = wt[0]
        else:
            tmp_df['WT'] = wt[1]

        rt = to_combined_df['RT'].fillna('').values
        if rt[0] != '':
            tmp_df['RT'] = rt[0]
        else:
            tmp_df['RT'] = rt[1]

        sol = to_combined_df['SOL'].fillna('').values
        if sol[0] != '':
            tmp_df['SOL'] = sol[0]
        else:
            tmp_df['SOL'] = sol[1]

        snz = to_combined_df['SNZ'].fillna('').values
        if snz[0] != '':
            tmp_df['SNZ'] = snz[0]
        else:
            tmp_df['SNZ'] = snz[1]

        tst = to_combined_df['TST'].fillna('').values
        if tst[0] != '':
            tmp_df['TST'] = tst[0]
        else:
            tmp_df['TST'] = tst[1]

        wason = to_combined_df['WASON'].fillna('').values
        if wason[0] != '':
            tmp_df['WASON'] = wason[0]
        else:
            tmp_df['WASON'] = wason[1]

        wasot = to_combined_df['WASOT'].fillna('').values
        if wasot[0] != '':
            tmp_df['WASOT'] = wasot[0]
        else:
            tmp_df['WASOT'] = wasot[1]

        ea = to_combined_df['EA'].fillna('').values
        if ea[0] != '':
            tmp_df['EA'] = ea[0]
        else:
            tmp_df['EA'] = ea[1]

        eat = to_combined_df['EAT'].fillna('').values
        if eat[0] != '':
            tmp_df['EAT'] = eat[0]
        else:
            tmp_df['EAT'] = eat[1]

        sq = to_combined_df['SQ'].fillna('').values
        if sq[0] != '':
            tmp_df['SQ'] = sq[0]
        else:
            tmp_df['SQ'] = sq[1]

        rest = to_combined_df['REST'].fillna('').values
        if rest[0] != '':
            tmp_df['REST'] = rest[0]
        else:
            tmp_df['REST'] = rest[1]

        notewu = to_combined_df['NOTEWU'].fillna('').values
        if notewu[0] != '':
            tmp_df['NOTEWU'] = notewu[0]
        else:
            tmp_df['NOTEWU'] = notewu[1]

        tib = to_combined_df['TIB'].fillna('').values
        if tib[0] != '':
            tmp_df['TIB'] = tib[0]
        else:
            tmp_df['TIB'] = tib[1]

        se1 = to_combined_df['SE1'].fillna('').values
        if se1[0] != '':
            tmp_df['SE1'] = se1[0]
        else:
            tmp_df['SE1'] = se1[1]

        se2 = to_combined_df['SE2'].fillna('').values
        if se2[0] != '':
            tmp_df['SE2'] = se2[0]
        else:
            tmp_df['SE2'] = se2[1]
        return tmp_df

    def create_html(self, tpl_file, dest_dir):
        new_patient_id_added = False

        for pid in self.patient_ids:
            patient = {}
            patientids = self.get_patient_by_id(str(pid))
            if len(patientids) == 0:
                uuid = self.generate_uuid()
                patient['id'] = pid
                patient['uuid'] = uuid
                self.all_patient_id_json_store.append(patient)
                self.survey_patients.append(patient)
                new_patient_id_added = True
            else:
                self.survey_patients.append(patientids[0])
        # if added a new patient. then we need to update the idstore.json
        if new_patient_id_added:
              # save all patient json id into json file
            with open(os.path.join(BASE_DIR, 'id_store', 'idstore.json'), 'w') as f:
                simplejson.dump(self.all_patient_id_json_store, f)
        else:
            print('no new patient id added')

        # create a latest report index html file
        index_template = Template(filename=tpl_file)
        output = StringIO()
        ctx = Context(output, patients=self.survey_patients)
        index_template.render_context(ctx)
        index_file = os.path.join(dest_dir, 'index.html')
        with open(index_file, 'wt') as f:
            f.write(output.getvalue())
        # close object and discard memory buffer --
        # .getvalue() will now raise an exception.
        output.close()

        # Create a Pandas dataframe from some data.
        df = DataFrame.from_dict(self.all_patient_id_json_store)
        df = df.sort(['id', 'uuid'], ascending=[1, 1])
        excel_file = os.path.join(dest_dir, 'IDs.xlsx')
        # Create a Pandas Excel writer using XlsxWriter as the engine.
        excel_writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(excel_writer, index=False, sheet_name='Diary')
        # Close the Pandas Excel writer and output the Excel file.
        excel_writer.save()


    def generate_uuid(self):
        return uuid.uuid4().__str__()

    def copy_latest_reports(self, reports_src_dir, latest_report_dir, current_date):
        for patient in self.survey_patients:
            patient_id = patient['id']
            patient_uuid = patient['uuid']
            pdf_file = os.path.join(reports_src_dir, patient_id, (patient_id + '-' + current_date + '.pdf'))
            try:
                dest_pdf_dir = os.path.join(latest_report_dir, 'pdf')
                dest_pdf_file = os.path.join(dest_pdf_dir, (patient_id + '-' + current_date + '.pdf'))
                dest_pdf_new_file = os.path.join(dest_pdf_dir, (patient_uuid + '.pdf'))
                shutil.copy(pdf_file, dest_pdf_dir)
                os.rename(dest_pdf_file, dest_pdf_new_file)
            except Exception as ex:
                print('Copy pdf report - {} failed, {}'.format(pdf_file, ex))

            html_file = os.path.join(reports_src_dir, patient_id, (patient_id + '-' + current_date + '.html'))
            try:
                dest_html_dir = os.path.join(latest_report_dir, 'html')
                dest_html_file = os.path.join(dest_html_dir, (patient_id + '-' + current_date + '.html'))
                dest_html_new_file = os.path.join(dest_html_dir, (patient_uuid + '.html'))
                shutil.copy(html_file, dest_html_dir)
                os.rename(dest_html_file, dest_html_new_file)
            except Exception as ex:
                print('Copy html report - {} failed, {}'.format(html_file, ex))
