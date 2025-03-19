import pkuseg

seg = pkuseg.pkuseg()           # 以默认配置加载模型
text = seg.cut('我爱北京天安门')  # 进行分词
print(text)


# import pkuseg
#
# seg = pkuseg.pkuseg(model_name='medicine')  # 程序会自动下载所对应的细领域模型
# text = seg.cut('我爱北京天安门')              # 进行分词
# print(text)
