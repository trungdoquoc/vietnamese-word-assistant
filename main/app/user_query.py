from Vietnamese_References.vnese_word_refs import *
import pandas as pd
"""

"""
test_pkl_file = '/Users/trungdoquoc/Desktop/Personal Projects/VNese_assistant/Step_1_Preprocessing/app/extracted_data/vnese_dict_words.pkl'

def word_length_check():
    """
    GOAL: check if input satisfies this conditions:
    type(input) == int && 0 < len(input) < 3
    returns: (int) the correct user input
    """
    validity = False
    word_length = input("Bạn cần tìm từ dài bao nhiêu âm (0 < độ dài < 3): ")

    while (validity == False):

        while True:
            try:
                length_int = int(word_length)
            except:
                print("Độ dài phải là số nguyên.")
                word_length = input("Thử lại: ")
            else:
                break

        if (length_int > 0 and length_int < 3):
            validity = True
        else:
            print("Độ dài từ cần tìm phải lớn hơn 0 và nhỏ hơn 3")
            word_length = input("Thử lại: ")

    return length_int


def helper_van_check():
    """
    GOAL: request an input and check if it is a valid vần:
    returns: (string) a valid van
    """
    input_van = input("Vần (không thanh âm): ").strip()
    #TODO: add 'ANY' if users has no specific condition.
    while input_van not in nguyen_am_don and input_van not in nguyen_am_da:
        input_van = input("Not valid. Vần (không thanh âm): ").strip()
    return input_van

def van_input_check(given_length):

    """
    GOAL: call helper_van_check() to add van into a list
    returns: (list of string) a list of valid vần with len == length_int
    """
    van_list = [''] * given_length
    for i in range(given_length):
        van_list[i] = helper_van_check()
    return van_list

def helper_thanh_check():
    """
    GOAL: request an input and check if it is a valid thanh:
    returns: (string) a valid thanh
    """
    input_thanh = input("Thanh âm (T/B): ").strip()
    while input_thanh not in ['T', 'B']:
        input_thanh = input("Not valid. Thanh âm (T/B): ").strip()
    return input_thanh

def thanH_input_check(given_length):
    thanh_list = [''] * given_length
    for i in range(given_length):
        thanh_list[i] = helper_thanh_check()
    return thanh_list

def main():
    word_db = pd.read_pickle(test_pkl_file)
    still_going = True
    print("Welcome:")

    while (still_going == True):
        print("----------")
        length_int = word_length_check()
        input_van_list = van_input_check(length_int)
        input_thanh_list = thanH_input_check(length_int)

        #First, query thanh:
        if length_int == 1:
            thanh_filtered = word_db.loc[(word_db['Th1'] == input_thanh_list[0]) & (word_db['Số_lượng_tiếng'] == 1)]
            # am_filtered = loc[thanh_filtered['T1'][0] == input_van_list[0]]
        else:
            thanh_filtered = word_db.loc[(word_db['Th1'] == input_thanh_list[0]) & (word_db['Th2'] == input_thanh_list[1]) & (word_db['Số_lượng_tiếng'] == 2)]

        #Then, query am:
        if length_int == 1:
            am_filtered = thanh_filtered.loc[thanh_filtered['T1'] == input_van_list[0]]
        else:
            am_filtered = thanh_filtered.loc[(thanh_filtered['T1'] == input_van_list[0]) & (thanh_filtered['T2'] == input_van_list[1])]

        if len(am_filtered) != 0:
            print("Truy vấn của bạn ra {} kết quả. " .format(len(am_filtered)))
            print(am_filtered)
        else:
            print("Rất tiếc chúng tôi chưa có từ này trong danh sách")
            # print(am_filtered)
        reset = input("Bạn có muốn thử lại? (Y/N): ").strip().lower()
        if reset == 'y':
            continue
        else:
            still_going = False
    return

if __name__ == '__main__':
    main()
