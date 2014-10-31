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
# Cache global variables for timeouts

""" This package exports the following repository classes as an abstraction
layer between the ORM and the application:

    * ProjectRepository
    * UserRepository
    * BlogRepository
    * TaskRepository

The responsibility of these repositories is only fetching one or many objects of
a kind and/or saving them to the DB by calling the ORM apropriate methods.

For more complex DB queries, refer to other packages or services within PyBossa.


Also, it exports repository classes that expose the same API than the previous
ones but use in-memory storage (actually, dicts) and does not use any ORM or
databases at all.
These classes are meant to be used in tests only, and are the following:

    * MemoryProjectRepository
    * MemoryUserRepository
    * MemoryBlogRepository
    * MemoryTaskRepository
"""

from project_repository import ProjectRepository, MemoryProjectRepository
from user_repository import UserRepository, MemoryUserRepository
from blog_repository import BlogRepository, MemoryBlogRepository
from task_repository import TaskRepository, MemoryTaskRepository
