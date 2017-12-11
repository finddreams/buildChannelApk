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
