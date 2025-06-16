import time
import random

from . import pages
from ._builtin import Bot


class PlayerBot(Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def play_round(self):
        if self.session.vars['end_game']:
            return

        if self.round_number == 1:
            yield pages.PreIntroduction
            yield pages.Introduction

        choice = random.choice('0123')

        yield pages.ChoosePage, dict(choice=choice)

        yield pages.Results

        if self.session.vars['end_game']:
            survey_answer = dict()
            for q in pages.FinalSurvey.form_fields:
                survey_answer[q] = 0

            yield pages.FinalSurvey, survey_answer
            yield pages.FinalResults


if __name__ == '__main__':
    print('test')