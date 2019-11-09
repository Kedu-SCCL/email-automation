#!/usr/bin/python3

from logging import getLogger, INFO, StreamHandler, Formatter, FileHandler
from sys import stdout
from base64 import b64decode

# http://www.vineetdhanawat.com/blog/2012/06/how-to-extract-email-gmail-contents-as-text-using-imaplib-via-imap-in-python-3/

from imaplib import IMAP4_SSL, IMAP4
from email import message_from_string
from os.path import exists

class Email():

    def __init__(self, host = None, username = None, password = None,
                 processed_email_db = None, acl_from_email_address = None):
        self.logger = self._setup_logger('odoo', 'stdout')
        self.host = host
        self.username = username
        self.password = password
        self.processed_email_db = processed_email_db
        self.acl_from_email_address = acl_from_email_address
        self.imap = None
        self.pending_processing_email = []

    def _setup_logger(self, name, log_file, level=INFO):
        # https://stackoverflow.com/a/11233293
        '''
        Creates a logger
        '''
        if log_file == 'stdout':
            formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler = StreamHandler(stdout)
        else:
            formatter = Formatter('%(asctime)s %(message)s')
            handler = FileHandler(log_file)
        handler.setFormatter(formatter)
        logger = getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        return logger

    def _login(self):
        '''
        Login to IMAP server
        '''
        self.imap = IMAP4_SSL(self.host)
        self.imap.login(self.username, b64decode(self.password).decode('utf8'))

    def _is_not_processed(self, email_id):
        '''
        True if e-mail id is not found in local db
        '''
        mode = 'r+' if exists(self.processed_email_db) else 'w+'
        with open(self.processed_email_db, mode) as fp:
            for line in fp:
                if email_id in line:
                    return False
            fp.write(email_id + '\n')
            return True

    def _is_acl_from_email_address(self, email_from):
        '''
        True if acl_from_email_address not set of set and "From:" matches
        '''
        if self.acl_from_email_address and email_from not in\
           self.acl_from_email_address:
            return False
        return True

    def get_pending_processing_emails(self):
        '''
        Returns message in INBOX which are not yet processed
        '''
        self._login()
        self.imap.select('Inbox')
        result, data = self.imap.uid('search', None, "ALL")
        # search and return uids instead
        i = len(data[0].split()) # data[0] is a space separate string
        for x in range(i):
            latest_email_uid = data[0].split()[x] # unique ids wrt label selected
            result, email_data = self.imap.uid('fetch', latest_email_uid,
                                               '(RFC822)')
            # fetch the email body (RFC822) for the given ID
            raw_email = email_data[0][1]
            #continue inside the same for loop as above
            raw_email_string = raw_email.decode('utf-8')
            # converts byte literal to string removing b''
            email_message = message_from_string(raw_email_string)
            email_id = email_message['Message-Id']
            email_from = email_message['From'].split('<',1)[1].split('>')[0]
            if self._is_not_processed(email_id) and\
               self._is_acl_from_email_address(email_from):
                email_subject = email_message['Subject']
                # this will loop through all the available multiparts in mail
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain": # ignore attachments/html
                        email_body = part.get_payload(decode = True)
                self.pending_processing_email.append((email_from, email_subject,
                                                  email_body.decode('utf8')))
        return self.pending_processing_email

