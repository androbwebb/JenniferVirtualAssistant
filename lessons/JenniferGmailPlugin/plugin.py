# -*- coding: utf-8-*-
import email
import inflect

from lessons.base.plugin import JenniferResponsePlugin, JenniferNotificationPlugin
from lessons.base.responses import JenniferResponse, JenniferTextResponseSegment, JenniferHtmlResponseSegment
from lessons.base.decorators import intent

from lessons.JenniferGmailPlugin.logic import GmailImapWrapper
from lessons.JenniferGmailPlugin.shared_settings import JenniferGmailSharedSettings


class JenniferGmailPlugin(JenniferResponsePlugin, JenniferGmailSharedSettings):

    PRIORITY = 50
    VERBOSE_NAME = "Gmail"
    REQUIRES_NETWORK = True

    def __init__(self, *args, **kwargs):
        self.pluralize_engine = inflect.engine()
        JenniferResponsePlugin.__init__(self, *args, **kwargs)

    @staticmethod
    def _is_intent_email_reated(tags, plain_text):
        """Does the user want to do something with emails?"""
        one_of_these = [
            ('inbox', 'NN'),
            ('email', 'NN'),
            ('emails', 'NNS'),
            ('gmail', 'NN'),
            ('gmails', 'NNS'),
        ]
        return any([word in tags for word in one_of_these])

    @intent
    def _is_intent_read_unread(self, tags, plain_text):
        """Does the user want to hear the emails outloud?"""
        one_verb = [
            ('read', 'VB'),
            ('check', 'VB'),
            ('check', 'NN'),
        ]
        return any([word in tags for word in one_verb]) \
               and self._is_intent_email_reated(tags, plain_text)

    @intent
    def _is_intent_count(self, tags, plain_text):
        """Does the user want to just hear unread counts?"""
        one_of_these = [
            ('count', 'NN'),
            ('count', 'VB'),
            ('count', 'VB'),
            ('how', 'WRB')
        ]
        return any([word in tags for word in one_of_these]) \
               and self._is_intent_email_reated(tags, plain_text)

    def can_respond(self, **kwargs):
        """
        Test if it can respond
        :param kwargs:
        :return:
        """
        tags = kwargs.get('tags')
        plain_text = kwargs.get('plain_text')

        # Only respond if we have an account
        if len(self.settings.get('accounts', [])) == 0:
            return False

        return any(self._intent_dictionary(tags, plain_text).values())

    def respond(self, **kwargs):
        """
        Respond to the user
        :param kwargs:
        :return:
        """
        plain_text = kwargs.get('plain_text')
        client = kwargs.get('client')
        client.give_output_string(self, "Checking email")

        # Find out which email
        this_account = None
        all_my_emails = {account['name'].lower(): account for account in self.get_accounts()}

        if len(self.get_accounts()) > 1:
            # Check if they included the name of the account already: i.e. "Check my work email"
            for email_account in all_my_emails.keys():
                if email_account in plain_text:
                    this_account = all_my_emails[email_account]
                    return self.dispatch_to_intent(this_account, **kwargs)

            client.give_output_string(self, "Which email account did you mean?")
            which_email_input = client.collect_input().lower()
            for email_account in all_my_emails.keys():
                if which_email_input in email_account:
                    this_account = all_my_emails[email_account]
                    return self.dispatch_to_intent(this_account, **kwargs)

            # If still hasn't selected an email, just iterate over them
            for email_account in all_my_emails.keys():
                # Ugh, couldn't match one.. let's just iterate through them
                if client.confirm(self, "Did you want to read your {} emails?".format(email_account)):
                    this_account = all_my_emails[email_account]
                    return self.dispatch_to_intent(this_account, **kwargs)
        else:
            # Only one accounts
            this_account = self.get_accounts()[0]
            return self.dispatch_to_intent(this_account, **kwargs)

        if not this_account:
            return

    def dispatch_to_intent(self, account, **kwargs):
        """
        Call whatever intent should be called
        :param account:
        :param kwargs:
        :return:
        """
        tags = kwargs.get('tags')
        plain_text = kwargs.get('plain_text')
        intents = self._intent_dictionary(tags, plain_text)

        if intents['read_unread']:
            return self.respond_read_unread(account, **kwargs)
        if intents['count']:
            return self.respond_count(account, **kwargs)

    def respond_read_unread(self, account, **kwargs):
        client = kwargs.get('client')

        # Get the imap instance
        imap = GmailImapWrapper(account['email'], account['password'], self.settings['markAsRead'])
        # Say "You have 10 new messages"
        unread_count = imap.num_unread_emails
        client.give_output_string(self, "You have {} new {}".format(unread_count,
                                                                    self.pluralize_engine.plural('email', unread_count)))

        if unread_count > 3:
            if not client.confirm(self, "Want me to read them all?", ['read']):
                return

        # Iterate over them with subjects (marking as read)
        emails = imap.get_unread_emails(10)
        for email_uid, email_msg in emails:
            from_email = email.utils.parseaddr(email_msg['From'])
            subject = email_msg['Subject']
            client.give_output_string(self, "Email from {}. Subject: {}".format(from_email[0] or from_email[1], subject))

            # Should we read the body?
            if client.confirm(self, "Want me to read it?", ['read']):
                client.give_output_string(self, "It says:")
                client.give_output_string(self, JenniferHtmlResponseSegment(imap.get_first_text_block(email_msg)))
                imap.read_message(email_uid)

            # Should we delete it?
            if client.confirm(self, "Should I delete it?", ['read']):
                client.give_output_string(self, "Deleted")
                imap.delete_message(email_uid)

    def respond_count(self, account, **kwargs):
        imap = GmailImapWrapper(account['email'], account['password'], self.settings['markAsRead'])
        unread = imap.num_unread_emails
        unread = unread if unread != 0 else "no"
        total = imap.num_total_emails
        return JenniferResponse(self, [
            JenniferTextResponseSegment(
                "You have {} new {}, and {} {} total".format(unread,
                                                             self.pluralize_engine.plural('email', unread),
                                                             total,
                                                             self.pluralize_engine.plural('message', total)))])


