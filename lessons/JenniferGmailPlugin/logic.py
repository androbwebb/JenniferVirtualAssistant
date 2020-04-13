import imaplib
import email
import re


class GmailImapWrapper(object):

    def __init__(self, username, password, mark_as_read, mailbox="INBOX"):
        self.username = username
        self.password = password
        self.mark_as_read = mark_as_read
        self.mailbox = mailbox

    def login_and_select(self, readonly=None):
        if readonly is None:
            readonly = True
        self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
        self.imap.login(self.username, self.password)
        self.imap.select(mailbox=self.mailbox, readonly=readonly)

    def logout_and_close(self):
        self.imap.close()
        self.imap.logout()

    def _get_status(self):
        return self.imap.status(self.mailbox,'(MESSAGES UNSEEN)')

    def _status(self):
        self.login_and_select()
        _, data = self._get_status()
        messages = int(re.search('MESSAGES\s+(\d+)', data[0]).group(1))
        unseen = int(re.search('UNSEEN\s+(\d+)', data[0]).group(1))
        self.logout_and_close()
        return {
            'total': messages,
            'unseen': unseen
        }

    @property
    def num_unread_emails(self):
        return self._status()['unseen']

    @property
    def num_total_emails(self):
        return self._status()['total']

    def get_unread_email_uids(self, number=10):
        self.login_and_select()
        _, data = self.imap.uid('search', None, '(UNSEEN)')
        to_return = data[0].split()[-number:]
        self.logout_and_close()
        return to_return

    def get_unread_emails(self, number=10):
        # Split off the last `numeber` emails
        email_uids = self.get_unread_email_uids()

        self.login_and_select()
        emails = []
        for email_uid in email_uids:
            _, data = self.imap.uid('fetch', email_uid, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_string(raw_email)
            emails.append((email_uid, email_message))

        self.logout_and_close()
        return emails

    def read_message(self, message_uid):
        if not self.mark_as_read:
            return  # Don't bother

        # Login without readonly for this
        self.login_and_select(readonly=False)
        self.imap.uid('store', message_uid, '+FLAGS', '\Seen')
        self.logout_and_close()

    def delete_message(self, message_uid):
        # Login without readonly for this
        self.login_and_select(readonly=False)
        self.imap.uid('store', message_uid, '+FLAGS', '\Deleted')
        self.imap.expunge()
        self.logout_and_close()

    @staticmethod
    def get_first_text_block(email_message_instance):

        def parse_before_return(string):
            # To help with weird apple mail formatting.
            return string.decode('utf8').replace('=\r\n', '').replace('=20', '')

        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return parse_before_return(part.get_payload())
        elif maintype == 'text':
            return parse_before_return(email_message_instance.get_payload())

