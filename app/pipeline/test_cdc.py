from pymongo import MongoClient


def insert_data_to_mongodb(uri, database_name, collection_name, data):
    """
    Insert data into a MongoDB collection.

    :param uri: MongoDB URI
    :param database_name: Name of the database
    :param collection_name: Name of the collection
    :param data: Data to be inserted (dict)
    """
    client = MongoClient(uri)
    db = client[database_name]
    collection = db[collection_name]

    try:
        result = collection.insert_one(data)
        print(f"Data inserted with _id: {result.inserted_id}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    insert_data_to_mongodb(
        "mongodb+srv://galleons777:galleons@cluster0.b1w6ev1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
        "scrabble",
        "posts",
        {"platform": "linkedin", "content": "Test content"}
    )
