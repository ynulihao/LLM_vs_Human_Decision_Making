import time
import random
from pathlib import Path

from .models import Constants
from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage, PageSaveHTML
from otree_utils.screenshot import capture_html_to_image

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, TimeoutError
from .cgt_configs import *


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


class PreIntroduction(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'debug': self.session.config.get('debug', False),
            'lang': self.session.config.get('lang', 'en')
        }


class Introduction(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'round_interactions': self.session.config.get('round_interactions', 8),
            'init_money': self.session.config.get('init_money', 100) * self.session.config.get('reward_scaling_factor', 1),
            'very_low_bets': decimal_to_percentage(self.session.config['bets'][0]),
            'low_bets': decimal_to_percentage(self.session.config['bets'][1]),
            'medium_bets': decimal_to_percentage(self.session.config['bets'][2]),
            'high_bets': decimal_to_percentage(self.session.config['bets'][3]),
            'very_high_bets': decimal_to_percentage(self.session.config['bets'][4]),

            'debug': self.session.config.get('debug', False),
            'lang': self.session.config.get('lang', 'en'),
        }


class ChoosePage(PageSaveHTML):
    form_model = 'player'
    form_fields = ['choice']

    def get_timeout_seconds(self):
        return self.session.config['timeout_seconds']

    def vars_for_template(self):
        choice_labels = []
        for choice in self.player.participant.vars['choice_order']:
            raw_label = player_chinese_choice_labels[choice]
            if '<very_low_bets>' in raw_label:
                raw_label = raw_label.replace('<very_low_bets>', str(decimal_to_percentage(self.session.config['bets'][0])))
            elif '<low_bets>' in raw_label:
                raw_label = raw_label.replace('<low_bets>', str(decimal_to_percentage(self.session.config['bets'][1])))
            elif '<medium_bets>' in raw_label:
                raw_label = raw_label.replace('<medium_bets>', str(decimal_to_percentage(self.session.config['bets'][2])))
            elif '<high_bets>' in raw_label:
                raw_label = raw_label.replace('<high_bets>', str(decimal_to_percentage(self.session.config['bets'][3])))
            elif '<very_high_bets>' in raw_label:
                raw_label = raw_label.replace('<very_high_bets>', str(decimal_to_percentage(self.session.config['bets'][4])))
            else:
                assert False, 'Unknown choice label'
            choice_labels.append(raw_label)

        return {
            'round': self.subsession.round_number,
            'debug': self.session.config.get('debug', True),
            'lang': self.session.config.get('lang', 'en'),

            'choice_labels': choice_labels,
            'remain_by_sub': self.player.remain_by_round_interactions(),

            'box_color_distri': eval(self.player.box_color_distri),
            'box_blue_list': list(range(eval(self.player.box_color_distri)[0])),
            'box_red_list': list(range(eval(self.player.box_color_distri)[1])),

            'very_low_bets': decimal_to_percentage(self.session.config['bets'][0]),
            'low_bets': decimal_to_percentage(self.session.config['bets'][1]),
            'medium_bets': decimal_to_percentage(self.session.config['bets'][2]),
            'high_bets': decimal_to_percentage(self.session.config['bets'][3]),
            'very_high_bets': decimal_to_percentage(self.session.config['bets'][4]),
        }

    def before_next_page(self):
        if self.timeout_happened:
            self.player.choice = random.choice(list(range(Constants.choice_num)))


