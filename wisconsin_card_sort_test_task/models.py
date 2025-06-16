import os
import ast
import random
import time
from copy import deepcopy
import datetime
from pathlib import Path
import itertools
from itertools import permutations

if os.getenv("USE_LLM_MOCK", "false").lower() == "true":
    from LLM_utils.llm_mock import LLMModels
else:
    from LLM_utils.llm import LLMModels
from LLM_utils.utils.llm_parse import extract_tags

from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
from .wcst_configs import *

author = 'Li Hao'

doc = """
Wisconsin Card Sorting Test (WCST) 
"""


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


class Constants(BaseConstants):
    name_in_url = 'wcst'
    players_per_group = None
    num_rounds = 100


def rotate_list(original_list, k):
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

            self.init_deck_order()
            self.init_all_criteria()
            self.init_rotate_order()

            if self.session.config['use_bot_player']:
                assert (self.session.config['use_multimodal_model'] ^ self.session.config['use_language_model']), \
                    'Use either a multimodal model or a language model'

            if self.session.config['use_multimodal_model']:
                assert self.session.config['save_html_image'], 'When using multimodal models, save HTML image'

            assert self.session.config['criteria_card_num'] == len(self.session.config['criteria_card_list']), \
                'Criteria number does not match number of criteria cards'

        # 去掉并行逻辑，强制所有玩家等待
        # if not self.session.config['use_bot_player']:
        #     group_matrix = []
        #     for i, p in enumerate(self.get_players()):
        #         group_matrix.append([i+1])
        #     self.set_group_matrix(group_matrix)

    def init_deck_order(self):
        if self.session.config['participant_use_same_deck']:

            for i, p in enumerate(self.get_players()):
                p.participant.vars['deck_order'] = wcst_card_list1 + wcst_card_list2
        else:
            all_combinations = list(itertools.product(wcst_color_list, wcst_shape_list, wcst_count_list))
            for i, p in enumerate(self.get_players()):
                new_wcst_card_list1 = [{'color': color, 'shape': shape, 'count': count}
                                       for color, shape, count in all_combinations]
                new_wcst_card_list2 = [{'color': color, 'shape': shape, 'count': count}
                                       for color, shape, count in all_combinations]

                random.shuffle(new_wcst_card_list1)
                random.shuffle(new_wcst_card_list2)
                p.participant.vars['deck_order'] = new_wcst_card_list1 + new_wcst_card_list2

        for i, p in enumerate(self.get_players()):
            p.item_card = str(p.participant.vars['deck_order'][0])
            p.participant.vars['deck_order'].pop(0)

    def init_all_criteria(self):
        if self.session.config['init_criteria'] == 'random':
            for i, p in enumerate(self.get_players()):
                p.current_criteria = random.choice(['color', 'shape', 'count'])
        else:
            for i, p in enumerate(self.get_players()):
                p.current_criteria = self.session.config['init_criteria']

    def init_rotate_order(self):
        for i, p in enumerate(self.get_players()):
            if self.session.config['use_rotate_order']:
                p.participant.vars['choice_order'] = rotate_list(self.session.config['criteria_card_list'], i)
            else:
                p.participant.vars['choice_order'] = list(range(len(self.session.config['criteria_card_list'])))

            p.choice_order = str(p.participant.vars['choice_order'])


class Group(BaseGroup):
    def play_round(self):
        players = self.get_players()
        for p in players:
            # TODO
            choice_order = ast.literal_eval(p.choice_order)
            chosen_card = choice_order[int(p.choice)]

            p.chosen_card = str(chosen_card)
            item_card = ast.literal_eval(p.item_card)

            if item_card[p.current_criteria] == chosen_card[p.current_criteria]:
                p.payoff = 1
                p.correct_in_this_criteria += 1
            else:
                p.payoff = 0

            switch = False
            if p.correct_in_this_criteria == self.session.config['switching_num']:
                switch = True
                criteria_list = self.session.config['criteria_list']
                criteria_list.remove(p.current_criteria)
                p.in_round(self.round_number + 1).current_criteria = random.choice(criteria_list)
                p.in_round(self.round_number + 1).correct_in_this_criteria = 0

            if self.round_number < Constants.num_rounds:
                # TODO: 这里需要注意上面切换，这个的round_number+1数据不对
                item_card = str(p.participant.vars['deck_order'][0])
                p.participant.vars['deck_order'].pop(0)

                p.in_round(self.round_number + 1).item_card = item_card
                p.in_round(self.round_number + 1).choice_order = p.choice_order
                if not switch:
                    p.in_round(self.round_number + 1).current_criteria = p.current_criteria
                    p.in_round(self.round_number + 1).correct_in_this_criteria = p.correct_in_this_criteria

    def judge_end(self):
        if self.round_number >= self.session.config['total_interactions'] or \
                self.round_number == Constants.num_rounds:
            self.session.vars['end_game'] = True


