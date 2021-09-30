import argparse
import os
import shutil
import zipfile
import lief


class LIEFInject:
    def __init__(self, args):
        has_lib = False
        with zipfile.ZipFile(args.input, 'r') as apk_file:
            for item in apk_file.infolist():
                if item.filename.endswith(".so"):
                    has_lib = True
                    break
        if not has_lib:
            print('apk can\'t find so')
            exit(1)
        self.apkpath = args.input
        self.outdir = args.output
        self.soname = args.soname
        self.deletelist = []
        self.toolPath = os.getcwd() + r"/tools"

    def injectso(self):
        injectsolist = []
        with zipfile.ZipFile(self.apkpath, 'r') as apk_file:
            for item in apk_file.infolist():
                if item.filename.find(self.soname) != -1:
                    apk_file.extract(item.filename)
                    self.deletelist.append(item.filename)
                    injectsolist.append(item.filename)
        # x86有一点问题，且不支持x86_64
        for soname in injectsolist:
            # if soname.find("x86_64") != -1:
            if soname.find("x86") != -1:
                continue
            so = lief.parse(os.getcwd() + "/" + soname)
            so.add_library("libfrida-gadget.so")
            so.write(soname + "gadget.so")

    def modifyapk(self):
        (path, filename) = os.path.split(self.apkpath)
        (file, ext) = os.path.splitext(filename)
        outapk = os.path.join(self.outdir, file + "_frida.apk")
        with zipfile.ZipFile(self.apkpath, 'r') as orig_file:
            with zipfile.ZipFile(outapk, 'w') as out_file:
                for item in orig_file.infolist():
                    if item.filename.find(self.soname) != -1 and os.path.exists(
                            os.getcwd() + "/" + item.filename + "gadget.so"):
                        out_file.write(os.getcwd() + "/" + item.filename +
                                       "gadget.so", arcname=item.filename)
                        if item.filename.find("lib/armeabi-v7a") != -1:
                            out_file.write(os.path.join(self.toolPath, "frida-gadget-14.2.18-android-arm.so"),
                                           arcname="lib/armeabi-v7a/libfrida-gadget.so")
                            print("add lib/armeabi-v7a/libfrida-gadget.so")
                        if item.filename.find("lib/arm64-v8a") != -1:
                            out_file.write(os.path.join(self.toolPath, "frida-gadget-14.2.18-android-arm64.so"),
                                           arcname="lib/arm64-v8a/libfrida-gadget.so")
                            print("add lib/arm64-v8a/libfrida-gadget.so")
                        if item.filename.find("lib/x86/") != -1:
                            out_file.write(os.path.join(self.toolPath, "frida-gadget-14.2.18-android-x86.so"),
                                           arcname="lib/x86/libfrida-gadget.so")
                            print("add lib/x86/libfrida-gadget.so")
                        continue
                    if item.filename.find("META-INF") == -1:
                        out_file.writestr(item, orig_file.read(item.filename))

        shutil.rmtree("lib")
        print("注入完毕")
        return outapk

    def addHook(self, apk_path):
        with zipfile.ZipFile(apk_path, 'a') as apk_file:
            for item in apk_file.infolist():
                if item.filename == "lib/armeabi-v7a/libfrida-gadget.so":
                    apk_file.write(os.path.join(self.toolPath, "libfrida-gadget.config.so"),
                                   arcname="lib/armeabi-v7a/libfrida-gadget.config.so")
                    print("add lib/armeabi-v7a/libfrida-gadget.config.so")
                if item.filename == "lib/arm64-v8a/libfrida-gadget.so":
                    apk_file.write(os.path.join(self.toolPath, "libfrida-gadget.config.so"),
                                   arcname="lib/arm64-v8a/libfrida-gadget.config.so")
                    print("add lib/arm64-v8a/libfrida-gadget.config.so")
                if item.filename == "lib/x86/libfrida-gadget.so":
                    apk_file.write(os.path.join(self.toolPath, "libfrida-gadget.config.so"),
                                   arcname="lib/x86/libfrida-gadget.config.so")
                    print("add lib/x86/libfrida-gadget.config.so")
                continue

    def signApk(self, apk_path):
        keystore = os.path.join(self.toolPath, 'APPkeystore.jks')
        alias = 'key0'
        pswd = 'qwer1234'
        aliaspswd = 'qwer1234'

        apkname = os.path.splitext(os.path.split(apk_path)[1])[0]
        outfile = os.path.join(os.path.split(apk_path)[
            0], apkname + "_Signed.apk")

        cmd = 'java -jar %s/apksignerNew.jar sign --ks %s --ks-key-alias %s --ks-pass pass:%s --key-pass pass:%s --out %s %s' % \
              (self.toolPath, keystore, alias, pswd, aliaspswd, outfile, apk_path)
        # print(cmd)
        os.system(cmd)

    def signApk2(self, apk_path):
        """
        读取原apk签名 hook掉签名验证
        """
        apkname = os.path.splitext(os.path.split(apk_path)[1])[0]
        outfile = os.path.join(os.path.split(apk_path)[
            0], apkname + "_Signed.apk")
        write_str = """
            # 获取签名信息
            apk.signed={}
            
            # 要处理的APK
            apk.src={}
            
            # 写出的APK名
            apk.out={}
            
            # 签名配置
            sign.enable=true
            sign.file={}/test.keystore
            sign.password=123456
            sign.alias=user
            sign.aliasPassword=654321
        """.format(args.input, apk_path, outfile, self.toolPath)

        with open("config.txt", 'w', encoding="utf8") as f:
            f.write(write_str.replace("\\", "/"))

        cmd = 'java -jar %s/nkstool.jar' % self.toolPath

        # print(cmd)
        os.system(cmd)
        os.remove("config.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help="apk path")
    parser.add_argument('output', help="Folder to store output files")
    parser.add_argument('soname', help="the so name of apk first load  ")
    parser.add_argument('-apksign', help="Sign apk", action='store_true')
    parser.add_argument(
        '-persistence', help="HOOK Persistence ", action='store_true')

    args = parser.parse_args()
    liefs = LIEFInject(args)
    liefs.injectso()
    out = liefs.modifyapk()
    if args.persistence:
        liefs.addHook(out)
    if args.apksign:
        # liefs.signApk(out)
        # 读取原apk签名 hook掉签名验证
        liefs.signApk2(out)

    print(u"sucess, new apk :" + out)
