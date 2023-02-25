import tkinter as tk
from viewable import Viewable
from viewstack.error import Error
from viewstack import dto


class ViewStack:
    def __init__(self, container):
        self._container = container
        self._selection = None
        self._views = dict()
        self._history = list()
        self._body_names = set()
        self._setup()

    @property
    def container(self):
        return self._container

    @property
    def selection(self):
        return self._selection

    @property
    def views(self):
        return self._views

    @property
    def history(self):
        return self._history.copy()

    def add(self, name, view):
        """Add a new view (instance of viewable.Viewable)"""
        if not name:
            msg = "You can't add a view without a name"
            raise Error(msg)
        if not isinstance(view, Viewable):
            msg = "The view should be an instance of Viewable"
            raise Error(msg)
        if self._selection:
            self._selection.view.body.grid_remove()
        if name in self._views:
            msg = "The name for this view is already associated with a registered view"
            raise Error(msg)
        body = view.build_grid(self._container, row=0, column=0, sticky="nswe")
        body_name = body.winfo_name()
        if body_name in self._body_names:
            msg = "The widget name of the underlying body of this view is already used by another view: '{}'"
            msg = msg.format(body_name)
            raise Error(msg)
        self._views[name] = view
        self._body_names.add(body_name)
        self._selection = dto.Selection(name, view)

    def lift(self, name):
        """Lift a view"""
        view = self._views.get(name)
        if not view:
            return None
        if self._selection:
            if self._selection.view is view:
                return view
            self._selection.view.body.grid_remove()
        view.body.grid()
        self._selection = dto.Selection(name, view)
        return view

    def hide(self, name):
        """Remove a view"""
        view = self._views.get(name)
        if not view:
            return False
        view.body.grid_remove()
        if self._selection and name == self._selection[0]:
            self._selection = None
        return True

    def destroy(self, name):
        """Destroy a view"""
        view = self._views.get(name)
        if not view:
            return False
        del self._views[name]
        self._body_names.remove(view.body.winfo_name())
        view.body.grid_forget()
        view.body.destroy()
        if self._selection and name == self._selection[0]:
            self._selection = None
        return True

    def _setup(self):
        self._container.rowconfigure(0, weight=1)
        self._container.columnconfigure(0, weight=1)

    def _update_history(self, name):
        for i, item in enumerate(self._history):
            if item == name:
                del self._history[i]
        self._history.insert(0, name)
