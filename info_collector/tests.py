from otree.api import Currency as c, currency_range, Submission
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):
        if self.round_number != 1:
            return

        yield pages.RecordInfoPage, dict(game_id=self.group.id_in_subsession, name=self.group.id_in_subsession,
                                         contact='18593167826', student_id='20171120065', school='ynu', major='se',
                                         gender='male', nation='CN', age=24, country='CN', birthplace='CN',
                                         religion='GCZY', alipay='18593167826')

        yield Submission(pages.RecordCompletePage, check_html=False)

