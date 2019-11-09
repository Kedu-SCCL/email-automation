#!/usr/bin/python

from email_automation import Email

from settings import host, username, password, processed_email_db,\
                     acl_from_email_address

e = Email(host = host, username = username, password = password,
          processed_email_db = processed_email_db, acl_from_email_address =
          acl_from_email_address)

e.logger.info('Getting pending processing emails...')
print(e.get_pending_processing_emails())

