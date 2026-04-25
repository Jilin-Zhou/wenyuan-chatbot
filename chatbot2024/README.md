# 文渊机器人知识库+大模型对话后端

本项目是基于flask构建的知识库+大模型对话系统后端
## 安装依赖
请在python 3.10环境下运行，并在终端中执行下面的命令以初始化项目依赖

```powershell
pip install -r requirements.txt
```

## 配置环境变量
项目中使用openai的chat API和embeddings API

需要对应地配置环境变量`OPENAI_BASE_URL`和`OPENAI_API_KEY`

由于不同操作系统和终端上配置环境变量的方法不同，此处请自行配置

## 构建词向量数据库（可选）
项目使用sqlite构建词向量知识库(QA.db)

若要修改词向量，请编写excel文件设置问答

excel文件命名需以`.xlsx`结尾，格式如下：

| questions | answers |
|:---------:|:-------:|
|北京有哪些好玩的地方?|北京不仅有故宫、长城、天安门、颐和园等名胜古迹，也有奥林匹克公园、798艺术区等现代旅游胜地，只等您来|
|去哪里买北京伴手礼比较好？|去东四一路向北还有前门大街可以买大部分北京有名的伴手礼和特产！当然还能打卡特色美食，快去逛一逛吧|

编写后将`your_QA.xlsx`放入`/static`文件夹

运行如下命令，执行`embedding.py`文件构建词向量数据库：
```powershell
python chat\embedding.py
```

## 启动服务

完成上述操作后，执行命令启动服务：

此处的运行端口`1090`可根据需要自行修改
```powershell
python app.py --port 1090
```