class JenniferGmailNotifierPlugin(JenniferNotificationPlugin, JenniferGmailSharedSettings):
    """
    A notification plugin. Checks for unread emails every minute and announces it.
    """

    RUN_EVERY_N_SECONDS = 60 * 1  # one minute
    PRIORITY = 10
    REQUIRES_NETWORK = True

    def __init__(self, brain, settings=None, profile=None):
        # Call parent
        JenniferNotificationPlugin.__init__(self, brain, profile, settings)

        # Dict for holding number of new emails
        self.number_new_emails = {}

        # For pluralizing
        self.pluralize_engine = inflect.engine().plural

        # `number_emails_announced` tracks how many new emails we've already notified about.
        #   We don't want to notify right away
        self.number_emails_announced = self.number_new_emails.copy()

    def set_settings(self, settings):
        """
        After setting the settings, initialize the counts of emails
        :param settings:
        :return:
        """
        JenniferNotificationPlugin.set_settings(self, settings)
        self.update_number_new_emails()
        self.number_emails_announced = self.number_new_emails.copy()

    def update_number_new_emails(self):
        """
        Update self.number_new_emails to hold unread counts for each account. Something like:
         {
            'personal': 15,
            'work': 0
         }
        :return: None
        """
        if hasattr(self, 'settings') and 'accounts' in self.settings:
            for account in self.get_accounts():
                if account['notifyNewEmails']:
                    imap = GmailImapWrapper(account['email'], account['password'], False)
                    self.number_new_emails[account['name']] = imap.num_unread_emails

    def run(self):
        """
        This runs every 2 minutes, and creates notifications if there are new emails
        :return:
        """
        self.update_number_new_emails()
        for account_name, count in self.number_new_emails.iteritems():
            try:
                new_count = count - self.number_emails_announced.setdefault(account_name, 0)
                if new_count > 0:

                    # Create the notification
                    notification_text = "You have {} new {} {}".format(new_count, account_name, self.pluralize_engine('email', new_count))
                    self.insert_into_queue(notification_text)

                    # Update notified count
                    self.number_emails_announced[account_name] = count
                elif new_count < 0:
                    self.number_emails_announced[account_name] = count
            except KeyError:
                # TODO: Never announced this account before (weird)
                pass
