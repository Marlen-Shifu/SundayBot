import logging

from db import User, Record, db_session as s

import datetime



def get_user(id, username = None):

    try:
        user = s.query(User).filter_by(id = id).first()

        if user == None:
            user_by_username = s.query(User).filter_by(username = username).first()
            return user_by_username

        return user
    except Exception as e:
        print(e)


def get_user_by_userid(id):

    try:
        user = s.query(User).filter_by(user_id = id).first()

        return user
    except Exception as e:
        print(e)


def add_user(user_id, username):

    try:

        user = User(username = username, user_id = user_id)

        s.add(user)
        s.commit()

        return 'ok'

    except Exception as e:
        return 'no'


def update_user_id(user, id):

    try:
        s.query(User).filter_by(username = user.username).update({User.user_id: id})
        s.commit()
    except Exception as e:
        print(e)


def get_all_workers():

    try:
        workers = s.query(User).all()
        return workers
    except Exception as e:
        print(e)



def get_record(id):

    try:
        res = s.query(Record).filter_by(id = id).first()

        return res
    except Exception as e:
        print(e)


def add_record(name, phone, cheque_photo, cheque_number):

    try:

        time = datetime.datetime.now()
        logging.warning(datetime)

        res = Record(name = name, phone = phone, cheque_photo = cheque_photo, cheque_number = cheque_number)

        s.add(res)
        s.commit()

        return 'ok'

    except Exception as e:
        return 'no'


def get_all_records():

    try:
        res = s.query(Record).all()
        return res
    except Exception as e:
        print(e)


def delete_record(id):

    try:

        res = get_record(id)

        s.delete(res)
        s.commit()

        return 'ok'

    except Exception as e:
        logging.warning(e)
        return 'no'