from django import forms
from django.forms import formset_factory
from django.db.models import Q

from haley_gg.apps.stats.models import (
    Player, Map, Result, League, ProleagueTeam
)


class ResultForm(forms.Form):
    date = forms.DateField(
        label='날짜',
        widget=forms.NumberInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
            }
        ),
    )
    league = forms.ModelChoiceField(
        label='리그',
        queryset=League.objects.all(),
        widget=forms.Select(
            attrs={'class': 'form-control'}
        )
    )
    title = forms.CharField(
        label='게임 이름',
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        ),
    )

    def clean(self):
        # Check that matches are already exist...?
        # This validation only check that if already exists title.
        # But result model has round field...
        # Only validate on title field? It's wrong!
        # So this validation is not required in this form.
        # And this must be move to formset.
        pass
        # if Result.objects.filter(
        #     date=self.cleaned_data.get('date'),
        #     league=self.cleaned_data.get('league'),
        #     title=self.cleaned_data.get('title')
        # ).exists():
        #     error_msg = '같은 경기 결과가 이미 존재합니다.'
        #     self.add_error('title', error_msg)


class PVPDataForm(forms.Form):
    race_list = [
        ('T', 'Terran'),
        ('P', 'Protoss'),
        ('Z', 'Zerg'),
    ]
    # set or winner's match, etc ...
    # this field is combined into title field in ResultForm.
    round = forms.CharField(
        label="라운드",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        ),
    )
    type = forms.ChoiceField(
        label="게임 타입",
        choices=[
            ('melee', '밀리'),
            ('top_and_bottom', '팀플')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            },
        ),
    )
    winner = forms.ModelChoiceField(
        label="승자",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    winner_race = forms.ChoiceField(
        label="승자 종족",
        choices=race_list,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    map = forms.ModelChoiceField(
        label='맵',
        queryset=Map.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    loser = forms.ModelChoiceField(
        label="패자",
        queryset=Player.objects.all(),
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )
    loser_race = forms.ChoiceField(
        label="패자 종족",
        choices=race_list,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                # 'required': 'true'
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        # Check that winner is same as loser.
        if not self.errors:
            winner = cleaned_data.get('winner')
            loser = cleaned_data.get('loser')
            if winner.name == loser.name:
                error_msg = '선택한 플레이어 이름이 같습니다.'
                self.add_error('winner', error_msg)
                self.add_error('loser', error_msg)
        return cleaned_data


class PVPDataFormSet(forms.BaseFormSet):
    def is_valid_with(self, resultForm):
        try:
            # Get resultForm data to check that data what formset have already exists.
            self.resultForm = resultForm
            super().is_valid()
        except Exception:
            raise Exception

    def clean(self):
        super().clean()

        # If formset have errors, pass cross form validation.
        if self.total_error_count() > 0:
            return

        # Group by round
        grouped_form = {}
        for form in self.forms:
            round = form.cleaned_data.get('round')
            # Check that data already exists with resultForm data given.
            if Result.objects.filter(
                date=self.resultForm.cleaned_data.get('date'),
                league=self.resultForm.cleaned_data.get('league'),
                title=self.resultForm.cleaned_data.get('title'),
                round=round
            ).exists():
                error_msg = '같은 경기 결과가 이미 존재합니다.'
                form.add_error('round', error_msg)
                continue
            if round not in grouped_form:
                grouped_form[round] = []
            grouped_form[round].append(form)

        # Iterate forms that grouped by round.
        for form_list in grouped_form.values():
            # Only run below validation sequence when rabs()esult type is teamplay.
            # Melee data already validated in PVPDataForm.
            if len(form_list) < 2:
                continue

            # Check that all map are equal.
            maps = [form.cleaned_data.get('map') for form in form_list]
            map_error_msg = ''
            if len(maps) != len(set(maps)):
                map_error_msg = '같은 맵이 아닙니다.'

            # Check that all players are distinct.
            players = [form.cleaned_data.get('winner') for form in form_list]
            players.extend([form.cleaned_data.get('loser') for form in form_list])
            duplicate_players = set([x for x in players if players.count(x) > 1])
            duplicate_error_msg = '플레이어가 중복됩니다.'

            # Check that all type are equal.
            error_msg = '팀플 타입이 아닙니다.'
            for form in form_list:
                if form.cleaned_data.get('type') != 'top_and_bottom':
                    form.add_error('type', error_msg)
                if len(map_error_msg) == 0:
                    form.add_error('map', map_error_msg)
                if form.cleaned_data.get('winner') in duplicate_players:
                    form.add_error('winner', duplicate_error_msg)
                if form.cleaned_data.get('loser') in duplicate_players:
                    form.add_error('loser', duplicate_error_msg)

    def save_with(self, ResultForm):
        # To create result data, we use form, not modelform.
        # Q: Why don't you use ModelForm?
        # A: Because modelform can't satisfy my result model.
        # This form have field that winner and loser,
        # but Result model only has one player.
        # And it doesn't care who is winner. Just it has win_status.
        # So we create two result data related winner and loser,
        # but modelform only create one data. So, I use form, not modelform.

        # It works fine, but using modelform is standardly recommand.
        date = ResultForm.cleaned_data.get('date')
        league = ResultForm.cleaned_data.get('league')
        title = ResultForm.cleaned_data.get('title')

        result_list = []
        for form in self.forms:
            cleaned_data = form.cleaned_data
            result_list.extend([
                Result(
                    date=date,
                    league=league,
                    title=title,
                    round=cleaned_data.get('round'),
                    map=cleaned_data.get('map'),
                    type=cleaned_data.get('type'),
                    player=cleaned_data.get('winner'),
                    race=cleaned_data.get('winner_race'),
                    win_state=True
                ),
                Result(
                    date=date,
                    league=league,
                    title=title,
                    round=cleaned_data.get('round'),
                    map=cleaned_data.get('map'),
                    type=cleaned_data.get('type'),
                    player=cleaned_data.get('loser'),
                    race=cleaned_data.get('loser_race'),
                    win_state=False
                )]
            )
        Result.objects.bulk_create(result_list)

        saved_result_list = []
        for result in result_list:
            # Calculate team status.

            # 1. resultForm에 들어있는 리그를 갖고 온다.
            # 2. 프로리그가 아니라면 그만둔다.
            # 3. 플레이어의 팀을 찾을 때, 해당 리그에 맞는 팀을 갖고 온다.
            # 4. 그 팀에 승리 또는 패배값을 누적하고 points에도 같이 누적한다.
            # 4-1. 팀플매치인경우 한 번만 누적한다.
            if league.type != 'proleague':
                continue

            # player가 속하고, league가 1번의 결과값인 team을 찾는다.
            team = ProleagueTeam.objects.filter(
                Q(league=league) &
                Q(players__in=[result.player])
            ).first()

            if result.round not in saved_result_list:
                team.save_result(result)
                saved_result_list.append(result.round)


def get_pvp_data_formset():
    return formset_factory(
        form=PVPDataForm,
        formset=PVPDataFormSet,
        extra=2,
    )
