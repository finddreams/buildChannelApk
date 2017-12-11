> 此文属于finddreams的原创博客，转载请注明出处：http://blog.csdn.net/finddreams/article/details/78773687

&emsp;&emsp;由于Android应用市场的多样性,运营人员为了统计App在各应用市场的下载量，通常会要求Android的APP包要能够根据不同的应用市场打出对应的带这个渠道的apk，这就成了Android团队打包发布的任务之一——打渠道包。

&emsp;&emsp;记得一年以前，我们项目中的打包方式是使用Gradle中的productFlavors配置来打渠道包,配置不同渠道的flavors信息

```
    productFlavors {
        xiaomi {
            manifestPlaceholders = [UMENG_CHANNEL_VALUE: "xiaomi"]
        }
        _360 {
            manifestPlaceholders = [UMENG_CHANNEL_VALUE: "360"]
        }
        test {
           packageName "com.example.test"
        }
```

&emsp;&emsp;然后通过不同的flavor配置来动态的替换掉AndroidManifest.xml中预定义的参数UMENG_CHANNEL_VALUE，来实现友盟的多渠道统计功能。

```

<meta-data
            android:name="UMENG_CHANNEL"
            android:value="${UMENG_CHANNEL_VALUE}"/>

```

&emsp;&emsp;使用 productFlavors 来实现多渠道的方式的

&emsp;&emsp;优点是可以定制不同的风格,比如不同包名，版本号，不同的appname，不同的ic_launcher等，可以打出两个不同环境的apk安装到手机上。

&emsp;&emsp;缺点就是如果只是用在打渠道包这个功能上，那就是牛刀杀鸡大材小用了，因为每打出一个渠道包就要重新的编译运行一遍，如果是一两个到无所谓，到要是十个以上就有罪可受了。

&emsp;&emsp;当时我们的apk大小是十几兆，用这种方式打五个渠道包，要花上半个小时以上的时间，真心的低效，不够优雅。

&emsp;&emsp;另外使用productFlavors来打包出渠道apk，使用Tinker这种热修复框架也不友好，因为productFlavors打出来的apk其实已经是两个不同的apk了，发布补丁的时候，可以会出现不同的结果，所以这种方式也不是微信Tinker 官方推荐的打渠道包方式。

&emsp;&emsp;新一代渠道包打包神器 Walle
----------------------------

&emsp;&emsp;它是美团点评技术团队开源的，号称 Android Signature V2 Scheme签名下的新一代渠道包打包神器。地址：https://github.com/Meituan-Dianping/walle Walle是Tinker官方推荐的打渠道包方式，因为打出的渠道包apk 本质上是同一个包，有兴趣的同学可以去看看这篇文章[《新一代开源Android渠道包生成工具Walle》](https://tech.meituan.com/android-apk-v2-signature-scheme.html) 了解什么是Android Signature V2 Scheme签名，Walle打包的原理。

&emsp;&emsp;关于Walle的如何使用不是本文要讲述的内容，因为官方的文档讲解的非常详细，正如本文的标题所揭示的主题一样，

&emsp;&emsp;本文的主要目的是帮助那些使用了360加固同时又使用Walle来打渠道包的开发人员，实现360加固之后，一键V2签名和打出渠道包。

&emsp;&emsp; 可能有人会问360加固不是都支持自动签名和打出渠道包吗，为什么还要这么麻烦用Walle?

&emsp;&emsp;1.首先360加固的自动签名是基于V1的，而使用walle来打渠道包只能是针对用V2签名的apk;

&emsp;&emsp;2.360加固打出的渠道包，是只针对有限几个的统计平台进行适配，比如说友盟，也就是在AndroidManifest.xml中插入 meta-data标签来实现不同渠道的替换，不够灵活。

```

<meta-data
            android:name="UMENG_CHANNEL"
            android:value="${UMENG_CHANNEL_VALUE}"/>

```

&emsp;&emsp; 下面我们目前使用的python脚本方式来实现这一系列无脑而又繁琐的操作，一键的签名和打渠道包。
&emsp;&emsp; build_channel_window.py 来调用cmd命名来实现。

&emsp;&emsp;build_channel_window.py 的具体代码如下(目前只适配了window，需要安装python的sdk）：

```
import os

version = "1.0.0"  # 版本号
channelOutFile = "1.0.0"  # 输出的渠道文件名
buildToolFile = "E:/sdk/build-tools/26.0.2"  #sdk 编译环境的位置
unSignApkName = "app-release.apk"  # 360加固之后没有签名的apk
apkName = "App_" + version + ".apk"  # 签名之后的名称
keyStoreName = "andmodule.jks"  # 签名文件的名称
apkFile = os.path.dirname(os.path.realpath(__file__))+"/"  # 获取到当前py文件的父目录

os.chdir(buildToolFile)

zipResult = os.system("zipalign -v -f 4 "+apkFile+unSignApkName+" " + apkFile+apkName)
print(zipResult)

if zipResult == 0:
    print("zipalign成功")
else:
    print("zipalign失败")
    exit(1)
signPath=  "apksigner sign --ks " +apkFile+"andmodule.jks --ks-key-alias finddreams --ks-pass pass:finddreams --key-pass pass:finddreams " + apkFile+apkName
print(signPath)
signResult = os.system(signPath)
print(signResult)

if signResult == 0:
    print("sign成功")
else:
    print("sign失败")
    exit(1)

os.chdir(apkFile)
checkResult = os.system("java -jar CheckAndroidV2Signature.jar " + apkName)
print(checkResult)
if checkResult == 0:
    print("已成功签名")
else:
    print("没有签名成功")
    exit(1)

channelResult = os.system("java -jar walle.jar batch -f channel  " + apkName + " " + channelOutFile)
print(checkResult)

if channelResult == 0:
    print("已生成渠道包")
else:
    print("生成渠道包失败")
    exit(1)
```

&emsp;&emsp;调用这个脚本的方法

```
python build_channel_window.py
```

&emsp;&emsp;使用了python脚本之后，省掉了很多之前的命令行重复劳动，一句命令就可以达到以前需要写好几句的效果，而且出现的错误也减少了，又提高了效率。

&emsp;&emsp;脚本的具体步骤说明：

&emsp;&emsp;首先我们从360加固之后的未签名的包先要进行zipalign来实现res资源的对齐，然后使用apksigner签名工具来实现apk的V2签名，因为在window下这些工具都是在Android SDK的build-tools目录下，所以先要把工作目录切换build-tools，因为每个人电脑的sdk目录都不一样所以做成可配置的。

&emsp;&emsp;签名成功之后使用CheckAndroidV2Signature.jar来检查是否是V2签名，然后调用walle.jar 来生成渠道包；

&emsp;&emsp;渠道信息都在 channel 文件里面,如果需要生成其他渠道只需要添加到 channel 文件中即可，使用 walle打渠道包的速度是非常快的，一秒就可以生成了。

```
android_360app # 360
android_tencent #腾讯应用宝
android_xiaomi #小米
android_meiZu  #魅族
android_huaWei #华为
android_baidu  #百度
android_wanDouJia  #豌豆荚
android_samsung  #三星
android_oppo     #oppo
android_mumayi   #木蚂蚁
android_anzhi    #安智
android_sougou   #搜狗
```


&emsp;&emsp;这个脚本执行的结果如下：

&emsp;&emsp;![这里写图片描述](http://img.blog.csdn.net/20171211163612681?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvZmluZGRyZWFtcw==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

&emsp;&emsp; 最后附上这些打包渠道资源的github地址：https://github.com/finddreams/buildChannelApk
