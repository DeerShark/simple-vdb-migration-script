## simple-vdb-migration-script

中文 | [English](README_EN.md)

腾讯云向量数据库的简单迁移脚本

### Why this script?

目前腾讯云向量数据库不支持直接数据**迁移**以及数据的**导入导出**，导致当你的数据需要迁移到另一个向量数据库实例时，非常棘手。这个脚本就是就是为了解决这个问题而生的。

### How to use?

1. 安装依赖

```shell
pip install -r requirements.txt
```

2. 修改环境变量配置

打开`example.env`文件，填入你的腾讯云向量数据库实例的相关信息，然后重命名为`.env`

> **注意**，导出端的数据库需要先建好，此脚本不会自动创建数据库。同时导入端的`IMPORT_VDB_REPLICAS`参数为导入端的向量数据库实例的副本数，数量应该是节点数-1，例如导入端有3个节点，那么`IMPORT_VDB_REPLICAS`应该为2

3. 运行脚本

```shell
python script.py
```

### Other

如果有一些输入迁移失败了，会将失败的数据写入到程序目录下的 `error_data.txt` 文件中，你可以方便的查看以及处理