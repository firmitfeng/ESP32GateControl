class KeyDB():
    FILE = 1
    UDP = 2
    TCP = 4
    SQLITE = 16

    def __init__(self, path=None, db_type=None):
        self.path = path
        if db_type is None:
            self.type = self.FILE
        self.is_change = False
        self.db = self.open()

    def __del__(self):
        if self.is_change:
            self.save()

    def save(self):
        if self.is_change:
            if self.type == self.FILE and self.path is not None:
                with open(self.path, 'w') as f:
                    # content = '\n'.join([str(i).strip() for i in self.db])
                    f.write('\n'.join([i.strip() for i in self.db if i]))
            self.is_change = False

    def open(self, mode='r'):
        content = []
        if self.type == self.FILE and self.path is not None:
            with open(self.path, mode) as f:
                content = f.read()
                content = [s.strip() for s in content.split('\n') if s]
        return content

    def initDB(self):
        print('init KeyDB')

    def put(self, val):
        val = str(val)
        val = val.strip('\n').strip()
        if val:
            self.db.append(val)
            self.is_change = True
        # print('put', val)

    def remove(self, val):
        val = str(val)
        val = val.strip('\n').strip()
        if val in self.db:
            self.db.remove(val)
            self.is_change = True
        # print('remove', val)

    def empty(self):
        self.db = []
        self.is_change = True
        # print('empty')

    def query(self, val):
        val = str(val)
        val = val.strip('\n').strip()
        return val in self.db

    def show(self):
        print(self.db)


if __name__ == '__main__':
    db = KeyDB('test.db')
    db.initDB()
    db.put('123123123')
    db.put('asdasd')
    db.put('')
    db.put(-22)
    print(db.query('123123123'))
    print(db.query('123'))
    db.show()
    db.empty()
    db.save()
    
