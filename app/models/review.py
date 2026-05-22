from app.services.database import Database

class Review:
    """Review model using Supabase"""
    
    TABLE_NAME = 'reviews'

    @classmethod
    def create(cls, user_id, product_id, rating, comment=None):
        db = Database()
        existing = cls.get_by_user_product(user_id, product_id)
        if existing:
            return cls.update(existing['id'], rating, comment)
        
        data = {
            'user_id': user_id,
            'product_id': product_id,
            'rating': rating,
            'comment': comment
        }
        return db.insert(cls.TABLE_NAME, data)

    @classmethod
    def get_by_id(cls, review_id):
        db = Database()
        return db.select_one(cls.TABLE_NAME, filters={'id': review_id})

    @classmethod
    def get_by_user_product(cls, user_id, product_id):
        db = Database()
        try:
            response = db.client.table(cls.TABLE_NAME).select('*').eq('user_id', user_id).eq('product_id', product_id).execute()
            return response.data[0] if response.data else None
        except:
            return None

    @classmethod
    def get_for_product(cls, product_id):
        db = Database()
        try:
            response = db.client.table(cls.TABLE_NAME).select('*').eq('product_id', product_id).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except:
            return []

    @classmethod
    def update(cls, review_id, rating, comment=None):
        db = Database()
        data = {'rating': rating, 'comment': comment}
        db.update(cls.TABLE_NAME, data=data, filters={'id': review_id})
        return cls.get_by_id(review_id)

    @classmethod
    def delete(cls, review_id):
        db = Database()
        db.delete(cls.TABLE_NAME, filters={'id': review_id})
        return True

    @classmethod
    def get_product_average_rating(cls, product_id):
        db = Database()
        try:
            response = db.client.table(cls.TABLE_NAME).select('rating').eq('product_id', product_id).execute()
            if response.data:
                ratings = [r['rating'] for r in response.data]
                avg = sum(ratings) / len(ratings)
                return {'average': round(avg, 1), 'count': len(ratings)}
            return {'average': 0, 'count': 0}
        except:
            return {'average': 0, 'count': 0}
