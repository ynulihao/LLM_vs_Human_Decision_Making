# Don't change anything in this file.
from .. import models
import otree.api
from otree.views.abstract import MockForm

from pathlib import Path
from otree_utils.misc import clean_html

class PageClassWithSaveHTML(otree.api.Page):
    form_model = None
    form_fields = []

    _template_type = 'Page'

    def begin_get(self):
        pass

    def end_get(self):
        pass

    def get(self):
        self.begin_get()

        if not self._is_displayed():
            self._increment_index_in_pages()
            return self._redirect_to_page_the_user_should_be_on()

        # this needs to be set AFTER scheduling submit_expired_url,
        # to prevent race conditions.
        # see that function for an explanation.
        # self.participant._current_form_page_url = self.request.url.path

        self._update_monitor_table()

        # 2020-07-10: maybe we should call vars_for_template before instantiating the form
        # so that you can set initial value for a field in vars_for_template?
        # No, i don't want to commit to that.
        if self.has_form():
            obj = self.get_object()
            form = self.get_form(instance=obj)
        else:
            form = MockForm()

        context = self.get_context_data(form=form)
        response = self.render_to_response(context)
        self.browser_bot_stuff(response)

        # API used
        # print(self.participant._url_i_should_be_on())
        # print(response.body.decode('utf-8'))
        # self.session.code
        # self.participant.code
        # self.session.config
        # self.subsession.get_folder_name()
        # os.path.abspath(os.getcwd())
        # breakpoint()

        st = self.session.vars['time_stamp']
        root_path = (Path(self.subsession.get_folder_name()) / 'logs' / f'{st}_{self.session.code}' /
                     self.participant.code / self.__class__.__name__)

        root_path.mkdir(parents=True, exist_ok=True)

        if self.session.config['save_html_image']:
            html_path = root_path / 'html' / f'{self.round_number}.html'
            html_path.parent.mkdir(parents=True, exist_ok=True)
            with open(html_path, 'w') as f:
                # 清理HTML外的JS，避免死循环
                static_file_port = self.session.config['static_file_port']
                raw_html = response.body.decode('utf-8').replace('/static/', f'http://127.0.0.1:{static_file_port}/static/')
                cleaned_html = clean_html(raw_html)
                f.write(cleaned_html)

            file_url = html_path.resolve().as_uri()
            image_path = root_path / 'image' / f'{self.round_number}.png'
            image_path.parent.mkdir(parents=True, exist_ok=True)

            # capture_html_to_image(file_url, output_path=image_path)

        self.end_get()
        return response


class Page(otree.api.Page):
    subsession: models.Subsession
    group: models.Group
    player: models.Player


class PageSaveHTML(PageClassWithSaveHTML):
    subsession: models.Subsession
    group: models.Group
    player: models.Player


class WaitPage(otree.api.WaitPage):
    subsession: models.Subsession
    group: models.Group


class Bot(otree.api.Bot):
    subsession: models.Subsession
    group: models.Group
    player: models.Player
