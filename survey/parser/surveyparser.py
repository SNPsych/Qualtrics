__author__ = 'simonyu'

from datetime import datetime, timedelta

import pandas as pd
from pandas.core.frame import DataFrame

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


def process_calculated(x):
    current_date_str = x['Date']
    bt_time_str = x['BT']
    lo_time_str = x['LO']
    wt_time_str = x['WT']
    rt_time_str = x['RT']
    x['BT'] = current_date_str + ' ' + bt_time_str
    x['LO'] = current_date_str + ' ' + lo_time_str
    x['WT'] = current_date_str + ' ' + wt_time_str
    x['RT'] = current_date_str + ' ' + rt_time_str

    # calculate the TIB first
    if x['BT'].find(BLANK_E) != -1 or x['RT'].find(BLANK_E) != -1:
        x['TIB'] = BLANK_B
    else:
        bt_time = datetime.strptime(x['BT'], '%Y-%m-%d %H:%M')
        rt_time = datetime.strptime(x['RT'], '%Y-%m-%d %H:%M')

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
        if x['LO'].find(BLANK_E) != -1 or x['WT'].find(BLANK_E) != -1:
            x['SE2'] = BLANK_B
        else:
            bt_time = datetime.strptime(x['BT'], '%Y-%m-%d %H:%M')
            lo_time = datetime.strptime(x['LO'], '%Y-%m-%d %H:%M')
            rt_time = datetime.strptime(x['RT'], '%Y-%m-%d %H:%M')
            wt_time = datetime.strptime(x['WT'], '%Y-%m-%d %H:%M')

            if lo_time < bt_time:
                lo_time = lo_time + timedelta(days=1)
            if rt_time < wt_time:
                rt_time = rt_time + timedelta(days=1)
            lo_bt = (lo_time - bt_time).total_seconds() / 60
            rt_wt = (rt_time - wt_time).total_seconds() / 60
            sol = float(x['SOL'])
            wasot = float(x['WASOT'])
            tib = float(x['TIB'])
            x['SE2'] = '{0:.2f}'.format((tib - (lo_bt + rt_wt + sol + wasot)) / tib)
    return x


