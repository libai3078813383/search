class Config:
    MYSQL_CONFIG = {
        'host': 'pc-bp10t7s47hgv1e3wu.rwlb.rds.aliyuncs.com',
        'user': 'py',
        'password': 'py@168520',
        'database': 'crmeb'
    }

    STOP_WORDS = set(['的', '了', '和', '与', '等', '是'])

    USER_DICT = [
        "iPhone13", "Type-C", "充电器", "数据线", "手机壳",
        "华为", "小米", "苹果", "三星", "OPPO",
        "Pro", "Max", "Plus", "5G"
    ]
