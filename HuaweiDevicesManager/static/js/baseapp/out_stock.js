function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Check if this cookie string begins with the name we want
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function devices_out_submit(event) {
    // 阻止表单的默认提交行为
    event.preventDefault();
    const confirmation = confirm("确定要出库吗？"); // 提示框
    if (!confirmation) {
        return; // 如果用户选择取消，直接返回
    }
    // 收集IMEI/SN数据
    var imeiList = []; // 存储当前表格中的IMEI/SN
    var tableRows = document.querySelectorAll("#outStockTable tbody tr");

    tableRows.forEach(function(row) {
        // 提取IMEI/SN列的值（假设IMEI/SN在第4列，即索引3）
        var imei_sn = row.cells[3].innerText; // 获取IMEI/SN
        imeiList.push(imei_sn); // 添加到列表
    });

    // 打印IMEI/SN列表以供调试
    console.log(imeiList);

    // 发送数据到后端
    fetch(document.getElementById("outDevicesInfoForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),  // 从 cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            description: document.getElementById("description").value,
            imei_sn_list: imeiList // 发送IMEI/SN列表
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
              window.location.href = "/auth/";  // 替换为你实际的目标URL
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("出库失败，请重试。");
    });
}


function removeRow(element) {
    // 找到点击取消按钮的对应行
    var row = element.closest('tr');
    row.parentNode.removeChild(row);
}


function devices_out_cancel(event) {
           event.preventDefault();
        // 跳转到新页面，例如添加新设备的页面
        window.location.href = "/auth/";  // 替换为你实际的目标URL
}
