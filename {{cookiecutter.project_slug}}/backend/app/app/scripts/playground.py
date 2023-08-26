from sqlalchemy import or_, Unicode

from app.core.recommendation_engine.collaborative.collaborative_engine import CollaborativeEngine
from app.core.recommendation_engine.recommender import Recommender
from app.core.recommendation_engine.types import RecommendationConfig, CollaborativeRecommendationConfig
from app.models.models_proxy import m
from app.db.session import SessionLocal
from app.models import Person, Collection

db = SessionLocal()

rc = Recommender(
    collection=Collection.objects().get("420815143014"),
    config=RecommendationConfig(
        collaborative=CollaborativeRecommendationConfig(
            user_id="06"
        )

    )
)

print(rc.recommend())

# col = CollaborativeEngine(Collection.objects().get("420815143014"))


# print(col.get_item_ids_of_person("00"))


#
# print(col)
# print("ASdasdasd")
# persons = m.Person.objects(db).filter(or_(
#     Person.external_id.ilike("%short%"),
#     Person.fields.cast(Unicode).ilike("%short%"),
# ))

# print("asd")
# for p in persons:
#     print(p)


# creator = EventsBulkCreator(db)
#
# settings.is_testing()
#

# EventRequestConsumer.execute(
#     [
#         {
#             "event_type": "type1",
#             "person_id": "person1",
#             "item_id": "item1",

#             "collection_id": 468594186415,
#         }
#     ],
#     db=db, use_async=False
# )
#
# creator.flush()

# print(m.Collection.objects(db).filter().all())

# with Database() as db:
#     print(db.execute("""
#     delete from event where created < now() - INTERVAL '7 days'
#     """))

# print("asd:",ItemsField.objects(db).get(159176836194).collection)

# CollectionPopularityBucket(Collection.objects(db).get(767784492414)).record_event({
#     "test": "name"
# })

# rdb = get_redis()
#
# rdb.zadd("test", {"valuee": time.time()})
# rdb.zadd("test", {"valuee3": time.time()})
# rdb.zadd("test", {"valuee5": time.time()})
# rdb.zadd("test", {"valuee6": time.time()})
# rdb.zadd("test", {"valuee4": time.time()})
# rdb.zadd("test", {"valuee8": time.time()})
#
# print(rdb.zpopmin("test",10))
#

# for i in range(1):
#     ItemRequestConsumer.execute({
#         "_key": random.randint(0, 1000000),
#         "collection_id": "12323",
#         "item_id": "12345",
#         "fields": {
#             "name": "test",
#             "genre": ["yo"]
#         }
#     }, execute_after=5)

# recommender = ItemToItemsRecommender(
#     collection=Collection.objects(db).get(767784492414), external_item_id="10470378"
# )
#
# recommendation = recommender.recommend(filters={
#     "category": "15424",
#     "engine_power": {
#         "gte": 100
#     }
# })


# print("ASdsad", recommendation.items)
#
#
#
# """
# The following produces a table with 3 columns
#
# [date]  [sum of invoices net_value with price>=150 & product_category!=hat] [count of unique customers that were invoiced for product_category=shoes]
# """
#
# interpreter = PQLInterpreter(bucket, {
#     "histogram": {
#         "interval": "1d",
#         "dimensions": [
#             {
#                 "data": {
#                     "sum": "net_value"
#                 },
#                 "filters": {
#                     "not": {
#                         "product_category": "hat"
#                     },
#                     "price": {
#                         "gte": 150
#                     }
#                 }
#             },
#             {
#                 "data": {
#                     "cardinality": "customer"
#                 },
#                 "product_category": "shoes"
#             }
#         ]
#     },
#     "period": "5"
# })
#
# prid(interpreter.execute())

#
# print("sad2:", User.objects().get_by_email("admin@kvp.com"))
#
#
#
# bucket = PopularityBucket("playground_bucket")
#
# bucket.delete_current_partition()
#
# add_shop_test_data_to_bucket(bucket)
#
# interpreter = PQLInterpreter(bucket, {
#     "histogram": {
#         "interval": "1d",
#         "dimensions": [
#             {
#                 "data": {
#                     "sum": "net_value"
#                 },
#                 "filters": {
#                     "not": {
#                         "product_category": "hat"
#                     },
#                     "price": {
#                         "gte": 150
#                     }
#                 }
#             },
#             {
#                 "data": {
#                     "cardinality": "customer"
#                 },
#                 "product_category": "shoes"
#             }
#         ]
#     },
#     "period": "5"
# })
#
# prid(interpreter.execute())
