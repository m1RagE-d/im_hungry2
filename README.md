# im_hungry

## **'What to do's**  


### 功能目标：  
  （1）根据profile决定吃什么（菜谱）  
  （2）根据input query决定吃什么（菜谱）  
  （3）根据input query preference推荐附近的餐厅（结合googlemap数据）  

所以  
建立profile  
  - [ ] Structure  
  - [ ] 什么information是重要的  
  - [ ] $${\color{red}钉死的选项}$$  
  - [ ] $${\color{red}弹性的选项}$$ [OFF](https://github.com/openfoodfacts/openfoodfacts-server/tree/main/taxonomies)  
数据库  
  - [ ] 菜谱  
    - 下厨房  
    - neurodivergent的个性化菜谱网站  
    - $${\color{red}标签}$$  
  - [ ] Google Map或者餐厅  
    - 位置信息？  
搜索匹配算法  
  - [ ] llm  
    - local？API？  
  - [ ] hard-coded filters (SQL + pgvector)  


## **Groceries**

material
    allergies
equipment
    electricity
    non-electronic
time
distance
nutrition
style
region
Price
wants
no-gos

先根据比较常见的配方写一版内置的一些标签，如果用户在Profile上加了一些额外的东西，然后再用llm运算

根据用户的喜好建一个更细的profile。比如说，我也是那几天在筛选tag的时候才看见，有些地方番茄炒蛋里面好像是会放肉的，然后所以就可能会导致一些忌口上这个食物的标记会不一样

---
## Feb 4, 2026
~~增加了一些内容但是有点没太懂那个后端（挠头）我明天（今天）上班摸鱼的时候研究一下。~~
已修改。之前的版本太简陋了，现在更新了一些接入api处理数据的方法。做成一个独立的完整app。

## 📂 文件说明 (File Structure)
请按照以下说明使用：
### 准备数据 (Pipeline)：
1. 准备工作 (Backend Setup)
你需要安装库，用来连接地图服务。 在终端运行：

```Bash
pip install fastapi uvicorn google-generativeai googlemaps pywebview
```
替换 Key： 把 main.py 第 25 行的 YOUR_GOOGLE_API_KEY_HERE 换成真实的 Key。

2. 准备数据： 确保你的文件夹里已经生成了 vibe_food.db (通过运行之前的 pipeline 脚本)。

3. 运行！： 直接在终端输入 python3 main.py，或者使用我们做的 Automator 图标。

ldd's to do list:
- [ ] 查看一下render
```
https://dashboard.render.com/register
```
- [ ] 搭建平台
- [ ] 测试软件，调整UI/UX部分
- [ ]思考token usage（提交时可以带url，但是如果给public test怎么控制cost）

## Feb 6, 2025
~~https://dashboard.render.com/register 这个玩意儿好麻烦一直在卡我银行卡，换一个免费的~~
现在打算试试huggingface.co。