class WaitingGroup(WaitPage):
    def after_all_players_arrive(self):

        if self.session.config['save_html_image']:
            if self.round_number > 1: 
                self.get_group_page_image('Results', self.round_number-1)
            self.get_group_page_image('ChoosePage', self.round_number)

        if self.session.config['use_bot_player']:
            if self.session.config['use_multimodal_model']:
                if self.round_number > 1: 
                    self.async_get_group_understanding()
            self.async_get_group_choice()

        self.group.play_round()
        self.group.judge_end()

    def get_group_page_image(self, page_name, round_number):
        page_name_list = ['Results', 'ChoosePage']

        assert page_name in page_name_list, 'Page name must be one of the following: {}'.format(page_name_list)

        for player in self.group.get_players():
            st = self.session.vars['time_stamp']
            root_path = Path(
                player.subsession.get_folder_name()) / 'logs' / f'{st}_{player.session.code}' / player.participant.code / f'{page_name}'
            html_path = root_path / 'html' / f'{round_number}.html'
            file_url = html_path.resolve().as_uri()
            image_path = root_path / 'image' / f'{round_number}.png'
            capture_html_to_image(file_url, output_path=image_path)

    def async_get_group_choice(self):
        self.async_run_func('get_bot_choice')

    def async_get_group_understanding(self):
        self.async_run_func('get_vlm_bot_understanding')

    def async_run_func(self, func_name):
        futures = []
        with ThreadPoolExecutor(max_workers=self.session.config['max_workers']) as executor:
            for player in self.subsession.get_players():  # group not subsession
                future = executor.submit(getattr(player, func_name, None))
                futures.append(future)

        try:
            done, not_done = wait(futures, timeout=60, return_when=ALL_COMPLETED)
            for future in futures:
                result = future.result()
                if result is not None:
                    to_update_objs, to_update_attributes = result
                    for i, obj in enumerate(to_update_objs):
                        for attr, value in to_update_attributes[i].items():
                            setattr(obj, attr, value)

        except TimeoutError:
            print("Timeout occurred before all futures completed")
            for future in not_done:
                index = futures.index(future)
                self.subsession.get_players()[index].bot_choice_error = True


class Results(PageSaveHTML):
    def begin_get(self):
        pass

    def get_timeout_seconds(self):
        return self.session.config['timeout_seconds']

    def vars_for_template(self):
        return {
            'round': self.subsession.round_number,
            'debug': self.session.config.get('debug', False),
            'choice': int(self.player.choice),
            'payoff': int(self.player.payoff), 
            'remain': int(self.player.remain_by_round_interactions()),
            'choice_percent': int(self.player.choice_percent),
            'choice_color': self.player.choice_color,
            'chinese_choice_color': 'F类型' if self.player.choice_color == 'blue' else 'J类型',
            'box_color_distri': self.player.box_color_distri,
            'box_blue_list': list(range(1, eval(self.player.box_color_distri)[0]+1)), 
            'box_red_list': list(range(eval(self.player.box_color_distri)[0]+1,Constants.box_num+1)),
            'token_box_id': self.player.token_box_id,
            'lang': self.session.config.get('lang', 'en'),
        }


class FinalSurvey(Page):
    form_model = 'player'
    form_fields = ['final_survey_group_1_q1_choice', 'final_survey_group_1_q2_choice', 'final_survey_group_1_q3_choice',
                   'final_survey_group_1_q4_choice', 'final_survey_group_2_q1_choice', 'final_survey_group_2_q2_choice',
                   'final_survey_group_3_q1_choice', 'final_survey_group_3_q2_choice', 'final_survey_group_3_q3_choice',
                   'final_survey_group_3_q4_choice', 'final_survey_group_4_q1_choice', 'final_survey_group_4_q2_choice',
                   ]

    def is_displayed(self):
        return self.session.vars['end_game']

    def vars_for_template(self):
        return {
            'total_payoff': self.player.remain() // self.session.config['total_interactions'],
            'gpt_mean': self.session.config['gpt_mean'] // 32,
            'gpt_std': self.session.config['gpt_std'],
        }


class FinalResults(Page):
    timeout_seconds = 60

    def is_displayed(self):
        return self.session.vars['end_game']

    def vars_for_template(self):
        return {
            'has_upcoming_apps': len(self.session.config['app_sequence']) > 1,
            'lang': self.session.config.get('lang', 'en')
        }

    def app_after_this_page(self, upcoming_apps):
        if self.session.vars['end_game'] and len(upcoming_apps) > 0:
            return upcoming_apps[0]


page_sequence = [
    PreIntroduction,
    Introduction,
    ChoosePage,
    WaitingGroup,
    Results,
    FinalSurvey,
    FinalResults
]
