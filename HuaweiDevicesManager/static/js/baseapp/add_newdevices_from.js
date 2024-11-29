    function devices_submit(event) {
        // 阻止表单的默认提交行为
        event.preventDefault();

        var imeiField = document.getElementById("imei");
        var modelNameField = document.getElementById("model_name");
        var modelNumField = document.getElementById("model_number");
        var colorField = document.getElementById("color");
        var formSub = document.getElementById("submitDevicesInfoForm");

        // 检查 IMEI 是否为空
        if (imeiField.value.trim() === "") {
            alert("IMEI/SN 是必填项！");
            imeiField.focus();  // 将焦点移到 IMEI 输入框
            return false;  // 阻止表单提交并保持在当前页面
        }

        // 检查 Model Name 是否为空
        if (modelNameField.value.trim() === "") {
            alert("Model Name 是必填项！");
            modelNameField.focus();  // 将焦点移到 Model Name 输入框
            return false;
        }

        // 检查 Model Number 是否为空
        if (modelNumField.value.trim() === "") {
            alert("Model Number 是必填项！");
            modelNumField.focus();  // 将焦点移到 Model Number 输入框
            return false;
        }

        // 检查 Color 是否为空
        if (colorField.value.trim() === "") {
            alert("Color 是必填项！");
            colorField.focus();  // 将焦点移到 Color 输入框
            return false;
        }

        // 如果所有验证通过，提交表单
        // 验证是否成功获取到表单
         if (!formSub) {
            console.log("Form not found!");
            return;
           }
    // 提交表单
          formSub.submit();  // 提交表单
    }


  //入库跳转
  function devices_cancel(event) {
         event.preventDefault();
        // 跳转到新页面，例如添加新设备的页面
        window.location.href = "/auth/";  // 替换为你实际的目标URL

    }
