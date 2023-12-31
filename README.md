# word2anki

使用 Bing 词典查询单词并制作 Anki 牌组。包含美式发音（需联网）、中文释义、变形。

⚠️ 不保证 Bing API 一直可用，在替换为自己申请的 API 前请勿将本项目用于任何盈利用途。

<p align="center"><img src="./assets/card.png" alt="card preview" width="400px" /></p>

## 如何使用

1. Python3.6+，安装依赖：

```shell
pip3 install requests genanki tqdm
```

2. 将单词填入 `words.txt`，每行一个
3. 运行 `python3 main.py`。将生成的 `build/*.apkg` 文件导入进 anki

## 详细说明

缓存：

- 单词的查询结果会被完整缓存在 `build/cache/*.json` 中
- 生成卡片时优先使用缓存，如果需要最新数据、部分单词解析出现问题等，请删除对应单词的缓存文件再重新构建

牌组：

- 生成不同牌组时，请及时修改 `main.py` 顶部的配置，比如牌组名称和 ID 等，避免与已有牌组重复

Bing API：

- 不保证一直可用
- 删除 `mkt=zh-cn` 参数即可获得来自牛津词典的纯英文数据，但结构可能有所不同，请自行修改解析逻辑
