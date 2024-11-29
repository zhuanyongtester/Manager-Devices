  const modalBody  = document.getElementById('modalBody');
  //入库跳转

  function add_new_devices() {
        // 跳转到新页面，例如添加新设备的页面
        window.location.href = "/auth/sub_form/";  // 替换为你实际的目标URL

    }

    //出库
  function out_old_devices(){
     const checkboxes = document.querySelectorAll('input[name="device_ids"]:checked');
    const selectedIds = Array.from(checkboxes).map(checkbox => checkbox.value);

    if (selectedIds.length === 0) {
        alert("请至少选择一个设备。");
        return;
    }

    // 将选中的 IMEI/SN 作为查询参数发送到后端
    const queryString = selectedIds.join(',');
    fetch(`/auth/out?id=${queryString}`, {
        method: 'GET'  // 或者使用 POST 方法
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 跳转到展示页面
        window.location.href = data.redirect_url;
    })
    .catch(error => {
        console.error('请求出错:', error);
    });
  }

function borrow_devices(){
    const checkboxes = document.querySelectorAll('input[name="device_ids"]:checked');
    const selectedIds = Array.from(checkboxes).map(checkbox => checkbox.value);

    if (selectedIds.length === 0) {
        alert("请至少选择一个设备。");
        return;
    }

    // 将选中的 IMEI/SN 作为查询参数发送到后端
    const queryString = selectedIds.join(',');
    fetch(`/auth/borrow?id=${queryString}`,
    {
        method: 'GET'  // 或者使用 POST 方法
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 跳转到展示页面
        window.location.href = data.redirect_url;
    })
    .catch(error => {
        console.error('请求出错:', error);
    });

}

function back_devices(){
    const checkboxes = document.querySelectorAll('input[name="device_ids"]:checked');
    const selectedIds = Array.from(checkboxes).map(checkbox => checkbox.value);

    if (selectedIds.length === 0) {
        alert("请至少选择一个设备。");
        return;
    }else if(selectedIds.length >1){
          alert("只能选择一个设备归还。");
        return;
    }

    // 将选中的 IMEI/SN 作为查询参数发送到后端
    const queryString = selectedIds.join(',');
    fetch(`/auth/back?id=${queryString}`,
    {
        method: 'GET'  // 或者使用 POST 方法
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 跳转到展示页面
        window.location.href = data.redirect_url;
    })
    .catch(error => {
        console.error('请求出错:', error);
    });
}

function checkDeviceInfoModal(imeiSn) {
    // 使用 fetch 请求后端
    fetch(`/auth/back?id=${imeiSn}`, {
        method: 'GET'  // 或者使用 POST 方法
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // 跳转到展示页面
        window.location.href = data.redirect_url;
    })
    .catch(error => {
        console.error('请求出错:', error);
        alert('请求出错，请稍后再试。'); // 提示用户出错
    });
}

  function ckAll(){
  var flag = document.getElementById("allChecks").checked;
  var cks = document.getElementsByName("device_ids");
  for(var i=0;i<cks.length;i++){
      cks[i].checked=flag;
  }
}

function showDeviceInfoModal(imei_sn) {
    // 使用 AJAX 请求获取设备信息
    $.ajax({
        url: '/auth/get_device_info/', // 你的后台 API 地址
        type: 'GET',
        data: { 'imei_sn': imei_sn },
        success: function(data) {
            // 假设返回的数据是一个对象，包含设备的详细信息
            $('#modal_imei_sn').text(data.imei_sn);
            $('#modal_device_name').text(data.device_name);
            $('#modal_device_color').text(data.device_color);
            $('#modal_person').text(data.person);
            $('#modal_is_overdue').text(data.is_overdue ? '是' : '否');
            $('#modal_overdue_days').text(data.overdue_days || 0);

            // 显示模态框
            $('#deviceInfoModal').modal('show');
        },
        error: function(xhr, status, error) {
            console.error("获取设备信息失败:", error);
        }
    });

}
function borrow_all_devices(){
   window.location.href = "/auth/borrow_all/"
}



// 显示模态框
function showUserInfoModal() {
    $('#user_info').modal('show');
}

// 搜索用户信息
function searchUserByName() {
    const searchValue = document.getElementById('borrowerSearch').value.trim();

    if (searchValue.length === 0) {
        document.getElementById('userListTableBodyModal').innerHTML = '';
        return;
    }

    // AJAX 请求到你的 API
    fetch(`/auth/search_user?job_number_or_name=${encodeURIComponent(searchValue)}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('userListTableBodyModal');
            tbody.innerHTML = '';  // 清空表格内容

            data.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><input type="radio" name="selectedUser" value="${user.name}" data-user='${JSON.stringify(user)}'></td>
                    <td>${user.job_number}</td>
                    <td>${user.name}</td>
                    <td>${user.department}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("搜索用户失败：", error);
        });
}

// 确认选择用户并跳转
function confirmUserSelection() {
    const selectedUserRadio = document.querySelector('input[name="selectedUser"]:checked');

    if (!selectedUserRadio) {
        alert("请先选择一个借用人！");
        return;
    }

    const selectedUserData = JSON.parse(selectedUserRadio.getAttribute('data-user'));

    // 构建查询参数，只包含 job_number
    const queryParams = new URLSearchParams({
        job_number: selectedUserData.job_number
    });

    // 跳转到 /auth/back_all/ 并传递 job_number 参数
    window.location.href = `/auth/back_all/?${queryParams.toString()}`;
}



$(document).ready(function(){
    $('#excelDevicesAddForm').on('submit', function(e) {
        e.preventDefault();

        var fileInput = $('#excel_devices_file');
        var filePath = fileInput.val();

        // 验证文件格式
        if (!filePath) {
            alert("请选择文件！");
            return false;
        }
        var allowedExtensions = /(\.xls|\.xlsx)$/i;
        if (!allowedExtensions.exec(filePath)) {
            alert("请上传Excel文件格式（.xls或.xlsx）！");
            fileInput.val('');
            return false;
        }

        // 使用 FormData 处理文件上传
        var formData = new FormData(this);

        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === "success") {
                    alert(response.message);
                    window.location.href = "/auth/";  // 成功后重定向
                } else {
                    alert(response.message);  // 错误时弹出消息
                }
            },
            error: function(xhr) {
                alert("上传失败，请重试！");
            }
        });
    });
});


$(document).ready(function() {
    $('#example1').DataTable({
        "pageLength": 10,
        "lengthChange": false,
        "language": {
            "lengthMenu": "每页 _MENU_ 条记录",
            "zeroRecords": "没有找到记录",
            "info": "第 _PAGE_ 页 (共 _PAGES_ 页)",
            "infoEmpty": "没有记录",
            "infoFiltered": "(从 _MAX_ 条记录过滤)",
            "search": "搜索:",
            "paginate": {
                "first": "首页",
                "last": "末页",
                "next": "下一页",
                "previous": "上一页"
            }
        }
    });
});