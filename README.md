## 前言
非root环境下frida持久化脚本,过滤掉apk签名效验
# 使用教程：
#### 安装
需要python3  java环境

`pip install lief`

#### 使用方法：
1. python3  LIEFInjectFrida.py source.apk(输入apk) out.apk(输出apk) soname(so名字) -apksign -persistence
2. 编写好自己的frida_script.js hook脚本
3. 推送到手机 adb push frida_script.js  data/local/tmp 
4. 验证 adb logcat -s frida-HOOK 打印出frida启动成功

**具体请关注微信公众号<逆向客栈>**
