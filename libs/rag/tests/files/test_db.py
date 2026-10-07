import pytest

import pygenai.rag.files.db as db_mod
from pygenai.rag.files import MongoFileSystemUnitOfWork


class FakeFileObj:
    def __init__(self, _id, filename, metadata, uploadDate, content):
        self._id = _id
        self.filename = filename
        self.metadata = metadata
        self.uploadDate = uploadDate
        self._content = content

    def read(self):
        return self._content


class FakeGridFS:
    def __init__(self):
        self._storage = []
        self._next_id = 1

    def put(self, data, filename=None, metadata=None):
        doc = {
            "_id": self._next_id,
            "filename": filename,
            "metadata": metadata or {},
            "uploadDate": self._next_id,
            "content": data,
        }
        self._storage.append(doc)
        self._next_id += 1
        return doc["_id"]

    def get(self, _id):
        for d in self._storage:
            if d["_id"] == _id:
                return FakeFileObj(d["_id"], d["filename"], d["metadata"], d["uploadDate"], d["content"])
        raise Exception("NotFound")

    def delete(self, _id):
        self._storage = [d for d in self._storage if d["_id"] != _id]


class FakeCursor:
    def __init__(self, docs):
        self._docs = docs
        self._limit = None

    def sort(self, sort_spec):
        # sort_spec like [("uploadDate", -1)]
        key, direction = sort_spec[0]
        reverse = direction < 0
        self._docs.sort(key=lambda d: d.get(key), reverse=reverse)
        return self

    def limit(self, n):
        self._limit = n
        return self

    def __iter__(self):
        docs = self._docs
        if self._limit is not None:
            docs = docs[: self._limit]
        for d in docs:
            yield d


class FakeFilesCollection:
    def __init__(self, gridfs):
        self._gridfs = gridfs

    def find(self, query):
        def matches(d):
            if "filename" in query:
                q = query["filename"]
                if isinstance(q, dict) and "$regex" in q:
                    import re

                    pattern = q["$regex"]
                    return re.match(pattern, d["filename"]) is not None
                else:
                    if d["filename"] != q:
                        return False
            if "metadata.route" in query:
                if d.get("metadata", {}).get("route") != query["metadata.route"]:
                    return False
            return True

        docs = [d for d in self._gridfs._storage if matches(d)]
        return FakeCursor(docs)


class FakeFS:
    def __init__(self, gridfs):
        self.files = FakeFilesCollection(gridfs)


class FakeDB:
    def __init__(self, gridfs):
        self.fs = FakeFS(gridfs)


class FakeMongoClient:
    def __init__(self):
        self._gridfs = FakeGridFS()

    def __getitem__(self, name):
        # return a DB that exposes fs.files.find
        return FakeDB(self._gridfs)


@pytest.fixture(autouse=True)
def fake_mongo_and_gridfs(monkeypatch):
    fake_client = FakeMongoClient()
    # monkeypatch MongoClient to return our fake client
    monkeypatch.setattr(db_mod, "MongoClient", lambda uri=None: fake_client)
    # monkeypatch gridfs.GridFS to return a wrapper around the fake gridfs

    def fake_gridfs(db):
        # ignore db, return the internal FakeGridFS instance
        return fake_client._gridfs

    monkeypatch.setattr(db_mod.gridfs, "GridFS", fake_gridfs)
    return fake_client


def test_db_basic_operations(tmp_path, fake_mongo_and_gridfs):
    uow = MongoFileSystemUnitOfWork(route="root", mongo_uri="fake://", database="db")

    # create text
    assert uow.create_text_file("hello db", "a.txt")
    data = uow.get_file("a.txt")
    assert data == b"hello db"

    # list
    items = uow.list_folder("")
    assert "a.txt" in items

    # upload local file
    src = tmp_path / "f.bin"
    src.write_bytes(b"blobdb")
    assert uow.upload_file(str(src), name="blob.bin")
    assert uow.get_file("blob.bin") == b"blobdb"

    # move
    assert uow.move_file("a.txt", "a2.txt")
    assert uow.get_file("a2.txt") == b"hello db"

    # delete
    assert uow.delete_file("a2.txt")
    with pytest.raises(FileNotFoundError):
        uow.get_file("a2.txt")
