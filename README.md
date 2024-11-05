# Finance-method
##
首先在服务器上安装MiniAnaconda，使用命令  

```wegt https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh```  

下载好后，使用bash命令运行  

```bash Miniconda3-latest-Linux-x86_64.sh```  

安装完后需要重新打开shell  
创建一个新的环境（python指定使用3.7版本）  

```conda create -n env python=3.7```  

激活刚刚的新环境  

```conda activate env```  

在新环境中安装numpy和pandas库  
```
  conda install numpy
  conda install pandas
```
拉取项目：  
```
git pull https://github.com/FoxLawrence/Finance-method.git main
```
SFTP：
```
sftp root@120.78.126.249
```
获取服务器上的文件：
```
get -r stock/Finance-method/merged_data.csv /Users/wangzhongjie/Desktop/大湾区
```

##
