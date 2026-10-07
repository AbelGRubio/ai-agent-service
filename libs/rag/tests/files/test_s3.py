import io

import pytest

import pygenai.rag.files.s3 as s3_mod
from pygenai.rag.files.s3 import S3FileSystemUnitOfWork


class FakeS3Client:
    def __init__(self):
        # storage: {(bucket,key): bytes}
        self.storage = {}

    def upload_fileobj(self, fileobj, bucket, key):
        fileobj.seek(0)
        self.storage[(bucket, key)] = fileobj.read()

    def delete_object(self, Bucket, Key):
        self.storage.pop((Bucket, Key), None)

    def get_object(self, Bucket, Key):
        if (Bucket, Key) not in self.storage:
            raise Exception("NoSuchKey")
        return {"Body": io.BytesIO(self.storage[(Bucket, Key)])}

    def list_objects_v2(self, Bucket, Prefix):
        keys = [k for (b, k) in self.storage.keys() if b == Bucket and k.startswith(Prefix)]
        contents = [{"Key": k} for k in keys]
        return {"Contents": contents} if contents else {}

    def copy_object(self, Bucket, CopySource, Key):
        src_bucket = CopySource["Bucket"]
        src_key = CopySource["Key"]
        data = self.storage.get((src_bucket, src_key))
        if data is None:
            raise Exception("SourceNotFound")
        self.storage[(Bucket, Key)] = data

    def upload_file(self, file_route, Bucket, Key):
        with open(file_route, "rb") as f:
            self.storage[(Bucket, Key)] = f.read()


@pytest.fixture(autouse=True)
def fake_boto3_client(monkeypatch):
    fake = FakeS3Client()

    def fake_client(*args, **kwargs):
        return fake

    monkeypatch.setattr(s3_mod, "boto3", type("B", (), {"client": staticmethod(fake_client)}))
    return fake


def test_s3_basic_operations(tmp_path, fake_boto3_client):
    bucket = "test-bucket"
    uow = S3FileSystemUnitOfWork(route="", bucket=bucket)

    # create text file
    assert uow.create_text_file("hello s3", "a.txt")
    assert fake_boto3_client.storage[(bucket, "/a.txt")] == b"hello s3"

    # get file
    assert uow.get_file("a.txt") == b"hello s3"

    # list folder
    items = uow.list_folder("")
    assert "a.txt" in items

    # upload local file
    src = tmp_path / "f.bin"
    src.write_bytes(b"blob")
    assert uow.upload_file(str(src), name="blob.bin")
    assert fake_boto3_client.storage[(bucket, "/blob.bin")] == b"blob"

    # move file
    assert uow.move_file("a.txt", "a2.txt")
    assert (bucket, "/a.txt") not in fake_boto3_client.storage
    assert (bucket, "/a2.txt") in fake_boto3_client.storage

    # delete file
    assert uow.delete_file("a2.txt")
    assert (bucket, "/a2.txt") not in fake_boto3_client.storage
