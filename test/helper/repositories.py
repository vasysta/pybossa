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

from pybossa.repositories import MemoryUserRepository
from pybossa.repositories import MemoryProjectRepository
from pybossa.repositories import MemoryBlogRepository
from pybossa.repositories import MemoryTaskRepository

# Memory repositories
memo_user_repo = MemoryUserRepository()
memo_project_repo = MemoryProjectRepository()
memo_task_repo = MemoryTaskRepository()
memo_blog_repo = MemoryBlogRepository()


def clean_all_memory_repos():
    memo_user_repo.clean()
    memo_project_repo.clean()
    memo_task_repo.clean()
    memo_blog_repo.clean()
