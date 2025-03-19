import pkuseg
# 训练自定义分词模型
def train_custom_model():
    # 准备训练数据
    train_data = [
        ['苹果', '手机', '充电器'],
        ['华为', 'Mate40', 'Pro'],
        ['小米', '数据线'],
        # ... 更多训练数据
    ]

    # 训练参数
    train_config = {
        'train_iter': 20,  # 训练轮数
        'learning_rate': 0.01,
    }

    # 训练模型
    pkuseg.train('train.txt', 'model_path', train_config)

    # 使用训练好的模型
    seg = pkuseg.pkuseg(model_name='model_path')
    return seg


# 使用训练好的模型
trained_seg = train_custom_model()
