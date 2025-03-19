class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

    @staticmethod
    def from_db_row(row):
        return {
            'id': row['id'],
            'name': row['store_name'],
            'price': float(row['price'])
        }
