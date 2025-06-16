import os
import random
import time
from copy import deepcopy
import datetime
from pathlib import Path
from itertools import permutations

from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer

if os.getenv("USE_LLM_MOCK", "false").lower() == "true":
    from LLM_utils.llm_mock import LLMModels
else:
    from LLM_utils.llm import LLMModels
from LLM_utils.utils.llm_parse import extract_tags

from .cgt_configs import *

author = 'Li Hao'

doc = """
Cambridge Gambling Task (CGT)
"""

default_conf_in_settings = None


class Constants(BaseConstants):
    app_name = 'cambridge_gambling_task'
    name_in_url = 'cgt'
    players_per_group = None
    num_rounds = 100
    choice_num = 10
    box_num = 10


player_choices = list(range(Constants.choice_num))


def make_final_survey_field(label, type):
    if type == 0:
        return models.IntegerField(
            choices=[
                [0, '策略A'],
                [1, '策略B']
            ],
            label=label,
            widget=widgets.RadioSelectHorizontal()
        )
    elif type == 1:
        return models.IntegerField(
            choices=[
                [0, "非常同意"],
                [1, "同意"],
                [2, "不确定"],
                [3, "不同意"],
                [4, "非常不同意"]
            ],
            label=label,
            widget=widgets.RadioSelectHorizontal()
        )


def decimal_to_percentage(decimal_number):
    """
    Convert a decimal number to a percentage and retain only the integer part.

    Args:
    decimal_number (float): The decimal number to convert.

    Returns:
    int: The integer part of the percentage.
    """
    percentage = decimal_number * 100
    return int(percentage)

def rotate_list(k):
    original_list = list(range(Constants.choice_num))
    k = k % len(original_list)
    return original_list[-k:] + original_list[:-k]


