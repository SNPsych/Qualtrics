from urllib import request, error, parse
import time, datetime
import logging
from sleepvl.settings import SURVEY_DOWNLOADS_DIR, SURVEY_OUTPUT_DIR, SURVEY_FILE_PREFIX, REST_SURVEY_API_URL, REST_API_PARAMS, RSCRIPTS_PATH, \
    PANDOC_PATH, TEX_PATH
from survey.parser.surveyparser import SurveyParser
import subprocess


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
    command = 'PATH="$PATH:' + PANDOC_PATH + ':' + TEX_PATH + '" ' + PANDOC_PATH + '/Rscript ' + RSCRIPTS_PATH + '/commandLocal.R ' + out_file

    print(command)
    subprocess.call(command, shell=True)
