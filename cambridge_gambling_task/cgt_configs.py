import random
def shuffle_list(original_list):
    shuffled_list = original_list[:]
    random.shuffle(shuffled_list)
    return shuffled_list

max_player_num = 120
max_repeat_num = 10


box_lst = []
all_choice = [(1, 9), (6, 4), (4, 6), (3, 7), (9, 1), (7, 3), (2, 8), (8, 2)]

for _ in range(max_player_num):
    player_list = []
    for i in range(max_repeat_num):
        player_list.extend(shuffle_list(all_choice))
    box_lst.append(player_list)

player_choice_labels = ['blue boxes, <very_low_bets>% bet.',
                        'blue boxes, <low_bets>% bet.',
                        'blue boxes, <medium_bets>% bet.',
                        'blue boxes, <high_bets>% bet.',
                        'blue boxes, <very_high_bets>% bet.',

                        'red boxes, <very_low_bets>% bet.',
                        'red boxes, <low_bets>% bet.',
                        'red boxes, <medium_bets>% bet.',
                        'red boxes, <high_bets>% bet.',
                        'red boxes, <very_high_bets>% bet.']

player_chinese_choice_labels = ['F <very_low_bets>%',
                                'F <low_bets>%',
                                'F <medium_bets>%',
                                'F <high_bets>%',
                                'F <very_high_bets>%',

                                'J <very_low_bets>%',
                                'J <low_bets>%',
                                'J <medium_bets>%',
                                'J <high_bets>%',
                                'J <very_high_bets>%']

if __name__ == '__main__':
    print(box_lst)
    print(len(box_lst))
    print(len(box_lst[0]))

