import time
import random
from pathlib import Path

from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage, PageSaveHTML
from otree_utils.screenshot import capture_html_to_image

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, TimeoutError


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
            'init_money': self.session.config.get('init_money', 2000) * self.session.config.get('reward_scaling_factor', 1),
            'debug': self.session.config.get('debug', False),
            'lang': self.session.config.get('lang', 'en')
        }


class ChoosePage(PageSaveHTML):
    form_model = 'player'
    form_fields = ['choice']

    def get_timeout_seconds(self):
        return self.session.config['timeout_seconds']

    def vars_for_template(self):
        return {
            'round': self.subsession.round_number,
            'card_num': self.session.config['card_num'],
            'card_num_for_loop': list(range(1,self.session.config['card_num']+1)),
            'debug': self.session.config.get('debug', True),
            'lang': self.session.config.get('lang', 'en'),
        }

    def before_next_page(self):
        if self.timeout_happened:
            self.player.choice = random.choice('0123')


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
            'card_num': self.session.config['card_num'],
            'card_num_for_loop': list(range(1,self.session.config['card_num']+1)),
            'debug': self.session.config.get('debug', False),
            'choice': int(self.player.choice),
            'reward': int(self.player.reward),
            'penalty': int(self.player.penalty),
            'payoff': int(self.player.payoff),  
            'remain': int(self.player.remain()),
            'lang': self.session.config.get('lang', 'en')
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
            'total_payoff': (self.player.remain() - self.session.config['init_money']) // self.session.config['total_interactions'],
            'gpt_mean': self.session.config['gpt_mean'] // 80,
            'gpt_std': self.session.config['gpt_std'] // 80,
            'lang': self.session.config.get('lang', 'en')
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
