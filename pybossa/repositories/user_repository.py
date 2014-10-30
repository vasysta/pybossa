# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2014 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.

from sqlalchemy import or_, func
from sqlalchemy.exc import IntegrityError

from pybossa.model.user import User
from pybossa.exc import WrongObjectError, DBIntegrityError



class UserRepository(object):

    def __init__(self, db):
        self.db = db


    def get(self, id):
        return self.db.session.query(User).get(id)

    def get_by_name(self, name):
        return self.db.session.query(User).filter_by(name=name).first()

    def get_by(self, **attributes):
        return self.db.session.query(User).filter_by(**attributes).first()

    def get_all(self):
        return self.db.session.query(User).all()

    def filter_by(self, **filters):
        return self.db.session.query(User).filter_by(**filters).all()

    def search_by_name(self, keyword):
        if len(keyword) == 0:
            return []
        keyword = '%' + keyword.lower() + '%'
        return self.db.session.query(User).filter(or_(func.lower(User.name).like(keyword),
                                  func.lower(User.fullname).like(keyword))).all()

    def total_users(self):
        return self.db.session.query(User).count()

    def save(self, user):
        self._validate_can_be('saved', user)
        try:
            self.db.session.add(user)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
            raise DBIntegrityError(e)

    def update(self, new_user):
        self._validate_can_be('updated', new_user)
        try:
            self.db.session.merge(new_user)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
            raise DBIntegrityError(e)


    def _validate_can_be(self, action, user):
        if not isinstance(user, User):
            name = user.__class__.__name__
            msg = '%s cannot be %s by %s' % (name, action, self.__class__.__name__)
            raise WrongObjectError(msg)


class MemoryUserRepository(object):
    """User repository class for use in tests. Exposes the same API as the
    DB based one."""

    def __init__(self):
        self.store = {}
        self.count = 0

    def clean(self):
        self.store = {}
        self.count = 0

    def _next_id(self):
        self.count += 1
        return self.count

    def get(self, id):
        return self.store.get(id)

    def get_by_name(self, name):
        users = filter(lambda x: x.name == name, self.store.values())
        return None if len(users) == 0 else users.pop()

    def get_by(self, **attributes):
        users = filter(lambda user: reduce(lambda y, z: y and getattr(user, z) == attributes[z], attributes.keys(), True), self.store.values())
        return None if len(users) == 0 else users.pop()

    def get_all(self):
        return self.store.values()

    def filter_by(self, **filters):
        return filter(lambda user: reduce(lambda y, z: y and getattr(user, z) == filters[z], filters.keys(), True), self.store.values())

    def search_by_name(self, keyword):
        if len(keyword) == 0:
            return []
        match = lambda x: keyword.lower() in x.name.lower() or keyword.lower() in x.fullname.lower()
        matches = filter(match, self.store.values())
        return matches

    def total_users(self):
        return len(self.store.keys())

    def save(self, user):
        self._validate_can_be('saved', user)
        if not user.id:
            user.id = self._next_id()
        self.store[user.id] = user

    def update(self, new_user):
        self._validate_can_be('updated', new_user)
        self.store[new_user.id] = new_user


    def _validate_can_be(self, action, user):
        if not isinstance(user, User):
            name = user.__class__.__name__
            msg = '%s cannot be %s by %s' % (name, action, self.__class__.__name__)
            raise WrongObjectError(msg)
