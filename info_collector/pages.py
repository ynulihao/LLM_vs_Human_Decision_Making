from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


def _get_labels(en):
    return {
        'game_id': '实验编号' + (' (Game ID)' if en else ''),
        'name': '姓名' + (' (Name)' if en else ''),
        'contact': '联系电话' + (' (Phone number)' if en else ''),
        'student_id': '学号' + (' (Student ID)' if en else ''),
        'school': '学校' + (' (School/University)' if en else ''),
        'major': '专业' + (' (Major)' if en else ''),
        'gender': '性别' + (' (Gender)' if en else ''),
        'nation': '民族' + (' (Nationality)' if en else ''),
        'age': '年龄' + (' (Age)' if en else ''),
        'country': '国家' + (' (Country)' if en else ''),
        'birthplace': '出生地' + (' (Birthplace)' if en else ''),
        'religion': '宗教' + (' (Religion)' if en else ''),
        'alipay': '支付宝账号' + (' (Alipay account)' if en else ''),
    }


class RecordInfoPage(Page):
    form_model = 'player'
    form_fields = ['game_id', 'name', 'contact', 'student_id', 'school', 'major',
                   'gender', 'nation', 'age', 'country', 'birthplace', 'religion', 'alipay']

    def vars_for_template(self):
        return {
            'en': True if self.session.config['lang'] == 'en' else False,
            'collect_info_first': self.session.config.get('collect_info_first', False),
            'lbl': _get_labels(True if self.session.config['lang'] == 'en' else False)
        }


class RecordCompletePage(Page):
    def vars_for_template(self):
        return {
            'en': self.subsession.en,
            'lbl': _get_labels(self.subsession.en),
            'collect_info_first': self.session.config.get('collect_info_first', False),
            'gender': {'male': '男' + (' (Male)' if self.subsession.en else ''),
                       'female': '女' + (' (Female)' if self.subsession.en else ''),
                       }[self.player.gender]
        }


page_sequence = [
    RecordInfoPage,
    RecordCompletePage
]
