import sakstig, objectpath, datetime, json, contextlib

@contextlib.contextmanager
def timing():
    start = datetime.datetime.now()
    yield
    end = datetime.datetime.now()
    print("%ss" % (end - start).total_seconds())
    
with open("test.json") as f:
    data = json.load(f)
     
with timing():
    for x in range(0, 1000):
        out = objectpath.Tree(data).execute("$.store.book.*[@.price > $.wanted].price")

query = sakstig.compile("$.store.book.*[@.price > $.wanted].price")
with timing():
    for x in range(0, 1000):
        out = sakstig.Tree(data).execute(query)