class SurveyParser(object):
    def __init__(self, in_filename, out_filename):
        self.in_filename = in_filename
        self.out_filename = out_filename
        self.survey_new_csv = DataFrame()
        self.survey_tmp_dict = {}

    def parse_csv(self):
        # Read the csv file, and skip the first row as it's a long string label name
        survey_data = pd.read_csv(self.in_filename)[1:]

        # Before sleep survey data
        bb_survey = survey_data.loc[survey_data['QID20'] == 'Before bed']

        # Upon awakening survey data
        ab_survey = survey_data.loc[survey_data['QID20'] != 'Before bed']

        # Define a before sleep DataFrame
        bb_df = DataFrame()
        bb_df['User'] = bb_survey['V3']
        bb_df['Date'] = bb_survey['V8'].apply(to_ymdstr)
        bb_df['Day'] = bb_survey['V8'].apply(find_weekday_ymdhms)
        # Create empty submission times first, fill it later
        bb_df['MULT'] = ''
        bb_df['NAPN'] = bb_survey['QID11#3_1_1_TEXT'].fillna(BLANK_E)
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
        bb_df['NOTE'] = bb_survey['QID19'].fillna(BLANK_E)

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
        bb_df['TIB'] = ''
        bb_df['SE1'] = ''
        bb_df['SE2'] = ''
        # process MULT
        bb_df['MULT'] = self.process_mult(bb_df)
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
        ab_df['NOTE'] = ''

        bt_series = ab_survey['QID2#2_1'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_1'].fillna(MM_ZERO)
        ab_df['BT'] = bt_series.apply(fill_for_hhmm)

        lo_series = ab_survey['QID2#2_2'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_2'].fillna(MM_ZERO)
        ab_df['LO'] = lo_series.apply(fill_for_hhmm)

        wt_series = ab_survey['QID2#2_3'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_3'].fillna(MM_ZERO)
        ab_df['WT'] = wt_series.apply(fill_for_hhmm)

        rt_series = ab_survey['QID2#2_4'].fillna(BLANK_NA) + ":" + ab_survey['QID2#1_4'].fillna(MM_ZERO)
        ab_df['RT'] = rt_series.apply(fill_for_hhmm)

        ab_df['SOL'] = ab_survey['QID3#2_1'].fillna(0).apply(hour_to_mins) + ab_survey['QID3#1_1'].fillna(0).apply(str_to_int)
        ab_df['SNZ'] = ab_survey['QID3#2_2'].fillna(0).apply(hour_to_mins) + ab_survey['QID3#1_2'].fillna(0).apply(str_to_int)
        ab_df['TST'] = ab_survey['QID3#2_3'].fillna(0).apply(hour_to_mins) + ab_survey['QID3#1_3'].fillna(0).apply(str_to_int)
        ab_df['WASON'] = ab_survey['QID6#3_1_1_TEXT'].fillna(BLANK_E)
        ab_df['WASOT'] = ab_survey['QID6#2_1'].fillna(0).apply(hour_to_mins) + ab_survey['QID6#1_1'].fillna(0).apply(str_to_int)
        ab_df['EA'] = ab_survey['QID7#3_1'].apply(fill_for_yesno)
        ab_df['EAT'] = ab_survey['QID7#2_1'].fillna(0).apply(hour_to_mins) + ab_survey['QID7#1_1'].fillna(0).apply(str_to_int)
        ab_df['SQ'] = ab_survey['QID5'].apply(fill_for_rank)
        ab_df['REST'] = ab_survey['QID8'].apply(fill_for_rank)

        calculated_df = DataFrame()
        calculated_df['Date'] = ab_df['Date']
        calculated_df['BT'] = ab_df['BT']
        calculated_df['LO'] = ab_df['LO']
        calculated_df['WT'] = ab_df['WT']
        calculated_df['RT'] = ab_df['RT']
        calculated_df['TST'] = ab_df['TST']
        calculated_df['SOL'] = ab_df['SOL']
        calculated_df['WASOT'] = ab_df['WASOT']
        calculated_df = calculated_df.apply(process_calculated, axis=1)

        ab_df['TIB'] = calculated_df['TIB']
        ab_df['SE1'] = calculated_df['SE1']
        ab_df['SE2'] = calculated_df['SE2']
        # Process MULT
        ab_df['MULT'] = self.process_mult(ab_df)

        # Merge two types of surveys together
        self.survey_new_csv = bb_df.append(ab_df, ignore_index=True)

        # sorting it first
        self.survey_new_csv = self.survey_new_csv.sort(['User', 'Date'], ascending=[1, 1])
        # combine rows based on user date and mult
        for index, row in self.survey_new_csv.iterrows():
            user_id = row['User']
            date = row['Date']
            mult = row['MULT']

            key = '{}'.format(user_id) + '{}'.format(date) + '{}'.format(mult)

            found = self.get_survey_data_from_dict(key)
            if found is None:
                self.set_survey_data_in_dict(key, index)
            else:
                duplicated_df = DataFrame(self.survey_new_csv, index=[index, found])
                # print('------- printing duplicated ---- {}'.format(duplicated))
                self.survey_new_csv.drop([index, found], inplace=True)

                new_combined_df = self.combine_rows(duplicated_df)
                # get the first row. actually there is only one row in the new_combined_df
                s = new_combined_df.xs(0)
                # set last_valid_index of survery_new_csv +1 as the index for new_combined_df
                s.name = self.survey_new_csv.last_valid_index() + 1
                # append it to the end
                self.survey_new_csv = self.survey_new_csv.append(s)

    def create_csv(self):
        """
        create new csv file
        """
        self.survey_new_csv = self.survey_new_csv.sort(['User', 'Date'], ascending=[1, 1])
        self.survey_new_csv.to_csv(self.out_filename, index=False)
        print('--- Finished to create a new csv file.')

    def get_survey_data_from_dict(self, key):
        return self.survey_tmp_dict.get(key)

    def set_survey_data_in_dict(self, key, value):
        self.survey_tmp_dict[key] = value

    def clean_survey_tmp_dict(self):
        self.survey_tmp_dict.clear()

    def process_mult(self, survey_df):
        self.clean_survey_tmp_dict()

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

        note = to_combined_df['NOTE'].fillna('').values
        if note[0] != '':
            tmp_df['NOTE'] = note[0]
        else:
            tmp_df['NOTE'] = note[1]

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
