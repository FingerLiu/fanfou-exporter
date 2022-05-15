# fanfou-exporter

使用浏览器 cookie 将饭否时间线导出至 Excel 文件。

```bash
git clone https://github.com/FingerLiu/fanfou-exporter.git
cd fanfou-exporter
pip install -r requirements.txt
./fanfou-exporter.py --help
./fanfou-exporter.py --homepage "https://fanfou.com/bitcher" --cookie "__utmc=208515845; xxxxx..."
```

## 获取 homepage 的方法
1. chrome 浏览器打开饭否，点击右侧的“消息”
2. 复制地址栏中的地址

## 获取 cookie 的方法
1. chrome 浏览器打开饭否，点击右侧的“消息”
2. 在页面空白处单击鼠标右键，选择“检查”
3. 点击网络 --> 文档 --> 标头,然后向下滚动至“请求标头”
4. 复制 "Cooke: " 后的那一串字符，如“__utmc=208515845; __utmz=208515845.1648xxx”
如图所示


[get-cookie](https://raw.githubusercontent.com/FingerLiu/fanfou-exporter/main/imgs/get-cookie.png)