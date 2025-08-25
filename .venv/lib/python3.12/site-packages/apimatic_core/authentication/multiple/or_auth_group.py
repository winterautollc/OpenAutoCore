from apimatic_core.authentication.multiple.auth_group import AuthGroup


class Or(AuthGroup):

    @property
    def error_message(self):
        return " or ".join(self._error_messages)

    def __init__(self, *auth_group):
        super(Or, self).__init__(auth_group)
        self._is_valid_group = False

    def is_valid(self):
        if not self.mapped_group:
            return False

        for participant in self.mapped_group:
            if participant.is_valid():
                self._is_valid_group = True
            else:
                self.error_messages.append(participant.error_message)

        return self.is_valid_group

