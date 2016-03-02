import os
import mock


def test_get_gmail_accounts(accounts=None):
    if accounts is None:
        def x(_):
            return [
                {
                    "email": "jennifervirtualassistantandrew@gmail.com",
                    "password": os.getenv('GMAIL_TEST_PASSWORD', ''),
                    "name": "personal",
                    "notifyNewEmails": True
                }
            ]
    else:
        def x(_):
            return accounts

    return x


def mock_imap_get_unread_emails(self, limit=10):
    r = []
    for x in range(limit):
        msg = mock.MagicMock()
        msg['From'] = "test human <test@test.com>"
        msg['Subject'] = "Subject"
        msg['Body'] = "Subject"
        r.append((x, msg))
    return r


def mock_imap_get_first_text_block(self, email_message_instance):
    return "test body test body"


def mock_imap_do_nothing(self, *args, **kwargs):
    return True


def mock_imap_delete(self, *args, **kwargs):
    return mock_imap_do_nothing(self, *args, **kwargs)


def mock_imap_mark_read(self, *args, **kwargs):
    return mock_imap_do_nothing(self, *args, **kwargs)


def mock_imap_status(self, *args, **kwargs):
    return ("OK", ["(INBOX MESSAGES 4000 UNSEEN 2)"])


def mock_can_respond_true(self, **kwags):
    return True