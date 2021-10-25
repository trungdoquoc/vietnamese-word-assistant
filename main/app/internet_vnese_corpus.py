# -*- coding: utf-8 -*-
import os
import re
import pandas as pd
import sys
import random
import json
from Vietnamese_References.vnese_word_refs import *

#-------
raw_data_path = './raw_text_data'
destination_path = './extracted_data/processed_text_file'

### WORD HELPER FUNCITON ###
def detect_thanh(tieng):
    """
    Given a single tieng, detect the thanh in it.
    input: string
    returns: tuples (B/T, thanh)

    HINT: a single tieng always has a thanh,
    if no thanh (other than ngang) is found,
    then that tiếng has thanh ngang. Else,
    thanh is the only thanh other than thanh ngang found.
    """
    res = []
    for letter in tieng:
        for k in thanh_dict:
            if letter in thanh_dict[k]:
                res.append(k)
    for r in res:
        if r != 'ngang':
            for k in bang_trac_dict:
                if r in bang_trac_dict[k]:
                    return (k, r)
    return ('B', 'ngang')

def replace_thanh_of_tieng(am):
    """
    For a single âm, detect the letter with thanh
    of that âm, then replace it with that
    letter without thanh.
    input: string (a single am)
    returns: string (âm without thanh)
    """
    for c in am:
        for k in thanh_nguyen_am:
            if c in thanh_nguyen_am[k]:
                am = am.replace(c, k)
    return am

def detect_van(tieng):
    """
    Detect all possible vần in **tieng_ko_dau**
    (both complete and partial vần)
    input: a string
    returns: a list of string
    """
    res = []
    longest_v = ''

    # special case: van = gi:
    # ng. am don:
    if tieng[:2] == 'gi':
        if tieng[2:] == '':
            res.append('i')
        elif tieng[2:] in nguyen_am_don or tieng[2:] in nguyen_am_da:
            res.append(tieng[2:])
        else:
            res.append(tieng[1:])
        return res

    # special case: van = qu:
    if tieng[0] == 'q':
        if tieng[1:] in nguyen_am_da:
            res.append(tieng[1:])
        elif 'o' + tieng[2:] in nguyen_am_da:
            res.append('o' + tieng[2:])
        else:
            res.append(tieng[2:])
        return res

    # special case: âm[0] == y:
    if tieng[0] == 'y':
        if len(tieng) == 1:
            res.append(tieng)
        elif 'i' + tieng[1:] in nguyen_am_da:
            res.append('i' + tieng[1:])
        else:
            print(tieng)
            res.append(tieng)
        return res

    for v in nguyen_am_da:
        if v in tieng:
            if len(v) > len(longest_v):
                longest_v = v
            res.append(v)
    if longest_v != '':
        res = [longest_v]

    if len(res) == 0:
        for v_don in nguyen_am_don:
            if v_don in tieng:
                res.append(v_don)
    return res

def create_cf_dict(csv_path):
    """
    GOAL: Create a look-up dict to convert viết_tắt -> normal format
    input: (string) the .csv path of the file
    returns: (dict) a look-up dict
    """
    vt_csv = pd.read_csv(csv_path, header = 0)
    v_d = {}
    for i in range(len(vt_csv)):
        v_d[vt_csv.iloc[i, 0]] = vt_csv.iloc[i, 2]
    return v_d

def replace_case_folding(am):
    """
    GOAL: replace any c-f(viet tat) string in
    a line with the full representation of that
    phrase.
    input: string (âm), string (csv file path for c-f dict)
    returns: string (full_am)
    """
    if am in cf_dict:
        return cf_dict[am]
    else:
        return

def lowercase_line(input_line):
    """
    GOAL: lowercase every char in input_line
    input: string
    returns: string
    """
    return input_line.lower()

def sub_special_chars_then_number(lwc_line):
    """
    GOAL: Take in lower-cased line, sub special
    chars with ' ', then sub nums with ' '.
    input: string (lower-cased line)
    returns: string (special chars and nums removed)
    """
    rx_s_char = re.compile(r'[!@#$%\^&*()[\]{};:,./<>?|`~\-=_+\\"\'\“\”\…]')
    rx_num = re.compile(r'[0-9]')
    sc_subbed_line = re.sub(rx_s_char, ' ', lwc_line)
    subbed_line = re.sub(rx_num, ' ', sc_subbed_line)
    return subbed_line

def iy_normalization(am):
    """
    GOAL: check if a given am needs
    to be iy-normalized or not
    """
    return

def normalize_am_with_thanh(am_with_thanh):
    """
    GOAL: replace am_with_thanh with
    am_+_thanh_key as a more standardized
    format to run models.

    input: string (am_with_thanh)
    returns: string (am_and_thanh_num)
    Key:
    Value:
    convert âm_with_thanh -> am_and_thanh_num
    eg: thuỷ -> thuy1
    """
    thanh_dieu = ['sac', 'hoi', 'nga', 'nang', 'huyen', 'ngang']
    thanh_num = thanh_dieu.index(detect_thanh(am_with_thanh)[1])
    am = replace_thanh_of_tieng(am_with_thanh)
    if thanh_num != 5:
        return am + str(thanh_num)
    else:
        return am

