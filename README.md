###说明

1.
2.采用sqlite来管理dlib产生的已知面部矩阵和用户数据，密码存储依然采用pickle存储
3.将file.py 替换为dboperation.py，并且去除了file.py
4.移除了文件夹encogings 和 faceinfo,因为采用了数据库(database目录)统一管理所以去掉了
5.还移除了一些不必要的零碎文件
