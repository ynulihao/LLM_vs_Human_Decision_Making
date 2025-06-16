from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Hu Xintao'

doc = """
Information collector, suggest append to all experiments 
"""

default_conf_in_settings = dict(
    name='info_collector',
    display_name="Information collector",
    num_demo_participants=1,
    app_sequence=['info_collector'],
)


class Constants(BaseConstants):
    name_in_url = 'info_collector'
    players_per_group = None
    num_rounds = 1


class Subsession(BaseSubsession):
    @property
    def en(self):
        return False if 'show_en' not in self.session.config else self.session.config['show_en']


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    game_id = models.StringField(blank=False)
    name = models.StringField(blank=False)
    contact = models.StringField(blank=False)
    student_id = models.StringField(blank=True)
    school = models.StringField(blank=False)
    major = models.StringField(blank=False)
    gender = models.StringField(blank=False, widget=widgets.RadioSelectHorizontal)
    nation = models.StringField(blank=False)
    age = models.IntegerField(blank=False, min=10, max=100)
    country = models.StringField(blank=False)
    birthplace = models.StringField(blank=False)
    religion = models.StringField(blank=True)
    alipay = models.StringField(blank=True)

    def gender_choices(self):
        return [
            ['male', '男' + (' (Male)' if self.subsession.en else '')],
            ['female', '女' + (' (Female)' if self.subsession.en else '')],
        ]
