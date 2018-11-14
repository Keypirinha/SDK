# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu

from collections import namedtuple
import datetime
import os

AnswerTuple = namedtuple('AnswerTuple', ('value', 'datetime'))

class YesNo(kp.Plugin):
    """A simple "Yes or No" plugin"""

    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    history = []

    def __init__(self):
        super().__init__()

    def on_start(self):
        self.history = []

        self.set_actions(self.ITEMCAT_RESULT, [
            self.create_action(
                name="copy",
                label="Copy",
                short_desc="Copy the name of the answer")])

    def on_catalog(self):
        self.set_catalog([self.create_item(
            category=kp.ItemCategory.KEYWORD,
            label="YesNo",
            short_desc="Yes or No",
            target="yesno",
            args_hint=kp.ItemArgsHint.REQUIRED,
            hit_hint=kp.ItemHitHint.NOARGS)])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[-1].category() != kp.ItemCategory.KEYWORD:
            return

        if not user_input:
            self.history = []

        # compute a new answer
        self.history.append(AnswerTuple(
            os.urandom(1)[0] % 2,
            datetime.datetime.now()))

        # suggest this new answer as well as the previous ones
        suggestions = []
        for idx in range(len(self.history) - 1, -1, -1):
            answer = self.history[idx]
            desc = "{}. {} (press Enter to copy)".format(
                idx + 1, answer.datetime.strftime("%H:%M:%S"))
            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label=self._value_to_string(answer.value),
                short_desc=desc,
                target="{},{}".format(answer.value, idx),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.NONE)

    def on_execute(self, item, action):
        if item and item.category() == self.ITEMCAT_RESULT:
            value = int(item.target().split(',', maxsplit=1)[0])
            kpu.set_clipboard(self._value_to_string(value))

    def _value_to_string(self, value):
        return "Yes" if value else "No"
