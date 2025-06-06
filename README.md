# search
支持window本地  支持docker
商品搜索 目前是将数据库商品 读取 然后进行分词 存储在内存中  适合50万商品以下小型项目使用
部署很简单  直接windows本地就可以运行 方便各位大拿优化 
本人不是后端专业开发 此项目为临时使用 很多地方可以做配置化，可自行修改 如技术问题请自行优化 勿喷
操作步骤
1. 将根目录下的 synonyms.sql 文件导入进去  
2. 修改app\services\search_engine.py 文件中的第66行代码  此处为你的 sql查询  查询结果 要包含 store_name(商品名称) keyword （关键词或者分类标签） spuid(商品id ) zone_rule_id（专区id）后边两个根据业务需求自行调整 自行修改search 方法中return的数据格式 注：此处可做优化  根据自己需求来
3. 修改config文件的 数据连接配置  
4. 然后直接run文件运行就行了
第二步运行的结构要包含这两列数据
![image](https://github.com/user-attachments/assets/d6f82bf9-99df-4260-956b-ca5d623823dc)
不懂得可以咨询vx: liang6483liang
觉得有帮助的可以支持一下
![bc670f7ecf4c0e9427483c86d75e822](https://github.com/user-attachments/assets/977ca337-371f-4b65-b632-7dd7fa62cd98) ![1749180539600](https://github.com/user-attachments/assets/9c2eae2c-5fba-484f-9131-b829f20fe559)
源代码在 master 分支上