class Subsession(BaseSubsession):
    primary_round = models.IntegerField()
    interaction = models.IntegerField()
    llm_models = LLMModels()

    def creating_session(self):
        if self.round_number == 1:
            # Check config in settings
            self.session.vars['end_game'] = False
            self.session.vars['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            assert self.session.config['total_interactions'] % self.session.config['round_interactions'] == 0, \
                "Round number must be multiple of total interactions"

            if self.session.config['use_bot_player']:
                assert (self.session.config['use_multimodal_model'] ^ self.session.config['use_language_model']), \
                    'Use either a multimodal model or a language model'

            if self.session.config['use_multimodal_model']:
                assert self.session.config['save_html_image'], 'When using multimodal models, save HTML image'

            for i, p in enumerate(self.get_players()):
                if self.session.config['use_rotate_order']:
                    p.participant.vars['choice_order'] = rotate_list(i)
                else:
                    p.participant.vars['choice_order'] = list(range(Constants.choice_num))

                p.choice_order = str(p.participant.vars['choice_order'])

        if self.round_number <= self.session.config['total_interactions']:
            for i, p in enumerate(self.get_players()):
                p.box_color_distri = str(box_lst[i][self.round_number-1])

    # if not self.session.config['use_bot_player']:
    #     group_matrix = []
    #     for i, p in enumerate(self.get_players()):
    #         group_matrix.append([i+1])
    #     self.set_group_matrix(group_matrix)


class Group(BaseGroup):
    def play_round(self):
        players = self.get_players()

        for p in players:
            choice_true = p.participant.vars['choice_order'][p.choice]
            if self.session.config['use_oracle_player']:
                assert not self.session.config['use_bot_player'], 'use_oracle_player and use_bot_player cannot be both True'
                box_color_distri = eval(p.box_color_distri)
                if box_color_distri[0] >= box_color_distri[1]:
                    choice_true = 4
                else:
                    choice_true = 9
            
            box_color_distri = eval(p.box_color_distri)

            token_box_id = random.randint(1, Constants.box_num)
            token_color = 'blue' if token_box_id <= box_color_distri[0] else 'red'
            choose_color = 'blue' if choice_true < 5 else 'red'

            if choice_true in [0, 5]:
                payoff = p.remain_by_round_interactions() * self.session.config['bets'][0]
                choice_percent = decimal_to_percentage(self.session.config['bets'][0])
            elif choice_true in [1, 6]:
                payoff = p.remain_by_round_interactions() * self.session.config['bets'][1]
                choice_percent = decimal_to_percentage(self.session.config['bets'][1])
            elif choice_true in [2, 7]:
                payoff = p.remain_by_round_interactions() * self.session.config['bets'][2]
                choice_percent = decimal_to_percentage(self.session.config['bets'][2])
            elif choice_true in [3, 8]:
                payoff = p.remain_by_round_interactions() * self.session.config['bets'][3]
                choice_percent = decimal_to_percentage(self.session.config['bets'][3])
            elif choice_true in [4, 9]:
                payoff = p.remain_by_round_interactions() * self.session.config['bets'][4]
                choice_percent = decimal_to_percentage(self.session.config['bets'][4])
            else:
                assert False, 'Invalid choice'

            payoff = round(payoff)

            if choose_color != token_color:
                payoff *= -1

            p.payoff = payoff
            p.choice_true = choice_true

            p.choice_color = choose_color
            p.choice_percent = choice_percent

            p.token_color = token_color
            p.token_box_id = token_box_id

            # p.box_color_distri = str(box_color_distri)
            p.major_color = 'blue' if box_color_distri[0] >= box_color_distri[1] else 'red'

            p.total_payoff_so_far = p.remain_by_round_interactions()

    def judge_end(self):
        if self.round_number >= self.session.config['total_interactions'] or \
                self.round_number == Constants.num_rounds:
            self.session.vars['end_game'] = True


class Player(BasePlayer):
    choice = models.IntegerField(
        label='你的选择 (You choose)', widget=widgets.RadioSelectHorizontal,
        choices=player_choices)
    choice_true = models.IntegerField()
    choice_order = models.StringField()

    choice_color = models.StringField()
    choice_percent = models.IntegerField()

    major_color = models.StringField()
    box_color_distri = models.StringField()

    token_color = models.StringField()
    token_box_id = models.IntegerField()

    total_payoff_so_far = models.IntegerField()

    prompt = models.StringField()
    reasoning = models.StringField()
    understanding = models.StringField()
    bot_choice_error = models.BooleanField(default=False)
    vlm_response = models.StringField()


    # Questions in FinalSurvey1.html
    final_survey_group_1_q1_choice = make_final_survey_field("我需要经常做出复杂的决策", 1)
    final_survey_group_1_q2_choice = make_final_survey_field("我需要评估，比较，和权衡已有信息做出决策", 1)
    final_survey_group_1_q3_choice = make_final_survey_field("我需要经常进行大量思考才能做出决策", 1)
    final_survey_group_1_q4_choice = make_final_survey_field("我能够分辨更好的选项并做出好的决策", 1)

    final_survey_group_2_q1_choice = make_final_survey_field("包含模棱两可或不确定的信息", 1)
    final_survey_group_2_q2_choice = make_final_survey_field("带给我很大的时间压力，使我来不及进行决策", 1)

    final_survey_group_3_q1_choice = make_final_survey_field("使用人工智能可以提高我的游戏得分", 1)
    final_survey_group_3_q2_choice = make_final_survey_field("使用人工智能可以让我更快地完成游戏", 1)
    final_survey_group_3_q3_choice = make_final_survey_field("人工智能在游戏中可以对我的决策起到辅助作用", 1)
    final_survey_group_3_q4_choice = make_final_survey_field("人工智能可以使我更容易在游戏中做决策", 1)

    final_survey_group_4_q1_choice = make_final_survey_field("让人工智能替代我进行游戏", 1)
    final_survey_group_4_q2_choice = make_final_survey_field("让人工智能辅助我进行游戏", 1)

    def remain_by_round_interactions(self):
        begin_round = ((self.round_number-1) // self.session.config['round_interactions']) * self.session.config['round_interactions'] + 1
        end_round = begin_round + self.session.config['round_interactions'] - 1

        return int(sum([p.payoff for p in self.in_rounds(begin_round, end_round)]) + self.session.config['init_money']
                   * self.session.config['reward_scaling_factor'])

    def remain(self):
        return int(sum([p.payoff for p in self.in_all_rounds()]) + self.session.config['init_money']
                   * self.session.config['reward_scaling_factor'] * (self.session.config['total_interactions'] // self.session.config['round_interactions']))

    def get_bot_choice(self):

        model = self.get_bot_model()

        if self.session.config['use_multimodal_model']:
            prompt, system_prompt, user_prompt = self.get_multimodal_model_prompt()
            file_path = self.get_snapshot_path_by_name(page_name='ChoosePage', round_number=self.round_number)
            image_path_list = [file_path]

            if self.session.config['vlm_model'] == 'qwen_vl_max':
                response = model.completion(prompt=prompt, image_path_list=image_path_list,
                                            temperature=self.session.config['temperature'],
                                            top_p=self.session.config['top_p'], seed=self.session.config['seed'])
            else:
                response = model.completion(system_prompt=system_prompt, prompt=user_prompt,
                                            image_path_list=image_path_list,
                                            temperature=self.session.config['temperature'],
                                            top_p=self.session.config['top_p'], seed=self.session.config['seed'])
        elif self.session.config['use_language_model']:
            prompt, system_prompt, user_prompt = self.get_language_model_prompt()
            response = model.completion(system_prompt=system_prompt, prompt=user_prompt,
                                        temperature=self.session.config['temperature'],
                                        top_p=self.session.config['top_p'], seed=self.session.config['seed'])

        else:
            assert False, 'Unsupported model type'

        # reasoning, choice = extract_content_reasoning_choice(response)  # $3, $4
        tags = extract_tags(response)
        tags = self.check_reasoning_choice_tags(tags, response)
        reasoning, choice = tags['reasoning'], tags['choice']
        choice = int(choice)  # 别骂，为了符合otree表单，所以改了一下

        to_update_objs = [self]
        to_update_attributes = [{'prompt': prompt, 'vlm_response': response, 'reasoning': reasoning, 'choice': choice}]

        return to_update_objs, to_update_attributes

    def get_vlm_bot_understanding(self):
        prev_round_number = self.round_number - 1
        model = self.get_bot_model()
        system_prompt = self.get_system_prompt(f'./{Constants.app_name}/prompt/system_prompt_result.txt')

        file_path = self.get_snapshot_path_by_name(page_name='Results', round_number=prev_round_number)
        image_path_list = [file_path]

        response = model.completion(prompt=system_prompt, image_path_list=image_path_list,
                                    temperature=self.session.config['temperature'], top_p=self.session.config['top_p'],
                                    seed=self.session.config['seed'])

        tags = extract_tags(response)
        tags = self.check_understanding_tags(tags)
        understanding = tags['understanding']
        # understanding = extract_content_understanding(response)  # $1

        to_update_objs = [self.in_round(prev_round_number)]
        to_update_attributes = [{'understanding': understanding}]

        return to_update_objs, to_update_attributes

    def get_snapshot_path_by_name(self, page_name, round_number):
        st = self.session.vars['time_stamp']
        root_path = Path(
            self.subsession.get_folder_name()) / 'logs' / f'{st}_{self.session.code}' / self.participant.code / f'{page_name}'
        file_path = root_path / 'image' / f'{round_number}.png'

        check_count = 0
        out_time_sec = 30
        while not file_path.exists():
            time.sleep(1)
            check_count += 1
            if check_count > out_time_sec:
                assert False, f'Error in screenshot function， {out_time_sec} sec cannot find {page_name} image.'
        return file_path

    def get_bot_model(self):
        model = None

        if self.session.config['use_language_model']:
            if self.session.config['language_model'] in self.subsession.llm_models.llm_models:
                model = self.subsession.llm_models.llm_models[self.session.config['language_model']]
            else:
                assert False, '{} not implemented yet'.format(self.session.config['language_model'])

        if self.session.config['use_multimodal_model']:
            if self.session.config['vlm_model'] in self.subsession.llm_models.llm_models:
                model = self.subsession.llm_models.llm_models[self.session.config['vlm_model']]
            else:
                assert False, '{} not implemented yet'.format(self.session.config['vlm_model'])

        return model

    def get_language_model_prompt(self):
        user_prompt = self.get_language_model_user_prompt()
        system_prompt = self.get_system_prompt(
            f'./{Constants.app_name}/prompt/{self.session.config["system_prompt_file"]}')
        if self.session.config['use_role_play']:
            system_prompt = self.get_role_play_prompt(
                f'./{Constants.app_name}/prompt/roles/{self.session.config["role_play_prompt_file"]}') + system_prompt
        prompt = system_prompt + user_prompt
        return prompt, system_prompt, user_prompt

    def get_multimodal_model_prompt(self):
        user_prompt = self.get_vlm_model_user_prompt()
        system_prompt = self.get_system_prompt(f'./{Constants.app_name}/prompt/system_prompt_choose_vlm.txt')  # TODO
        if self.session.config['use_role_play']:
            system_prompt = self.get_role_play_prompt(self.session.config['role_play_prompt_path']) + system_prompt
        prompt = system_prompt + user_prompt
        return prompt, system_prompt, user_prompt

    def get_language_model_user_prompt(self):
        if self.session.config["system_prompt_file"] == 'system_prompt_choose.txt':
            blue_boxes = int(eval(self.box_color_distri)[0])
            red_boxes = int(eval(self.box_color_distri)[1])

            user_prompt = (f'Your total points in this phase so far: {self.remain_by_round_interactions()} points.\n'
                           f'Now this is the {self.round_number}th round of the game.\n In front of you are {blue_boxes} Type F chest(s) and {red_boxes} Type J chest(s). '
                           f'Please make your choice.')

            historical_prompt = ('Here is the historical information from the past round(s),'
                                 ' and you may use it as a reference for your following choice.\n')

            if self.round_number == 1:
                return user_prompt

            for i in range(1, self.round_number):
                choose_color = self.in_round(i).choice_color
                token_color = self.in_round(i).token_color

                if choose_color == 'blue':
                    choose_color = 'Type F'
                else:
                    choose_color = 'Type J'

                if token_color == 'blue':
                    token_color = 'Type F'
                else:
                    token_color = 'Type J'

                historical_prompt = historical_prompt + f'In round {i}, you chose the {choose_color} chest and bet {self.in_round(i).choice_percent}%.\n'

                if self.in_round(i).payoff > 0:
                    historical_prompt = historical_prompt + (
                        f'Fortunately, the coin was hidden under the {token_color} chest, '
                        f'and You earned {float(self.in_round(i).payoff)} points in rewards.\n')
                else:
                    historical_prompt = historical_prompt + (
                        f'Unfortunately, the coin was hidden under the {token_color} chest, '
                        f'and you received {float(self.in_round(i).payoff)} points as a penalty.\n')

            user_prompt = historical_prompt + user_prompt

            return user_prompt
        elif self.session.config["system_prompt_file"] == 'system_prompt_medicine.txt':
            blue_boxes = int(eval(self.box_color_distri)[0])
            red_boxes = int(eval(self.box_color_distri)[1])

            # Modification: Changed "game" to "diagnostic simulation" and "medication(s)" to "diagnostic test(s)"
            user_prompt = (f'Your total points in this phase so far: {self.remain_by_round_interactions()} points.\n'
                           f'Now this is the {self.round_number}th round of the diagnostic simulation.\n'  # modified text here
                           f'In front of you are {blue_boxes} Type F diagnostic test(s) and {red_boxes} Type J diagnostic test(s). '  # modified text here
                           f'Please make your choice.')

            # Modification: Updated historical prompt to reflect the diagnostic simulation context
            historical_prompt = (
                'Here is the historical information from the past round(s) of the diagnostic simulation,'
                ' which you may use as a reference for your subsequent decision-making.\n')  # modified text here

            if self.round_number == 1:
                return user_prompt

            for i in range(1, self.round_number):
                choose_color = self.in_round(i).choice_color
                token_color = self.in_round(i).token_color

                if choose_color == 'blue':
                    choose_color = 'Type F'
                else:
                    choose_color = 'Type J'

                if token_color == 'blue':
                    token_color = 'Type F'
                else:
                    token_color = 'Type J'

                # Modification: Changed "chose" to "selected", "medication" to "diagnostic test", and "bet" to "allocated ... of your points"
                historical_prompt = historical_prompt + f'In round {i}, you selected the {choose_color} diagnostic test and allocated {self.in_round(i).choice_percent}% of your points.\n'  # modified text here

                if self.in_round(i).payoff > 0:
                    historical_prompt = historical_prompt + (
                        # Modification: Changed "coin was hidden under the {token_color} chest" to "critical biomarker was detected in a {token_color} diagnostic test"
                        f'Fortunately, the critical biomarker was detected in a {token_color} diagnostic test, '  # modified text here
                        # Modification: Changed "You earned" to "you earned" (to keep consistent tone)
                        f'and you earned {float(self.in_round(i).payoff)} points in rewards.\n')  # modified text here
                else:
                    historical_prompt = historical_prompt + (
                        # Modification: Changed "coin was hidden under the {token_color} chest" to "critical biomarker was not detected in the {token_color} diagnostic test"
                        f'Unfortunately, the critical biomarker was not detected in the {token_color} diagnostic test, '  # modified text here
                        # Modification: Changed "you received {points} points as a penalty" to "you incurred a penalty of {points} points"
                        f'and you incurred a penalty of {float(self.in_round(i).payoff)} points.\n')  # modified text here

            user_prompt = historical_prompt + user_prompt

            return user_prompt
        elif self.session.config['system_prompt_file'] == 'system_prompt_economics.txt':
            blue_boxes = int(eval(self.box_color_distri)[0])
            red_boxes = int(eval(self.box_color_distri)[1])

            user_prompt = (f'Your total points in this period so far: {self.remain_by_round_interactions()} points.\n'
                           f'Now this is the {self.round_number}th round of the game.\n In front of you are {blue_boxes} Sector F opportunities and {red_boxes} Sector J opportunities. '
                           f'Please make your choice.')

            historical_prompt = ('Here is the historical information from the past round(s),'
                                 ' and you may use it as a reference for your following choice.\n')

            if self.round_number == 1:
                return user_prompt

            for i in range(1, self.round_number):
                choose_color = self.in_round(i).choice_color
                token_color = self.in_round(i).token_color

                if choose_color == 'blue':
                    choose_color = 'Sector F'
                else:
                    choose_color = 'Sector J'

                if token_color == 'blue':
                    token_color = 'Sector F'
                else:
                    token_color = 'Sector J'

                historical_prompt = historical_prompt + f'In round {i}, you chose the {choose_color} sector and invest {self.in_round(i).choice_percent}%.\n'

                if self.in_round(i).payoff > 0:
                    historical_prompt = historical_prompt + (
                        f'Fortunately, the substantial returns was hidden under the {token_color} sector, '
                        f'and You earned {float(self.in_round(i).payoff)} points in rewards.\n')
                else:
                    historical_prompt = historical_prompt + (
                        f'Unfortunately, the substantial returns was hidden under the {token_color} sector, '
                        f'and you received {float(self.in_round(i).payoff)} points as a penalty.\n')

            user_prompt = historical_prompt + user_prompt

            return user_prompt
        else:
            raise FileNotFoundError('no system_prompt_file found')

    def get_vlm_model_user_prompt(self):
        raise NotImplementedError('GCT vlm prompt not implemented yet')

    def get_system_prompt(self, path):
        def replace_with_error(string, old, new):
            if old not in string:
                raise ValueError(f"The substring '{old}' was not found in the given string.")
            return string.replace(old, new)

        with open(path, 'r') as f:
            system_prompt = f.read()

        replace_data = {}
        for i in range(Constants.choice_num):

            replace_data[f'<map_{i}>'] = player_chinese_choice_labels[self.participant.vars['choice_order'][i]]

        for key, value in replace_data.items():
            old_phrase, new_phrase = key, str(value)
            system_prompt = replace_with_error(system_prompt, old_phrase, new_phrase)

        replace_data = {
            '<init_money>': self.session.config['init_money'] * self.session.config["reward_scaling_factor"],
            '<round_interactions>': self.session.config['round_interactions'],

            '<very_low_bets>': decimal_to_percentage(self.session.config['bets'][0]),
            '<low_bets>': decimal_to_percentage(self.session.config['bets'][1]),
            '<medium_bets>': decimal_to_percentage(self.session.config['bets'][2]),
            '<high_bets>': decimal_to_percentage(self.session.config['bets'][3]),
            '<very_high_bets>': decimal_to_percentage(self.session.config['bets'][4]),
        }

        for key, value in replace_data.items():
            old_phrase, new_phrase = key, str(value)
            system_prompt = replace_with_error(system_prompt, old_phrase, new_phrase)

        return system_prompt

    def get_role_play_prompt(self, path):
        with open(path, 'r') as f:
            role_play_prompt = f.read()
        return role_play_prompt

    def check_reasoning_choice_tags(self, tags, response=None):
        if 'reasoning' not in tags:
            tags['reasoning'] = ''
            print('Not found reasoning tag.')

        valid_choices = map(str, list(range(0, Constants.choice_num)))

        if ('choice' in tags) and (tags['choice'] not in valid_choices):
            if len(tags['choice']) == 1:
                tags['choice'] = random.choice(valid_choices)
                self.bot_choice_error = True
                print('Invalid choice tag.')
            else:
                print(tags['choice'])
                tags.pop('choice')

        if 'choice' not in tags:
            tags['choice'] = self.extract_choice_by_gpt(response)
            self.bot_choice_error = True
            print('Not found choice tag.')

        return tags

    def check_understanding_tags(self, tags):
        if 'understanding' not in tags:
            tags['understanding'] = ''
            print('Not found understanding tag.')
        return tags

    def extract_choice_by_gpt(self, response):
        valid_choices = ''.join(map(str, list(range(0, Constants.choice_num))))

        model = self.subsession.llm_models.llm_models['gpt-3.5']

        system_prompt = ('You are an AI assistant, I will give you a player response and you need to extract the '
                         'player\'s choice. Your response must always present in the following format: '
                         '<choice>Any number between 0-9 indicates your choice</choice>')

        response = model.completion(system_prompt=system_prompt, prompt=response,
                                    temperature=self.session.config['temperature'],
                                    top_p=self.session.config['top_p'], seed=self.session.config['seed'])
        tags = extract_tags(response)

        if ('choice' not in tags) or (tags.get('choice', -1) not in valid_choices):
            tags['choice'] = random.choice(valid_choices)
            print('gpt 3.5 extract choice error.')
        else:
            print('gpt 3.5 extract choice success.')

        return tags['choice']

