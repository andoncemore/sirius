import flask

from sirius.models import hardware
from sirius.models.db import db
from sirius.testing import base

# pylint: disable=no-member
class TestPrinting(base.Base):

    def setUp(self):
        base.Base.setUp(self)
        self.autologin()
        hardware.Printer.phone_home('000d6f000273ce0b')
        self.testuser.claim_printer('n5ry-p6x6-kth7-7hc4', 'my test printer')
        db.session.commit()
        self.printer = hardware.Printer.query.first()

    def get_print_url(self):
        return flask.url_for(
            'printer_print.printer_print',
            user_id=self.testuser.id,
            username=self.testuser.username,
            printer_id=self.printer.id,
        )

    def test_print_ok(self):
        r = self.client.post(self.get_print_url(), data=dict(
            target_printer=self.printer.id, 
            face='default',
            message='hello'
        ))
        self.assertRedirects(r, '/printer/1')

    def test_print_wrong_printer(self):
        r = self.client.post(self.get_print_url(), data=dict(
            target_printer='10',
            face='default',
            message='hello2'
        ))
        self.assertIn('Not a valid choice', r.data.decode('utf-8'))
        self.assert200(r)
    
    def test_that_message_is_added_to_db(self):
        self.assertTrue(self.printer.messages.count() == 0)

        r = self.client.post(self.get_print_url(), data=dict(
            target_printer=self.printer.id, 
            face='default',
            message='hello'
        ))

        self.assertTrue(self.printer.messages.count() == 1)
    
    def test_that_stored_messages_are_trimmed(self):
        from sirius.models.messages import Message
        from sirius.protocol.protocol_loop import _get_next_command_id

        # put 100 dummy messages in the database
        dummy_messages = [
            Message(
                print_id=_get_next_command_id(),
                pixels=bytearray(b''),
                sender_name='[dummy test data]',
                target_printer=self.printer,
            ) 
            for _ in range(100)
        ]
        
        for dummy_message in dummy_messages:
            db.session.add(dummy_message)
        
        db.session.commit()
        self.assertEqual(self.printer.messages.count(), 100)

        # add one more
        r = self.client.post(self.get_print_url(), data=dict(
            target_printer=self.printer.id, 
            face='default',
            message='hello'
        ))

        # check there are still 100
        self.assertEqual(self.printer.messages.count(), 100)

        # check that the oldest message was deleted
        self.assertNotIn(dummy_messages[0], self.printer.messages)
        # and the second-oldest was not deleted
        self.assertIn(dummy_messages[1], self.printer.messages)
