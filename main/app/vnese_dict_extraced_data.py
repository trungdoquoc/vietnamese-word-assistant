import re
import pandas as pd
import numpy as np
from Vietnamese_References.vnese_word_refs import *

full_fp = '/Users/trungdoquoc/Desktop/Personal Projects/VNese_assistant/VV/vv30K.dict'

def get_word_definition(file_path):
    """
    Extract each word definition (word + meaning) as an element of a list
    input: file_path
    returns: 2-D list
    """
    all_words = [] # 2-D list, each element is (word + meaning)
    with open(file_path) as f:
        new_w = []
        for line in f:
            if line[0] == '@':
                new_w.append(line.strip('@').strip('\n'))
            elif line == '\n':
                all_words.append(new_w)
                new_w = []
            else:
                new_w.append(line.strip('\n'))
        all_words.append(new_w) # append the last word in the dictionary
    return all_words

def create_dict_from_wlist(word_list):
    # create a dict, key: the word, value: meaning
    # input: 2-D word_list --> output: word dict
    new_dict = {}
    for word in word_list:
        meaning = ''
        for e in range(1, len(word)):
            if e != len(word)-1:
                meaning = meaning + word[e] + '\n'
            else:
                meaning = meaning + word[e]
        new_dict[word[0]] = meaning
    return new_dict


# -- Part 1: Detect thanh in a word --
def split_word_to_tieng(word):
    """
    take a word, split it as a list of tieng
    input: a string of word
    returns: a list of 'clean' tieng
    """
    char_list = ['.', ',']

    tieng_list = word.lower().replace('-', ' ').replace('.', ' ').replace(',', ' ').split()
    return tieng_list

def detect_thanh(tieng):
    """
    Given a single tiếng, detect the thanh in it.
    input: string | output: string (B or T)

    HINT: a single tiếng always has a thanh,
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
                    return k
    return 'B'

# -- Part 2: Detect vần in a word --
def replace_thanh_of_tieng_am(am):
    """
    GOAL: Given a single âm, detect the letter with thanh
    , replace it with that letter without thanh.
    """
    for c in am:
        for k in thanh_nguyen_am:
            if c in thanh_nguyen_am[k]:
                am = am.replace(c, k)
    return am

def replace_thanh_of_tieng_list(list_tieng_w_thanh):
    """
    For a list of tieng, detect the letter with thanh
    in each tiếng element, then replace that letter with that
    letter without thanh.
    input: a list of tiếng in a word
    returns: a list of tiếng, each tiếng is without thanh
    """
    list_tieng_wo_thanh = [''] * len(list_tieng_w_thanh)

    for t in range(len(list_tieng_w_thanh)):
        tieng = list_tieng_w_thanh[t]
        for c in tieng:
            for k in thanh_nguyen_am:
                if c in thanh_nguyen_am[k]:
                    tieng = tieng.replace(c, k)
        list_tieng_wo_thanh[t] = tieng
    return list_tieng_wo_thanh

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
        return res[0]

    # special case: van = qu:
    if tieng[0] == 'q':
        if tieng[1:] in nguyen_am_da:
            res.append(tieng[1:])
        elif 'o' + tieng[2:] in nguyen_am_da:
            res.append('o' + tieng[2:])
        else:
            res.append(tieng[2:])
        return res[0]

    # special case: âm[0] == y:
    if tieng[0] == 'y':
        if len(tieng) == 1:
            res.append(tieng)
        elif 'i' + tieng[1:] in nguyen_am_da:
            res.append('i' + tieng[1:])
        else:
            res.append(tieng)
        return res[0]

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
        if len(res) > 1:
            return res[-1]
        elif len(res) == 0:
            return ''
    return res[0]

def main():
    word_2d_list = get_word_definition(full_fp)
    word_dict = create_dict_from_wlist(word_2d_list)

# Create new DataFrame
    word_df = pd.DataFrame.from_dict(data = word_dict, orient = 'index', dtype = str)
    word_df.columns = ['Word_Meaning']
    word_df.index.name = 'Word'

    # Số lượng tiếng
    word_df['Số_lượng_tiếng'] = ''
    for w in word_df.index:
        n_w = w.replace('-', ' ')
        l = len(n_w.split())
        word_df.at[w, 'Số_lượng_tiếng'] = l

    #New column for Thanh and Van
    df_thanh_cols = ['Th1', 'Th2', 'Th3', 'Th4']
    df_van_cols = ['T1', 'T2', 'T3', 'T4']

    for c in df_thanh_cols:
        word_df[c] = ''

    for c in df_van_cols:
        word_df[c] = ''

    valid_word = word_df.loc[word_df['Số_lượng_tiếng'] <= 4]

# Fill thanh + vần data into valid_word DataFrame
    for w in valid_word.index:
        formatted_w_1 = split_word_to_tieng(w) #split into a list of tiếng
        formatted_w_2 = replace_thanh_of_tieng_list(split_word_to_tieng(w))

        if len(formatted_w_1) != len(formatted_w_2):
            print("ERROR ERROR!")
        else:
            while len(formatted_w_1) < 4:
                formatted_w_1.append('')

            while len(formatted_w_2) < 4:
                formatted_w_2.append('')

            thanh_res = [''] * len(formatted_w_1)
            van_res = [''] * len(formatted_w_2)

            for t in range(len(formatted_w_1)):
                if formatted_w_1[t] != '' and formatted_w_2[t] != '':
                    thanh_res[t] = detect_thanh(formatted_w_1[t])
                    van_res[t] = detect_van(formatted_w_2[t])

            for c in range(len(df_thanh_cols)):
                valid_word.at[w, df_thanh_cols[c]] = thanh_res[c]

            for c in range(len(df_van_cols)):
                valid_word.at[w, df_van_cols[c]] = van_res[c]

    print(valid_word)

    valid_word.to_pickle("./extracted_data/vnese_dict_words.pkl")
    valid_word.to_csv("./extracted_data/vnese_dict_words.csv")
    return

if __name__ == '__main__':
    main()
