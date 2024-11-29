function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function devices_view_submit(event){
       event.preventDefault(); // 阻止默认提交行为
       const signName= document.getElementById("sign_name");
       const imeiElement = document.getElementById('deviceImei');
       const viewImeiSn = imeiElement.innerText.replace('IMEI/SN: ', '').trim(); // 或者使用 imeiElement.getAttribute('data-imei-sn')

         if (signName.value.trim() === "") {
            alert("确认名称不能为空");
            imeiField.focus();  // 将焦点移到 IMEI 输入框
            return false;  // 阻止表单提交并保持在当前页面
        }
       fetch(document.getElementById("viewDevicesInfoForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // 从 cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            imei_sn_list: viewImeiSn, // 发送IMEI/SN列表
            sign_name:signName.value
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message); // 提示操作结果
        if (data.success) {
            window.location.href = "/auth/"; // 替换为你实际的目标URL
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("内部错误还机失败，请重试。");
    });
 }




function devices_view_cancel(event){
    event.preventDefault();
    // 跳转到新页面，例如添加新设备的页面
    window.location.href = "/auth/"; // 替换为你实际的目标URL

}