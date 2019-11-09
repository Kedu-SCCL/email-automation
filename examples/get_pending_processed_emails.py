#!/usr/bin/python

from email_automation import Email

from settings import host, username, password, read_email_db, eol,\
                     acl_from_email_address

e = Email(host = host, username = username, password = password,
          read_email_db = read_email_db, eol = eol, acl_from_email_address =
          acl_from_email_address)

e.logger.info('Getting pending processed emails...')
print(e.get_pending_processed_emails())