def complete_line_process(raw_line):
    """
    GOAL: process a given line.
    input: (string) raw line
    returns: (string) processed line and (dict) normalized word in that line
    """
    n_splitted = []
    dict_line = {}
    cf_split = sub_special_chars_then_number(raw_line).split()
    for am in cf_split:
        # Check if am is viet_tat (Case_folding):
        if am.isupper() == True:
            f_am = replace_case_folding(am)
            if f_am != None:
                f_am_split = sub_special_chars_then_number(f_am).split()
                for e in f_am_split:
                    #iy_normed = ...
                    am_and_thanh_num = normalize_am_with_thanh(e).lower()
                    if am_and_thanh_num not in dict_line:
                        dict_line[am_and_thanh_num] = e
                    n_splitted.append(am_and_thanh_num)
            else:
                #iy_normed = ...
                am_and_thanh_num = normalize_am_with_thanh(am).lower()
                if am_and_thanh_num not in dict_line:
                    dict_line[am_and_thanh_num] = am
                n_splitted.append(am_and_thanh_num)
        else:
            #iy_normed = ...
            am_and_thanh_num = normalize_am_with_thanh(am).lower()
            if am_and_thanh_num not in dict_line:
                dict_line[am_and_thanh_num] = am
            n_splitted.append(am_and_thanh_num)

    n_splitted[-1] = n_splitted[-1] + '\n'
    low_r_line = lowercase_line(' '.join(n_splitted))
    return (low_r_line, dict_line)

def update_dict(big_dict, small_dict):
    big_keys = big_dict.keys()
    small_keys = small_dict.keys()

    for s_key in small_keys:
        if s_key not in big_keys:
            big_dict[s_key] = small_dict[s_key]
    return big_dict
#-------

#### BIG FUNCTION ####
def create_new_processed_tf(original_fname):
    """
    GOAL:
    1) Normalize and save text file into a new file for later steps.
    2) While normalizing, generate .json dict to store normalized indiv. từ
    for later translation.
    input: (string) path of raw text file
    returns: (string) path of new processed text file
    """

    # create new empty .txt file:
    processed_fname = 'processed_tf.txt'
    newfile_path = destination_path + '/' + processed_fname
    with open(os.path.join(destination_path, processed_fname), 'w') as fp:
        pass

    # create new normalized text file and .json file
    with open(file_path, mode = 'r') as rf, \
         open(new_file_path, mode = 'w') as wf:
        for r_line in rf:
            n_splitted = []
            cf_split = sub_special_chars_then_number(raw_line).split()
            for am in cf_split:
                # Check if am is viet_tat (Case_folding):
                if am.isupper() == True:
                    f_am = replace_case_folding(am)
                    if f_am != None:
                        f_am_split = sub_special_chars_then_number(f_am).split()
                        for e in f_am_split:
                            #iy_normed = ...
                            am_and_thanh_num = normalize_am_with_thanh(e)
                            n_splitted.append(am_and_thanh_num)
                    else:
                        #iy_normed = ...
                        am_and_thanh_num = normalize_am_with_thanh(am)
                        n_splitted.append(am_and_thanh_num)
                else:
                    #iy_normed = ...
                    am_and_thanh_num = normalize_am_with_thanh(am)
                    n_splitted.append(am_and_thanh_num)

            n_splitted[-1] = n_splitted[-1] + '\n'
            low_r_line = lowercase_line(' '.join(n_splitted))
            wf.write(low_r_line)

    return

#### RUNNING ####
cf_dict = create_cf_dict('./extracted_data/Viet_tat.csv')

def main():
    """
    GOAL: if argv is a text file name in the folder raw_data_path folder,
    process that file only, otherwise process all files in the folder.
    input (optional): (string) name of the specified text file
    returns: None
    """
    normalized_dict = {}
    # CASE 1: if argv is omitted, process all file
    # if argv == '':
    list_all_file = os.listdir(raw_data_path)

    # process each file
    for fname in list_all_file:
        processed_fname = 'processed_' + fname
        og_file_path = raw_data_path + '/' + fname
        newfile_path = destination_path + '/' + processed_fname

        with open(os.path.join(destination_path, processed_fname),'w') as fp:
            pass

        with open(og_file_path, mode = 'r') as rf, \
             open(newfile_path, mode = 'w') as wf:
             for r_line in rf:
                 low_r_line, dict_line = complete_line_process(r_line)
                 wf.write(low_r_line)
                 normalized_dict = update_dict(normalized_dict, dict_line)

    # CASE 2: if argv is a valid file name
    # else:
    #     if argv in os.listdir(raw_data_path):
    #         fname = argv
    #         processed_fname = 'processed_' + fname + '.txt'
    #         og_file_path = raw_data_path + '/' + fname
    #         newfile_path = destination_path + '/' + processed_fname
    #
    #         with open(os.path.join(destination_path, processed_fname),'w') as fp:
    #             pass
    #
    #         with open(og_file_path, mode = 'r') as rf, \
    #              open(newfile_path, mode = 'w') as wf:
    #              for r_line in rf:
    #                  low_r_line, dict_line = complete_line_process(r_line)
    #                  wf.write(low_r_line)
    #                  normalized_dict = update_dict(normalized_dict, dict_line)
        # else:
        #     print('File không tồn tại. Xin thử lại')
        #     return

    json.dump(normalized_dict, open('foobar.txt', 'w'))
    return

if __name__ == '__main__':
    main()
"""
STEPS:
1. caller function:
"""
