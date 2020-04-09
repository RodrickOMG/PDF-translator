# PDF-translator
A PDF translator which can translate English pdf into Chinese pdf. 将英文的PDF翻译并自动生成中文版PDF

## 效果图🚀

![image-20200409170007412](https://tva1.sinaimg.cn/large/00831rSTgy1gdnmeqw8lej310l0u0grh.jpg)

### 文字识别

![](https://tva1.sinaimg.cn/large/00831rSTly1gdnmlsrjitj30u016fb29.jpg)

### 翻译截图

![image-20200409170642103](https://tva1.sinaimg.cn/large/00831rSTly1gdnmlg51k2j30u016h159.jpg)

最后翻译完成并自动生成的PDF文件在result_pdf文件夹中

## 注意⚠️

- 选择文件的按钮很丑，请忽略。更改界面请在main.py中对应代码中进行修改
- 目前只是一个很简陋的版本，经过测试发现会出现文字被覆盖、公式乱码等情况，有时间再想办法解决
- translate.py中一共有三个翻译接口，可以自行选择。其中trans是使用的有道翻译接口；trans2使用的是Google的googletrans中的Translator，但使用久了或者频繁了IP会被封；trans3是用browserdrive的方式打开浏览器自动使用Google翻译，但速度较慢，效率太低。
- 这种翻译出来的PDF其实效果不太理想，既能作为参考，最好的办法还是看原版的文献，万不得已再使用翻译工具。

### Author 🐠

- github@RodrickOMG
- April, 2020