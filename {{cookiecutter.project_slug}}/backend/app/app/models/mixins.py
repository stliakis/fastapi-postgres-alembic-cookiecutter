from sqlalchemy.orm.attributes import flag_modified

from app.utils.base  import merge
from app.utils.jstruct import JStruct


class ExtrasHolderMixin():

    @property
    def extras(self):
        return JStruct(self._extras or {})

    def update_extras(self, extras):
        self._extras = merge(self._extras or {}, extras)
        flag_modified(self, "_extras")
        return self
