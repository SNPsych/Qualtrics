from urllib import request, error, parse
import time
import datetime
import logging
import subprocess

from sleepvl.settings import SURVEY_DOWNLOADS_DIR, SURVEY_OUTPUT_DIR, SURVEY_FILE_PREFIX, REST_SURVEY_API_URL, REST_API_PARAMS, \
    RSCRIPTS_COMMAND_PATH, R_PATH, R_ENV_PATH, INDEX_HTML_TPL_DIR, SURVEY_REPORT_DIR, SURVEY_LATEST_REPORT_DIR, SURVEY_LATEST_REPORT_INDEX_DIR
from survey.parser.surveyparser import SurveyParser


def survey_rest_call_job():
    print('--- Start to call survey rest api ...')
    start_tm = time.time()
    encoded_api_params = parse.urlencode(REST_API_PARAMS)
    rest_url = REST_SURVEY_API_URL + "?" + encoded_api_params

    stm = datetime.datetime.fromtimestamp(start_tm).strftime('%Y_%m_%d_%H_%M_%S')

    downloand_file_name = SURVEY_DOWNLOADS_DIR + '/sleep_diary_' + stm + '.csv'
    try:
        request.urlretrieve(rest_url, filename=downloand_file_name)
    except error.URLError as e:
        logging.error('Call rest api failed, {}'.format(e.reason))
    # end_tm = time.time()
    # print('-------------> Finished, took %.2f sec' % (end_tm - start_tm))

    in_file = downloand_file_name

    out_file = SURVEY_OUTPUT_DIR + '/' + SURVEY_FILE_PREFIX + '_sleep_diary_' + stm + '.csv'
    surveyParser = SurveyParser(in_file, out_file)
    surveyParser.parse_csv()
    surveyParser.create_csv()

    # command = 'PATH="$PATH:/usr/local/bin:/Library/TeX/Distributions/.DefaultTeX/Contents/Programs/texbin"
    # /usr/local/bin/Rscript /Users/simonyu/MyDev/devworkspace/sleepvl/Rscripts/commandLocal.R ' + out_file
    command = R_ENV_PATH + ' ' + R_PATH + '/Rscript ' + RSCRIPTS_COMMAND_PATH + '/commandLocal.R ' + out_file

    print(command)
    subprocess.call(command, shell=True)

    index_tpl_file = INDEX_HTML_TPL_DIR + '/latest_index.tpl'
    latest_report_index_dir = SURVEY_LATEST_REPORT_INDEX_DIR
    surveyParser.create_html(index_tpl_file, latest_report_index_dir)

    # copy the latest reports into latest reports directory
    today = datetime.datetime.fromtimestamp(start_tm).strftime('%Y-%m-%d')
    surveyParser.copy_latest_reports(SURVEY_REPORT_DIR, SURVEY_LATEST_REPORT_DIR, today)

survey_rest_call_job()
