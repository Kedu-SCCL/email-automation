#!/usr/bin/python

from email_automation import Email

from settings import smtp_server, smtp_port, smtp_user, smtp_password,\
                     l_destination_email

e = Email(smtp_server = smtp_server, smtp_port = smtp_port, smtp_user =
          smtp_user, smtp_password = smtp_password)

e.send_email(l_destination_email, 'subject', 'body')
