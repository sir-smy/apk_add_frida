Java.perform(function () {
  var Log = Java.use("android.util.Log");
  Log.i("frida-HOOK","frida启动成功");
  // var hook_class = Java.use('com.xxx');
  // hook_class.encode.implementation = function (a1) {
  //   Log.i("frida-HOOK",a1);
  //   var res = hook_class.encode(a1);
  //   return res;
  // }
})
