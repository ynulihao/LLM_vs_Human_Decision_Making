import os
import random
import time
from copy import deepcopy
import datetime
from pathlib import Path
from itertools import permutations

if os.getenv("USE_LLM_MOCK", "false").lower() == "true":
    from LLM_utils.llm_mock import LLMModels
else:
    from LLM_utils.llm import LLMModels
from LLM_utils.utils.llm_parse import extract_tags

from otree.api import models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
from .igt_configs import *

author = 'Li Hao'

doc = """
Iowa gambling task
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
                [0, "Strongly Agree"],
                [1, "Agree"],
                [2, "Not Sure"],
                [3, "Disagree"],
                [4, "Strongly Disagree"]
            ],
            label=label,
            widget=widgets.RadioSelectHorizontal()
        )


class Constants(BaseConstants):
    name_in_url = 'igt'
    players_per_group = None
    num_rounds = 100


class Subsession(BaseSubsession):
    primary_round = models.IntegerField()
    interaction = models.IntegerField()
    llm_models = LLMModels()

    def creating_session(self):
        if self.round_number == 1:
            # Check config in settings
            self.session.vars['end_game'] = False
            self.session.vars['time_stamp'] = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            self.init_cards_order()
            self.init_cards_penalty_distributions()

            if self.session.config['use_bot_player']:
                assert (self.session.config['use_multimodal_model'] ^ self.session.config['use_language_model']), \
                    'Use either a multimodal model or a language model'

            if self.session.config['use_multimodal_model']:
                assert self.session.config['save_html_image'], 'When using multimodal models, save HTML image'

            assert self.session.config['card_num'] <= len(self.session.config['card_penalty_distributions']), \
                'Card penalty distribution must be less than or equal to number of cards'

            assert self.session.config['card_num'] <= 4, f'Card num {self.session.config["card_num"]} is greater than 4'

        # if not self.session.config['use_bot_player']:
        #     group_matrix = []
        #     for i, p in enumerate(self.get_players()):
        #         group_matrix.append([i+1])
        #     self.set_group_matrix(group_matrix)

    def init_cards_order(self):
        if self.session.config['random_card_order']:
            cards = ["1", "2", "3", "4"]
            all_permutations = list(permutations(cards))
            random.shuffle(all_permutations)

            for i, p in enumerate(self.get_players()):
                p.participant.vars['card_order'] = all_permutations[i % len(all_permutations)]
        else:
            all_permutations = [["1", "2", "3", "4"], ["4", "1", "2", "3"],
                                ["3", "4", "1", "2"], ["2", "3", "4", "1"]]
            for i, p in enumerate(self.get_players()):
                p.participant.vars['card_order'] = all_permutations[i % len(all_permutations)]

    def init_cards_penalty_distributions(self):
        if self.session.config['random_penalty_distribution']:
            for p in self.get_players():
                cards_penalty_distributions = []
                for i in range(len(self.get_players())):
                    new_list = []
                    for _ in range(10):
                        original_list = deepcopy(
                            self.session.config['card_penalty_distributions'][i % self.session.config['card_num']])
                        random.shuffle(original_list)
                        new_list.extend(original_list)
                    cards_penalty_distributions.append(new_list)
                p.participant.vars['cards_penalty_distributions'] = cards_penalty_distributions
        else:
            print('fixed_penalty_distribution')
            assert self.session.config['card_num'] <= 4, (
                'fixed_penalty_distribution only has {} cards'.format(self.session.config['card_num']))

            fixed_cards_rewards = [fixed_card1_rewards, fixed_card2_rewards,
                                   fixed_card3_rewards, fixed_card4_rewards]
            cards_penalty_distributions = []

            for i in range(self.session.config['card_num']):
                cards_penalty_distributions.append(fixed_cards_rewards[i % len(fixed_cards_rewards)])

            for p in self.get_players():
                p.participant.vars['cards_penalty_distributions'] = cards_penalty_distributions


class Group(BaseGroup):
    def play_round(self):
        players = self.get_players()
        for p in players:
            card_choice = p.participant.vars['card_order'][int(p.choice)]
            p.card_num = card_choice
            p.card_order = ' '.join(p.participant.vars['card_order'])

            card_choice_idx = int(card_choice) - 1

            p.reward = int(self.session.config['card_rewards'][card_choice_idx] *
                           self.session.config['reward_scaling_factor'])
            p.penalty = int(p.participant.vars['cards_penalty_distributions'][card_choice_idx][0] *
                            self.session.config['reward_scaling_factor'])

            p.payoff = p.reward - p.penalty
            p.participant.vars['cards_penalty_distributions'][card_choice_idx].pop(0)

    def judge_end(self):
        if self.round_number >= self.session.config['total_interactions'] or \
                self.round_number == Constants.num_rounds:
            self.session.vars['end_game'] = True


class Player(BasePlayer):
    choice = models.StringField(
        label='你的选择 (You choose)', widget=widgets.RadioSelectHorizontal,
        choices=[
            ['0', '宝箱1 (Chest 1)'],
            ['1', '宝箱2 (Chest 2)'],
            ['2', '宝箱3 (Chest 3)'],
            ['3', '宝箱4 (Chest 4)']])

    card_num = models.StringField()
    card_order = models.StringField()

    reward = models.IntegerField(initial=0)
    penalty = models.IntegerField(initial=0)

    prompt = models.StringField()
    reasoning = models.StringField()
    understanding = models.StringField()
    bot_choice_error = models.BooleanField(default=False)
    vlm_response = models.StringField()

    

    final_survey_group_1_q1_choice = make_final_survey_field("I need to frequently make complex decisions", 1)
    final_survey_group_1_q2_choice = make_final_survey_field(
        "I need to evaluate, compare, and weigh the available information to make decisions", 1)
    final_survey_group_1_q3_choice = make_final_survey_field(
        "I often need to engage in extensive thought before making decisions", 1)
    final_survey_group_1_q4_choice = make_final_survey_field(
        "I am capable of discerning better options and making good decisions", 1)

    final_survey_group_2_q1_choice = make_final_survey_field("Involving ambiguous or uncertain information", 1)
    final_survey_group_2_q2_choice = make_final_survey_field(
        "Placing significant time pressure on me, making it hard for me to decide in time", 1)

    final_survey_group_3_q1_choice = make_final_survey_field("Using AI can improve my game score", 1)
    final_survey_group_3_q2_choice = make_final_survey_field("Using AI can help me finish the game faster", 1)
    final_survey_group_3_q3_choice = make_final_survey_field("AI can assist my decision-making during the game", 1)
    final_survey_group_3_q4_choice = make_final_survey_field(
        "AI can make it easier for me to make decisions in the game", 1)

    final_survey_group_4_q1_choice = make_final_survey_field("Let AI play the game for me", 1)
    final_survey_group_4_q2_choice = make_final_survey_field("Let AI assist me in playing the game", 1)

    def remain(self):
        return int(sum([p.payoff for p in self.in_all_rounds()]) + self.session.config['init_money']
                   * self.session.config['reward_scaling_factor'])

    def get_bot_choice(self):

        model = self.get_bot_model()

        if self.session.config['use_multimodal_model']:
            prompt, system_prompt, user_prompt = self.get_multimodal_model_prompt()
            file_path = self.get_snapshot_path_by_name(page_name='ChoosePage', round_number=self.round_number)
            image_path_list = [file_path]

            if self.session.config['vlm_model'] == 'qwen_vl_max':  # 通义千问似乎不允许空图片提交，似乎不支持system prompt  # TODO 待确认
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
            print(response)

        else:
            assert False, 'Unsupported model type'

        tags = extract_tags(response)
        tags = self.check_reasoning_choice_tags(tags, response=response)
        reasoning, choice = tags['reasoning'], tags['choice']
        choice = str(int(choice) - 1)

        to_update_objs = [self]
        to_update_attributes = [{'prompt': prompt, 'vlm_response': response, 'reasoning': reasoning, 'choice': choice}]

        return to_update_objs, to_update_attributes

    def get_vlm_bot_understanding(self):
        prev_round_number = self.round_number - 1
        model = self.get_bot_model()
        system_prompt = self.get_system_prompt('./iowa_gambling_task/prompt/system_prompt_result.txt')

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
            f'./iowa_gambling_task/prompt/{self.session.config["system_prompt_file"]}')
        if self.session.config['use_role_play']:
            system_prompt = self.get_role_play_prompt(
                f'./iowa_gambling_task/prompt/roles/{self.session.config["role_play_prompt_file"]}') + system_prompt
        prompt = system_prompt + user_prompt
        return prompt, system_prompt, user_prompt

    def get_multimodal_model_prompt(self):
        user_prompt = self.get_vlm_model_user_prompt()
        system_prompt = self.get_system_prompt('./iowa_gambling_task/prompt/system_prompt_choose_vlm.txt')
        if self.session.config['use_role_play']:
            system_prompt = self.get_role_play_prompt(self.session.config['role_play_prompt_path']) + system_prompt
        prompt = system_prompt + user_prompt
        return prompt, system_prompt, user_prompt

    def get_language_model_user_prompt(self):
        if self.session.config["system_prompt_file"] == 'system_prompt_choose.txt':
            begin_user_prompt = (f'Your total points so far: {self.remain()} points.\n'
                                   f'Now this is the {self.round_number}th round of the game.\n'
                                   f'Please make your choice.')
            historical_prompt = ('Here is the historical information from the past round(s),'
                             ' and you may use it as a reference for your following choice.\n')
            reward_template = (
                'In round {round_number}, you chose chest number {choice_number}. '
                'You earned {reward} points in rewards.\n'
            )
            reward_penalty_template = (
                'In round {round_number}, you chose chest number {choice_number}. '
                'You earned {reward} points in rewards and received a penalty of {penalty} points.\n'
            )
        elif self.session.config["system_prompt_file"] == 'system_prompt_medicine.txt':
            begin_user_prompt = (f'The patient’s current health status: {self.remain()} points.\n'
                                 f'This is the {self.round_number}th round of treatment.\n'
                                 f'Please select the treatment you wish to administer.')

            historical_prompt = ('Here is the health record from previous treatments.\n'
                                 'You may use this information to guide your next decision.\n')

            reward_template = (
                'In round {round_number}, you administered treatment option {choice_number}. '
                'The patient’s health improved by {reward} points.\n'
            )

            reward_penalty_template = (
                'In round {round_number}, you administered treatment option {choice_number}. '
                'The patient’s health improved by {reward} points but declined by {penalty} points due to adverse effects.\n'
            )
        elif self.session.config['system_prompt_file'] == 'system_prompt_economics.txt':
            begin_user_prompt = (f'Your current balance: {self.remain()} credits.\n'
                                 f'This is the {self.round_number}th round of investments.\n'
                                 f'Please choose your investment option.')

            historical_prompt = ('Here is the financial history from previous rounds,'
                                 ' which you may use as a reference for your next investment decision.\n')

            reward_template = (
                'In round {round_number}, you chose investment option {choice_number}. '
                'You gained {reward} credits in returns.\n'
            )

            reward_penalty_template = (
                'In round {round_number}, you chose investment option {choice_number}. '
                'You gained {reward} credits in returns but incurred a loss of {penalty} credits.\n'
            )
        else:
            raise FileNotFoundError('no system_prompt_file found')

        user_prompt = begin_user_prompt
        historical_prompt = historical_prompt


        if self.round_number == 1:
            return user_prompt

        for i in range(1, self.round_number):
            if self.in_round(i).penalty == 0:
                # historical_prompt = (historical_prompt + (
                #     f'In round {i}, you chose chest number {str(int(self.in_round(i).choice) + 1)}. '
                #     f'You earned {self.in_round(i).reward} points in rewards.\n'))

                historical_prompt = (historical_prompt + reward_template.format(
                    round_number=i,
                    choice_number=str(int(self.in_round(i).choice) + 1),
                    reward=self.in_round(i).reward
                ))
            elif self.in_round(i).penalty > 0:
                # historical_prompt = (historical_prompt + (
                #     f'In round {i}, you chose chest number {str(int(self.in_round(i).choice) + 1)}. '
                #     f'You earned {self.in_round(i).reward} points in rewards and received a penalty of {self.in_round(i).penalty} points.\n'))

                historical_prompt = (historical_prompt + reward_penalty_template.format(
                    round_number=i,
                    choice_number=str(int(self.in_round(i).choice) + 1),
                    reward=self.in_round(i).reward,
                    penalty=self.in_round(i).penalty
                ))
            else:
                assert False, 'penalty must >= 0'

        user_prompt = historical_prompt + user_prompt

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
            # 这里设置+1是为了把otree的0-3，映射回1-4，非常不优雅，想想怎么改

        user_prompt = historical_prompt + user_prompt

        return user_prompt

    def get_system_prompt(self, path):
        with open(path, 'r') as f:
            system_prompt = f.read()

        old_phrase = 'a loan of 2000 points'
        new_phrase = f'a loan of {self.session.config["init_money"] * self.session.config["reward_scaling_factor"]} points'
        system_prompt = system_prompt.replace(old_phrase, new_phrase)

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
