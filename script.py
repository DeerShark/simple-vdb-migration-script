import os
import queue
import threading
import time
from typing import List

import tcvectordb
from loguru import logger
from tcvectordb.model.document import Filter
from tcvectordb.model.enum import ReadConsistency
from tqdm import tqdm

# 导出端vdb
client_export = tcvectordb.RPCVectorDBClient(
    url=os.getenv("EXPORT_VDB_URL"),
    username=os.getenv("EXPORT_VDB_USERNAME"),
    key=os.getenv("EXPORT_VDB_KEY"),
    read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY,
    timeout=30,
)
db_export = client_export.database(os.getenv("EXPORT_VDB_DATABASE"))

# 导入端vdb
client_import = tcvectordb.RPCVectorDBClient(
    url=os.getenv("IMPORT_VDB_URL"),
    username=os.getenv("IMPORT_VDB_USERNAME"),
    key=os.getenv("IMPORT_VDB_KEY"),
    read_consistency=ReadConsistency.EVENTUAL_CONSISTENCY,
    timeout=30,
)
db_import = client_import.database(os.getenv("IMPORT_VDB_DATABASE"))

coll_list = db_export.list_collections()

import_coll_list = [label.collection_name for label in db_import.list_collections()]

# 维护一个队列，用于存储导入端vdb的collection
coll_queue = queue.Queue()


def create_collections():
    # 创建导入端vdb的collection
    with tqdm(total=len(coll_list), desc="create_collections") as create_collection_bar:
        for export_coll in coll_list:
            collection_name = export_coll.collection_name
            # 判断collection是否存在
            if not collection_name in import_coll_list:
                # 创建collection
                db_import.create_collection(
                    name=collection_name,
                    shard=export_coll.shard,
                    replicas=os.getenv("IMPORT_VDB_REPLICAS"),
                    description=export_coll.description,
                    index=export_coll.index,
                    timeout=30,
                )
            coll_queue.put(export_coll.collection_name)
            create_collection_bar.update(1)


def import_data(coll_sum):
    finished_coll = 0
    # 从队列中取出导入端vdb的collection
    while coll_sum > finished_coll:
        if coll_queue.empty():
            time.sleep(0.5)
            continue

        # 获取导入端vdb的collection
        collection_name = coll_queue.get()
        export_coll = db_export.collection(collection_name)

        # 导出端vdb的collection数据
        import_coll = db_import.collection(export_coll.collection_name)
        limit = 20
        with tqdm(total=export_coll.document_count, desc=import_coll.collection_name, leave=False) as import_data_bar:
            for i in range(0, export_coll.document_count, limit):
                # 获取导出端vdb的collection数据
                filter_param = Filter("")
                doc_list = export_coll.query(
                    retrieve_vector=True,
                    filter=filter_param,
                    limit=limit,
                    offset=i,
                )

                # 打印导入的数据
                for doc in doc_list:
                    # 插入导入端vdb的collection数据
                    try:
                        import_coll.upsert([doc])
                    except Exception as e:
                        # 存储失败的数据
                        with open(f"error_data.txt", "a") as f:
                            f.write(f"{collection_name}: {doc}\n")
                        logger.error(f"insert data error: {e}, collection_name: {collection_name}, doc: {doc}")
                    import_data_bar.update(1)

        finished_coll += 1


def main():
    # 打印导出端vdb的collection列表个数
    coll_sum = len(coll_list)
    logger.info(f"export coll list: {coll_sum}")

    # 创建线程
    threads: List[threading.Thread] = [
        threading.Thread(target=create_collections),
        threading.Thread(target=import_data, args=(coll_sum,)),
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
