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

from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError

from pybossa.model.task import Task
from pybossa.model.task_run import TaskRun
from pybossa.exc import WrongObjectError, DBIntegrityError



class TaskRepository(object):

    def __init__(self, db):
        self.db = db


    # Methods for queries about Task objects
    def get_task(self, id):
        return self.db.session.query(Task).get(id)

    def get_task_by(self, **attributes):
        return self.db.session.query(Task).filter_by(**attributes).first()

    def filter_tasks_by(self, yielded=False, **filters):
        query = self.db.session.query(Task).filter_by(**filters)
        if yielded:
            return query.yield_per(1)
        return query.all()

    def count_tasks_with(self, **filters):
        return self.db.session.query(Task).filter_by(**filters).count()


    # Methods for queries about TaskRun objects
    def get_task_run(self, id):
        return self.db.session.query(TaskRun).get(id)

    def get_task_run_by(self, **attributes):
        return self.db.session.query(TaskRun).filter_by(**attributes).first()

    def filter_task_runs_by(self, yielded=False, **filters):
        query = self.db.session.query(TaskRun).filter_by(**filters)
        if yielded:
            return query.yield_per(1)
        return query.all()

    def count_task_runs_with(self, **filters):
        return self.db.session.query(TaskRun).filter_by(**filters).count()


    # Methods for saving, deleting and updating both Task and TaskRun objects
    def save(self, element):
        self._validate_can_be('saved', element)
        try:
            self.db.session.add(element)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
            raise DBIntegrityError(e)

    def update(self, element):
        self._validate_can_be('updated', element)
        try:
            self.db.session.merge(element)
            self.db.session.commit()
        except IntegrityError as e:
            self.db.session.rollback()
            raise DBIntegrityError(e)

    def delete(self, element):
        self._validate_can_be('deleted', element)
        table = element.__class__
        self.db.session.query(table).filter(table.id==element.id).delete()
        self.db.session.commit()

    def delete_all(self, elements):
        for element in elements:
            self._validate_can_be('deleted', element)
            table = element.__class__
            self.db.session.query(table).filter(table.id==element.id).delete()
        self.db.session.commit()

    def update_tasks_redundancy(self, project, n_answers):
        """update the n_answers of every task from a project and their state.
        Use raw SQL for performance"""
        sql = text('''
                   UPDATE task SET n_answers=:n_answers,
                   state='ongoing' WHERE app_id=:app_id''')
        self.db.session.execute(sql, dict(n_answers=n_answers, app_id=project.id))
        # Update task.state according to their new n_answers value
        sql = text('''
                   WITH project_tasks AS (
                   SELECT task.id, task.n_answers,
                   COUNT(task_run.id) AS n_task_runs, task.state
                   FROM task, task_run
                   WHERE task_run.task_id=task.id AND task.app_id=:app_id
                   GROUP BY task.id)
                   UPDATE task SET state='completed'
                   FROM project_tasks
                   WHERE (project_tasks.n_task_runs >=:n_answers)
                   and project_tasks.id=task.id
                   ''')
        self.db.session.execute(sql, dict(n_answers=n_answers, app_id=project.id))
        self.db.session.commit()


    def _validate_can_be(self, action, element):
        if not isinstance(element, Task) and not isinstance(element, TaskRun):
            name = element.__class__.__name__
            msg = '%s cannot be %s by %s' % (name, action, self.__class__.__name__)
            raise WrongObjectError(msg)


class MemoryTaskRepository(object):
    """Task and taskrun repository class for use in tests. Exposes the same API as the
    DB based one."""

    def __init__(self):
        self.task_store = {}
        self.taskrun_store = {}
        self.task_coun = 0
        self.taskrun_coun = 0

    def clean(self):
        self.task_store = {}
        self.taskrun_store = {}
        self.task_coun = 0
        self.taskrun_coun = 0

    def _next_task_id(self):
        self.task_count += 1
        return self.task_count

    def _next_taskrun_id(self):
        self.taskrun_count += 1
        return self.taskrun_count


    # Methods for queries about Task objects
    def get_task(self, id):
        return self.task_store.get(id)

    def get_task_by(self, **attributes):
        tasks = filter(lambda task: reduce(lambda y, z: y and getattr(task, z) == attributes[z], attributes.keys(), True), self.task_store.values())
        return None if len(tasks) == 0 else tasks.pop()

    def filter_tasks_by(self, yielded=False, **filters):
        tasks = filter(lambda task: reduce(lambda y, z: y and getattr(task, z) == filters[z], filters.keys(), True), self.task_store.values())
        if yielded:
            return (tr for tr in tasks)
        return tasks

    def count_tasks_with(self, **filters):
        return len(self.filter_tasks_by(**filters))


    # Methods for queries about TaskRun objects
    def get_task_run(self, id):
        return self.taskrun_store.get(id)

    def get_task_run_by(self, **attributes):
        taskruns = filter(lambda taskrun: reduce(lambda y, z: y and getattr(taskrun, z) == attributes[z], attributes.keys(), True), self.taskrun_store.values())
        return None if len(taskruns) == 0 else taskruns.pop()

    def filter_task_runs_by(self, yielded=False, **filters):
        taskruns = filter(lambda taskrun: reduce(lambda y, z: y and getattr(taskrun, z) == filters[z], filters.keys(), True), self.taskrun_store.values())
        if yielded:
            return (tr for tr in taskruns)
        return taskruns

    def count_task_runs_with(self, **filters):
        return len(self.filter_task_runs_by(**filters))


    # Methods for saving, deleting and updating both Task and TaskRun objects
    def save(self, element):
        self._validate_can_be('saved', element)
        if isinstance(element, Task):
            if not element.id:
                element.id = self._next_task_id()
            self.task_store[element.id] = element
        if isinstance(element, TaskRun):
            if not element.id:
                element.id = self._next_taskrun_id()
            self.taskrun_store[element.id] = element

    def update(self, element):
        self._validate_can_be('updated', element)
        self.save(element)

    def delete(self, element):
        self._validate_can_be('deleted', element)
        if isinstance(element, Task):
            del self.task_store[element.id]
        if isinstance(element, TaskRun):
            del self.taskrun_store[element.id]

    def delete_all(self, elements):
        for element in elements:
            self.delete(element)

    def update_tasks_redundancy(self, project, n_answers):
        """update the n_answer of every task from a project and their state."""
        tasks = self.filter_tasks_by(app_id=project.id)
        for task in tasks:
            task.n_answers = n_answers
            task.state = 'ongoing'
            taskruns = self.count_task_runs_with(task_id=task.id)
            task.state = 'ongoing' if taskruns < n_answers else 'completed'


    def _validate_can_be(self, action, element):
        if not isinstance(element, Task) and not isinstance(element, TaskRun):
            name = element.__class__.__name__
            msg = '%s cannot be %s by %s' % (name, action, self.__class__.__name__)
            raise WrongObjectError(msg)
