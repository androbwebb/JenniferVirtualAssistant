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

        print ask_add_gmail()
        answer = raw_input(prompt)

        while answer.lower() not in ['n', 'no']:
            current_email = {}
            print "Email Address:"
            current_email['email'] = raw_input(prompt)
            print "Password:"
            current_email['password'] = getpass(prompt)
            print "Name (Personal, Work, etc):"
            current_email['name'] = raw_input(prompt).lower()
            print "Receive notifications when you have new emails for this account? (y/n)"
            current_email['notifyNewEmails'] = raw_input(prompt).lower() in ['y', 'yes']

            settings_template_dict['accounts'].append(current_email)

            # Ask about more
            print ask_add_gmail()
            answer = raw_input(prompt)

        print "Should I mark emails as read when I read them out loud to you? (y/n)"
        answer = raw_input(prompt)
        settings_template_dict['markAsRead'] = answer.lower() in ['y', 'yes']

        return settings_template_dict
