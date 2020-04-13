from getpass import getpass


class JenniferGmailSharedSettings(object):

    def get_accounts(self):
        try:
            return self.settings['accounts']
        except (KeyError, TypeError):
            return []

    @staticmethod
    def initialize_settings(settings_template_dict):
        """
        Custom initialize settings
        """
        settings_template_dict['accounts'] = []
        prompt = "> "

        # A helper to get the ask
        def ask_add_gmail():
            return "Do you want to add {} Gmail Account (y/n)?".format("a" if len(settings_template_dict['accounts']) == 0 else "another")

        print(ask_add_gmail())
        answer = input(prompt)

        while answer.lower() not in ['n', 'no']:
            current_email = {}
            print("Email Address:")
            current_email['email'] = input(prompt)
            print("Password:")
            current_email['password'] = getpass(prompt)
            print("Name (Personal, Work, etc):")
            current_email['name'] = input(prompt).lower()
            print("Receive notifications when you have new emails for this account? (y/n)")
            current_email['notifyNewEmails'] = input(prompt).lower() in ['y', 'yes']

            settings_template_dict['accounts'].append(current_email)

            # Ask about more
            print(ask_add_gmail())
            answer = input(prompt)

        if len(settings_template_dict['accounts']) >= 1:
            print("Should I mark emails as read when I read them out loud to you? (y/n)")
            answer = input(prompt)
            settings_template_dict['markAsRead'] = answer.lower() in ['y', 'yes']
        else:
            settings_template_dict['enabled'] = False

        return settings_template_dict
