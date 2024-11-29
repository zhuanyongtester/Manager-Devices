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
let selectedDevices = [];

function addDevice(imei, model, color) {
    // 检查设备是否已被选择
    if (selectedDevices.find(device => device.imei === imei)) {
        alert("该设备已被添加到已选设备列表！");
        return;
    }

    // 添加设备到已选设备列表
    selectedDevices.push({ imei, model, color });

    // 隐藏表1中对应的行
    document.getElementById(`deviceRow${imei}`).style.display = 'none';

    // 更新已选设备表
    updateSelectedDeviceTable();
}

function removeDevice(imei) {
    // 从已选设备列表中移除设备
    selectedDevices = selectedDevices.filter(device => device.imei !== imei);

    // 重新显示表1中的行
    document.getElementById(`deviceRow${imei}`).style.display = '';

    // 更新已选设备表
    updateSelectedDeviceTable();
}

function updateSelectedDeviceTable() {
    const tbody = document.getElementById('selectedDeviceTableBody');
    tbody.innerHTML = ''; // 清空表2内容

    selectedDevices.forEach((device, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${device.model}</td>
            <td>${device.color}</td>
            <td>${device.imei}</td>
            <td><button class="btn btn-sm btn-danger" onclick="removeDevice('${device.imei}')">-</button></td>
        `;
        tbody.appendChild(row);
    });
}



function searchDeviceByIMEI() {
    const searchValue = document.getElementById('imeiSearch').value.toLowerCase().trim(); // 获取搜索值并去除多余空格
    const rows = document.querySelectorAll('#deviceListBody tr');

    rows.forEach(row => {
        const imeiCell = row.cells[3].textContent.toLowerCase(); // 获取IMEI/SN单元格内容
        const nameCell = row.cells[1].textContent.toLowerCase(); // 获取设备名称单元格内容
        const imei = imeiCell.trim(); // 进行比较的IMEI

        // 确保在selectedDevices中找到了设备，使用每个设备的IMEI进行比较
        const isSelected = selectedDevices.some(device => device.imei.toLowerCase() === imei.toLowerCase());

        // 搜索IMEI/SN或设备名称包含搜索值，且设备不在已选设备列表中
        const matchesSearch = (imeiCell.includes(searchValue) || nameCell.includes(searchValue)) && !isSelected;

        // 根据匹配情况设置行的显示状态
        row.style.display = matchesSearch ? '' : 'none';
    });
}


function devices_borrow_cancel(event) {
    event.preventDefault(); // 阻止表单提交
    // 清空已选择的设备列表
    selectedDevices = [];

    // 重新显示所有设备
    document.querySelectorAll('#deviceListBody tr').forEach(row => {
        row.style.display = '';
    });

    // 更新表2
    updateSelectedDeviceTable();
}
function devices_borrow_all_submit(event){
    event.preventDefault(); // 阻止默认提交行为borrow_job_number
    const borrow_job_number = document.getElementById("borrow_job_number");
    const borrowName = document.getElementById("borrowName");
    const borrow_department = document.getElementById("borrow_department");
    const borrow_days = document.getElementById("borrow_days");
    const borrow_description = document.getElementById("borrow_description");
    // Convert the Set to an array and join to create a comma-separated string
    const imei_sn_list = selectedDevices.map(device => device.imei);
    console.log(imei_sn_list); // 输出为 ["imei1", "imei2", "imei3", ...]
        if (borrow_job_number.value.trim() === "") {
        alert("借机人工号是必填项！");
        borrowName.focus(); // 将焦点移到借机人名称输入框
        return false; // 阻止表单提交
    }
     if (borrowName.value.trim() === "") {
        alert("借机人名称是必填项！");
        borrowName.focus(); // 将焦点移到借机人名称输入框
        return false; // 阻止表单提交
    }

    // 检查部门是否为空
    if (borrow_department.value.trim() === "") {
        alert("部门是必填项！");
        borrow_department.focus(); // 将焦点移到部门输入框
        return false; // 阻止表单提交
    }

    // 检查借机天数是否为空
    if (borrow_days.value.trim() === "") {
        alert("借机天数不能为空！");
        borrow_days.focus(); // 将焦点移到借机天数输入框
        return false; // 阻止表单提交
    }

    // 检查借机天数是否为正整数
    var borrowDays = parseInt(borrow_days.value, 10);
    if (isNaN(borrowDays) || borrowDays <= 0) {
        alert("借机天数必须为正整数！");
        borrow_days.focus(); // 将焦点移到借机天数输入框
        return false; // 阻止表单提交
    }

    // 检查借机理由是否为空
    if (borrow_description.value.trim() === "") {
        alert("借机理由不能为空！");
        borrow_description.focus(); // 将焦点移到借机理由输入框
        return false; // 阻止表单提交
    }

    fetch(document.getElementById("viewDevicesInfoForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // 从 cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            imei_sn_list: imei_sn_list, // 发送IMEI/SN列表
            borrow_job_number: borrow_job_number.value,
            borrowName: borrowName.value,
            borrow_department: borrow_department.value,
            borrow_days: borrow_days.value,
            borrow_description: borrow_description.value,
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
        alert("借机失败，请重试。");
    });

}

function devices_borrow_all_cancel(event){
    event.preventDefault();
    // 跳转到新页面，例如添加新设备的页面
    window.location.href = "/auth/"; // 替换为你实际的目标URL
}

function fetchJobNumbers(query) {
    const suggestions = document.getElementById('suggestions');

    if (!suggestions) {
        console.error('Element with id "suggestions" not found.');
        return;
    }

    if (query.length === 0) {
        suggestions.innerHTML = '';
        return;
    }

    fetch('/auth/search_job_name/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ job_number: query })
    })
    .then(response => response.json())
    .then(data => {
        suggestions.innerHTML = '';  // 清空建议

        if (data.job_numbers.length === 0) {
            // 如果没有结果，显示提示
            let noResultItem = document.createElement('div');
            noResultItem.classList.add('list-group-item');
            noResultItem.textContent = '无匹配结果';
            suggestions.appendChild(noResultItem);
            return;
        }

        data.job_numbers.forEach(borrower => {
            let suggestionItem = document.createElement('a');
            suggestionItem.classList.add('list-group-item', 'list-group-item-action');
            suggestionItem.href = "#";
            suggestionItem.innerHTML = `${borrower.job_number} - ${borrower.name} - ${borrower.department}`;
            suggestionItem.onclick = (e) => {
                e.preventDefault();
                selectJobNumber(borrower.job_number, borrower.name, borrower.department);
            };
            suggestions.appendChild(suggestionItem);
        });
    })
    .catch(error => console.error('Error:', error));
}

function selectJobNumber(jobNumber, name, department) {
    document.getElementById('borrow_job_number').value = jobNumber;
    document.getElementById('borrowName').value = name;
    document.getElementById('borrow_department').value = department;
    document.getElementById('suggestions').innerHTML = '';  // 清空建议框
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


