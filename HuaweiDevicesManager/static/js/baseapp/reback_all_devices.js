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

// 用于跟踪已选择设备的 IMEI
let selectedDevices = new Set();

function addDevice(imei) {
    // Find the row of the device in the first table
    const deviceRow = document.getElementById(`deviceRow${imei}`);

    // Check if the row exists
    if (deviceRow) {
        // Get the device information from the row
        const deviceName = deviceRow.cells[1].innerText; // 设备名称
        const deviceColor = deviceRow.cells[2].innerText; // 设备颜色
        const borrowTime = deviceRow.cells[4].innerText; // 借机时间
        const borrowDays = deviceRow.cells[5].innerText; // 借机天数
        const backTime = deviceRow.cells[6].innerText; // 还机时间
        const isOverdue = deviceRow.cells[7].innerText; // 是否超期

        // Create a new row for the selected devices table
        const selectedDeviceRow = document.createElement('tr');

        selectedDeviceRow.innerHTML = `
            <td>${document.getElementById('selectedDeviceTableBody').children.length + 1}</td>
            <td>${deviceName}</td>
            <td>${deviceColor}</td>
            <td>${imei}</td>
            <td>${borrowTime}</td>
            <td>${borrowDays}</td>
            <td>${backTime}</td>
            <td>${isOverdue}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeDevice('${imei}')">-</button>
            </td>
        `;

        // Append the new row to the selected devices table
        document.getElementById('selectedDeviceTableBody').appendChild(selectedDeviceRow);

        // 添加设备的 IMEI 到 selectedDevices Set
        selectedDevices.add(imei);

        // Optionally, remove the row from the original table
        deviceRow.remove();
    }
}

function removeDevice(imei) {
    // Find the row in the selected devices table
    const selectedRows = document.querySelectorAll('#selectedDeviceTableBody tr');

    selectedRows.forEach(row => {
        const rowIMEI = row.cells[3].innerText; // IMEI/SN
        if (rowIMEI === imei) {
            // Get the device information from the selected row
            const deviceName = row.cells[1].innerText; // 设备名称
            const deviceColor = row.cells[2].innerText; // 设备颜色
            const borrowTime = row.cells[4].innerText; // 借机时间
            const borrowDays = row.cells[5].innerText; // 借机天数
            const backTime = row.cells[6].innerText; // 还机时间
            const isOverdue = row.cells[7].innerText; // 是否超期

            // Find the device list table and create a new row
            const deviceListTable = document.getElementById('deviceListTable').getElementsByTagName('tbody')[0];
            const newDeviceRow = document.createElement('tr');

            newDeviceRow.id = `deviceRow${imei}`;
            newDeviceRow.innerHTML = `
                <td>${deviceListTable.children.length + 1}</td>
                <td>${deviceName}</td>
                <td>${deviceColor}</td>
                <td>${imei}</td>
                <td>${borrowTime}</td>
                <td>${borrowDays}</td>
                <td>${backTime}</td>
                <td>${isOverdue}</td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="addDevice('${imei}')">+</button>
                </td>
            `;

            // Append the new row back to the device list table
            deviceListTable.appendChild(newDeviceRow);

            // 从 selectedDevices Set 中移除该设备的 IMEI
            selectedDevices.delete(imei);

            // Remove the row from the selected devices table
            row.remove();
        }
    });
}

function searchDeviceByIMEI() {
    const searchTerm = document.getElementById('imeiSearch').value.toLowerCase();
    const deviceRows = document.querySelectorAll('#deviceListTable tbody tr');

    deviceRows.forEach(row => {
        const imeiCell = row.cells[3].innerText.toLowerCase();

        // 显示所有设备行如果搜索框为空
        if (!searchTerm || imeiCell.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function updateSelectedDeviceIndex() {
    const selectedRows = document.querySelectorAll('#selectedDeviceTableBody tr');
    selectedRows.forEach((row, index) => {
        row.children[0].innerText = index + 1; // 更新序号
    });
}

function devices_view_submit(event) {
    event.preventDefault(); // 阻止默认提交行为
    const signName = document.getElementById("sign_name");

    // Convert the Set to an array and join to create a comma-separated string
    const imei_sn_list = Array.from(selectedDevices).join(", ");

    if (signName.value.trim() === "") {
        alert("确认名称不能为空");
        signName.focus();  // 将焦点移到确认名称输入框
        return false;  // 阻止表单提交并保持在当前页面
    }

    fetch(document.getElementById("viewDevicesInfoForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // 从 cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            imei_sn_list: imei_sn_list, // 发送IMEI/SN列表
            sign_name: signName.value
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
        alert("还机失败，请重试。");
    });
}

function devices_view_cancel(event) {
    event.preventDefault();
    // 跳转到新页面，例如添加新设备的页面
    window.location.href = "/auth/"; // 替换为你实际的目标URL
}

    $(document).ready(function () {
        $('#deviceListTable').DataTable({
            "pageLength": 10,  // Show 10 entries by default
            "lengthMenu": [5, 10, 25, 50, 100],  // Option for entries to show
             "searching": false,  // 禁用搜索功能
            "language": {
                "lengthMenu": "每页显示 _MENU_ 条记录",
                "zeroRecords": "没有找到记录",
                "info": "显示 _PAGE_ / _PAGES_ 页",
                "infoEmpty": "没有可用记录",
                "infoFiltered": "(从 _MAX_ 条记录中筛选)",
                "search": "搜索:",
                "paginate": {
                    "first": "第一页",
                    "last": "最后一页",
                    "next": "下一页",
                    "previous": "上一页"
                }
            }
        });
    });
