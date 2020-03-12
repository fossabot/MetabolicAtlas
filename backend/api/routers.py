class GemodelRouter(object):
    def db_for_read(self, model, **hints):
        if model.__name__ in ['GEModelSet', 'GEModelSample', 'GEModelReference', 'GEModelFile',
         'GEModel', 'GEM', 'GEMAuthor', 'GEMreference', 'Author']:
            return 'gems'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ in ['GEModelSet', 'GEModelSample', 'GEModelReference', 'GEModelFile', 'GEModel',
         'GEM', 'GEMAuthor', 'GEMreference', 'Author']:
            return 'gems'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1.__class__.__name__ in ['GEModelSet', 'GEModelSample', 'GEModelReference',
         'GEModelFile', 'GEModel', 'GEM', 'GEMAuthor', 'GEMreference', 'Author']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name in ['gemodelset', 'gemodelsample', 'gemodelreference', 'gemodelfile',
         'gemodel', 'gem', 'gemauthor', 'gemreference', 'author']:
            return db == 'gems'
        return None

class ApiRouter(object):
    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db != 'gems'
