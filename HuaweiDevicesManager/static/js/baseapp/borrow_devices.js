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

function devices_borrow_submit(event) {
    event.preventDefault(); // 阻止默认提交行为
    var borrow_job_number = document.getElementById("borrow_job_number");
    var borrowName = document.getElementById("borrowName");
    var borrow_department = document.getElementById("borrow_department");
    var borrow_days = document.getElementById("borrow_days");

    var borrow_description = document.getElementById("borrow_description");
    // 检查借机人名称是否为空
    if (borrow_job_number.value.trim() === "") {
        alert("借机人名称是必填项！");
        borrowName.focus(); // 将焦点移到借机人名称输入框
        return false; // 阻止表单提交
    }

    // 检查借机人名称是否为空
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

    var imeiList = []; // 存储当前表格中的IMEI/SN
    var tableRows = document.querySelectorAll("#borrowStockTable tbody tr");

    tableRows.forEach(function(row) {
        // 提取IMEI/SN列的值（假设IMEI/SN在第4列，即索引3）
        var imei_sn = row.cells[3].innerText; // 获取IMEI/SN
        imeiList.push(imei_sn); // 添加到列表
    });

    // 打印IMEI/SN列表以供调试
    console.log(borrow_job_number.value);

    // 发送数据到后端
    fetch(document.getElementById("borrowDevicesInfoForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // 从 cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            borrow_description: borrow_description.value,
            borrow_job_number: borrow_job_number.value, // 发送工号
            borrowName: borrowName.value,
            borrow_department: borrow_department.value, // 发送部门信息
            borrow_days: borrow_days.value, // 发送借机天数
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
            window.location.href = "/auth/"; // 替换为你实际的目标URL
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("借机失败，请重试。");
    });
}

function removeRow(element) {
    // 找到点击取消按钮的对应行
    var row = element.closest('tr');
    row.parentNode.removeChild(row);
}

function devices_borrow_cancel(event) {
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
        // 初始化设备列表 DataTable
        $('#borrowStockTable').DataTable({
            "pageLength": 10,
            "lengthMenu": [5, 10, 25, 50, 100],
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