class Player(BasePlayer):
    choice = models.StringField(
        label='你的选择 (You choose)', widget=widgets.RadioSelectHorizontal,
        choices=[
            ['0', '箱子A (Chest A)'],
            ['1', '箱子B (Chest B)'],
            ['2', '箱子C (Chest C)'],
            ['3', '箱子D (Chest D)']])

    current_criteria = models.StringField()
    chosen_card = models.StringField()
    item_card = models.StringField()
    choice_order = models.StringField()
    correct_in_this_criteria = models.IntegerField(default=0)

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

    def remain(self):
        return int(sum([p.payoff for p in self.in_all_rounds()]))

    def get_bot_choice(self):

        model = self.get_bot_model()

        if self.session.config['use_multimodal_model']:
            assert False, 'Not implemented for multimodal model'
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

        tags = extract_tags(response)
        tags = self.check_reasoning_choice_tags(tags, response=response)
        reasoning, choice = tags['reasoning'], tags['choice']
        choice = str(int(choice) - 1)

        to_update_objs = [self]
        to_update_attributes = [
            {'prompt': prompt, 'vlm_response': response, 'reasoning': reasoning, 'choice': choice}]

        return to_update_objs, to_update_attributes

    def get_vlm_bot_understanding(self):
        prev_round_number = self.round_number - 1
        model = self.get_bot_model()
        system_prompt = self.get_system_prompt('./wisconsin_card_sort_test_task/prompt/system_prompt_result.txt')

        file_path = self.get_snapshot_path_by_name(page_name='Results', round_number=prev_round_number)
        image_path_list = [file_path]

        response = model.completion(prompt=system_prompt, image_path_list=image_path_list,
                                    temperature=self.session.config['temperature'], top_p=self.session.config['top_p'],
                                    seed=self.session.config['seed'])

        tags = extract_tags(response)
        tags = self.check_understanding_tags(tags)
        understanding = tags['understanding']

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
            f'./wisconsin_card_sort_test_task/prompt/{self.session.config["system_prompt_file"]}')
        if self.session.config['use_role_play']:
            system_prompt = self.get_role_play_prompt(
                f'./wisconsin_card_sort_test_task/prompt/roles/{self.session.config["role_play_prompt_file"]}') + system_prompt
        prompt = system_prompt + user_prompt

        prompt_replace_data = self.session.config.get('prompt_replace_data', {'circle': 'smiley',
                                 'triangle':'flower',
                                 'crosses': 'dollar',
                                 'star': 'heart'})

        for old, new in prompt_replace_data.items():
            prompt = prompt.replace(old, new)
        for old, new in prompt_replace_data.items():
            system_prompt = system_prompt.replace(old, new)
        for old, new in prompt_replace_data.items():
            user_prompt = user_prompt.replace(old, new)

        return prompt, system_prompt, user_prompt

    def get_multimodal_model_prompt(self):
        user_prompt = self.get_vlm_model_user_prompt()
        system_prompt = self.get_system_prompt('./wisconsin_card_sort_test_task/prompt/system_prompt_choose_vlm.txt')
        if self.session.config['use_role_play']:
            system_prompt = self.get_role_play_prompt(self.session.config['role_play_prompt_path']) + system_prompt
        prompt = system_prompt + user_prompt
        return prompt, system_prompt, user_prompt

    def get_language_model_user_prompt(self):
        if self.session.config["system_prompt_file"] == 'system_prompt_choose.txt':
            begin_user_prompt = (f'Now this is the {self.round_number}th round of the game.\n'
                                 f' {self.describe_symbols(ast.literal_eval(self.item_card), "item")}. Please make your choice.')
            historical_prompt = ('Here is the historical information from the past round(s),'
                                 ' and you may use it as a reference for your following choice.\n')
            # reward_template = (
            #     'In round {round_number}, {choice_attribute}, You chose chest {choice_number}({chest_attribute}). Your reasoning process is {reason}. ' #
            #     'Match Correct.\n'
            # )
            # penalty_template = (
            #     'In round {round_number}, {choice_attribute}, You chose chest {choice_number}({chest_attribute}). Your reasoning process is {reason}. ' #
            #     'Match Failed.\n'
            # )
            reward_template = (
                'In round {round_number}, {choice_attribute}, You chose chest {choice_number}. Your reasoning process is {reason}. ' # 
                'Match Correct.\n'
            )
            penalty_template = (
                'In round {round_number}, {choice_attribute}, You chose chest {choice_number}. Your reasoning process is {reason}. ' # 
                'Match Failed.\n'
            )
            user_prompt = begin_user_prompt
            historical_prompt = historical_prompt

            if self.round_number == 1:
                return user_prompt

            for i in range(1, self.round_number):
                chest_name = ['A', 'B', 'C', 'D']
                if self.in_round(i).payoff == 1:
                    historical_prompt = (historical_prompt + reward_template.format(
                        round_number=i,
                        choice_number=chest_name[int(self.in_round(i).choice)],
                        # str(int(self.in_round(i).choice) + 1),
                        choice_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).item_card), 'item'),
                        # chest_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).chosen_card), f'chest {chest_name[int(self.in_round(i).choice)]}'),
                        reason=self.in_round(i).reasoning,
                    ))
                elif self.in_round(i).payoff == 0:
                    historical_prompt = (historical_prompt + penalty_template.format(
                        round_number=i,
                        choice_number=chest_name[int(self.in_round(i).choice)],
                        # str(int(self.in_round(i).choice) + 1),
                        choice_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).item_card), 'item'),
                        # chest_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).chosen_card), f'chest {chest_name[int(self.in_round(i).choice)]}'),
                        reason=self.in_round(i).reasoning,
                    ))
                else:
                    assert False, 'payoff must be 0 or 1'
                # 这里设置+1是为了把otree的0-3，映射回1-4，非常不优雅，想想怎么改

            user_prompt = historical_prompt + user_prompt  # + f'\n Last round you think: {self.in_round(self.round_number-1).reasoning}'
        elif self.session.config["system_prompt_file"] == 'system_prompt_medicine.txt':
            begin_user_prompt = (f'Now this is the {self.round_number}th round of the game.\n'
                                 f' {self.describe_symbols(ast.literal_eval(self.item_card), "sample")}. Please make your choice.')
            historical_prompt = ('Here is the historical information from the past round(s),'
                                 ' and you may use it as a reference for your following choice.\n')
            reward_template = (
                'In round {round_number}, {choice_attribute}, You chose chest {choice_number}. Your reasoning process is {reason}. '  # 
                'Match Correct.\n'
            )
            penalty_template = (
                'In round {round_number}, {choice_attribute}, You chose chest {choice_number}. Your reasoning process is {reason}. '  # 
                'Match Failed.\n'
            )
            user_prompt = begin_user_prompt
            historical_prompt = historical_prompt

            if self.round_number == 1:
                return user_prompt

            for i in range(1, self.round_number):
                chest_name = ['A', 'B', 'C', 'D']
                if self.in_round(i).payoff == 1:
                    historical_prompt = (historical_prompt + reward_template.format(
                        round_number=i,
                        choice_number=chest_name[int(self.in_round(i).choice)],
                        # str(int(self.in_round(i).choice) + 1),
                        choice_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).item_card), 'sample'),
                        # chest_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).chosen_card), f'chest {chest_name[int(self.in_round(i).choice)]}'),
                        reason=self.in_round(i).reasoning,
                    ))
                elif self.in_round(i).payoff == 0:
                    historical_prompt = (historical_prompt + penalty_template.format(
                        round_number=i,
                        choice_number=chest_name[int(self.in_round(i).choice)],
                        # str(int(self.in_round(i).choice) + 1),
                        choice_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).item_card), 'sample'),
                        # chest_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).chosen_card), f'chest {chest_name[int(self.in_round(i).choice)]}'),
                        reason=self.in_round(i).reasoning,
                    ))
                else:
                    assert False, 'payoff must be 0 or 1'

            user_prompt = historical_prompt + user_prompt  # + f'\n Last round you think: {self.in_round(self.round_number-1).reasoning}'
        elif self.session.config['system_prompt_file'] == 'system_prompt_economics.txt':
            begin_user_prompt = (f'Now this is the {self.round_number}th round of the game.\n'
                                 f' {self.describe_symbols(ast.literal_eval(self.item_card), "asset")}. Please make your choice.')
            historical_prompt = ('Here is the historical information from the past round(s),'
                                 ' and you may use it as a reference for your following choice.\n')
            reward_template = (
                'In round {round_number}, {choice_attribute}, You chose chest {choice_number}. Your reasoning process is {reason}. '  # 
                'Match Correct.\n'
            )
            penalty_template = (
                'In round {round_number}, {choice_attribute}, You chose chest {choice_number}. Your reasoning process is {reason}. '  # 
                'Match Failed.\n'
            )
            user_prompt = begin_user_prompt
            historical_prompt = historical_prompt

            if self.round_number == 1:
                return user_prompt

            for i in range(1, self.round_number):
                chest_name = ['A', 'B', 'C', 'D']
                if self.in_round(i).payoff == 1:
                    historical_prompt = (historical_prompt + reward_template.format(
                        round_number=i,
                        choice_number=chest_name[int(self.in_round(i).choice)],
                        # str(int(self.in_round(i).choice) + 1),
                        choice_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).item_card), 'asset'),
                        # chest_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).chosen_card), f'chest {chest_name[int(self.in_round(i).choice)]}'),
                        reason=self.in_round(i).reasoning,
                    ))
                elif self.in_round(i).payoff == 0:
                    historical_prompt = (historical_prompt + penalty_template.format(
                        round_number=i,
                        choice_number=chest_name[int(self.in_round(i).choice)],
                        # str(int(self.in_round(i).choice) + 1),
                        choice_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).item_card), 'asset'),
                        # chest_attribute=self.describe_symbols(ast.literal_eval(self.in_round(i).chosen_card), f'chest {chest_name[int(self.in_round(i).choice)]}'),
                        reason=self.in_round(i).reasoning,
                    ))
                else:
                    assert False, 'payoff must be 0 or 1'

            user_prompt = historical_prompt + user_prompt  # + f'\n Last round you think: {self.in_round(self.round_number-1).reasoning}'
        else:
            raise FileNotFoundError('no system_prompt_file found')

        return user_prompt

    def get_vlm_model_user_prompt(self):
        assert False
        user_prompt = (f'Your total points so far: {self.remain()} points.\n'
                       f'Now this is the {self.round_number}th round of the game.\n'
                       f'Please make your choice.')

        historical_prompt = ('Here is the historical information from the past round(s),'
                             ' and you may use it as a reference for your following choice.\n')

        if self.round_number == 1:
            return user_prompt

        for i in range(1, self.round_number):
            historical_prompt = (historical_prompt + (
                f'In round {i}, you chose chest number {str(int(self.in_round(i).choice) + 1)}. '
                f'You had seen: "{self.in_round(i).understanding}".\n'))

        user_prompt = historical_prompt + user_prompt

        return user_prompt

    def get_system_prompt(self, path):
        with open(path, 'r') as f:
            system_prompt = f.read()
        system_prompt = system_prompt.replace('<criteria_card_1>', self.describe_symbols(ast.literal_eval(self.choice_order)[0], 'chest').replace('chest', 'chest A'))
        system_prompt = system_prompt.replace('<criteria_card_2>', self.describe_symbols(ast.literal_eval(self.choice_order)[1], 'chest').replace('chest', 'chest B'))
        system_prompt = system_prompt.replace('<criteria_card_3>', self.describe_symbols(ast.literal_eval(self.choice_order)[2], 'chest').replace('chest', 'chest C'))
        system_prompt = system_prompt.replace('<criteria_card_4>', self.describe_symbols(ast.literal_eval(self.choice_order)[3], 'chest').replace('chest', 'chest D'))
        return system_prompt

    def get_role_play_prompt(self, path):
        with open(path, 'r') as f:
            role_play_prompt = f.read()
        return role_play_prompt

    def check_reasoning_choice_tags(self, tags, response=None):
        if 'reasoning' not in tags:
            tags['reasoning'] = ''
            print('Not found reasoning tag.')

        valid_choices = '1234'

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

    def check_understanding_tags(self, tags, response=None):
        if 'understanding' not in tags:
            tags['understanding'] = ''
            print('Not found understanding tag.')
        return tags

    def extract_choice_by_gpt(self, response):
        valid_choices = '1234'

        model = self.subsession.llm_models.llm_models['gpt-3.5']

        system_prompt = ('You are an AI assistant, I will give you a player response and you need to extract the '
                         'player\'s choice. Your response must always present in the following format: '
                         '<choice>Any number between 1-4 indicates your choice of chest</choice>')

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

    def describe_symbols(self, symbol_dict, entity_type="chest"):
        """
        Convert a dictionary describing symbols into a human-readable description
        for either a box or an item.

        Args:
            symbol_dict (dict): A dictionary with keys 'color', 'shape', and 'count'.
            entity_type (str): The type of entity to describe ('box' or 'item').

        Returns:
            str: A formatted string describing the symbols on the entity.
        """
        # Extract values from the dictionary
        color = symbol_dict.get('color', 'unknown color')
        shape = symbol_dict.get('shape', 'unknown shape')
        count = symbol_dict.get('count', 'unknown count')

        # Determine the entity type for description
        entity = entity_type if "chest" in entity_type else "item"

        # Format the description
        description = f"The {entity} has {count} {color} {shape}"

        # Handle pluralization for count
        if isinstance(count, int) and count > 1:
            description = f"The {entity} has {count} {color} {shape}s"
        # description = (f"The {entity}'s symbols: the number of symbols is {count}, "
        #                f"the color of the symbols is {color}, and the type of the symbols is {shape}")

        return description
