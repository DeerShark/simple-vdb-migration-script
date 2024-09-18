## simple-vdb-migration-script

[中文](README.md) | English

Simple migration script for Tencent Cloud Vector Database

### Why this script?

Currently, Tencent Cloud Vector Database does not support direct data **migration** and **import and export** of data, which makes it very difficult when your data needs to be migrated to another vector database instance. This script is designed to solve this problem.

### How to use?

1. Install dependencies

```shell
pip install -r requirements.txt
```

2. Modify environment variable configuration

Open the `example.env` file, fill in the relevant information of your Tencent Cloud Vector Database instance, and rename it to `.env`.

> **Note that** the database on the export side needs to be built first, and this script will not automatically create a database. At the same time, the `IMPORT_VDB_REPLICAS` parameter on the import side is the number of replicas of the vector database instance on the import side, which should be the number of **nodes - 1**. For example, if there are 3 nodes on the import side, then `IMPORT_VDB_REPLICAS` should be 2.

3. Run the script

```shell
python script.py
```

### Other

If some input migration fails, the failed data will be written to the `error_data.txt` file in the program directory, so you can easily view and process it.