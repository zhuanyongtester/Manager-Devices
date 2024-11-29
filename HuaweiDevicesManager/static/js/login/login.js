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

function deleteCookie(name) {
    // 删除 cookie，设置过期时间为过去的时间
    document.cookie = name + '=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function logout(event) {
    event.preventDefault(); // 阻止表单默认提交

    const loginButton = event.target; // 获取点击的按钮

    // 禁用按钮以防止重复提交
    loginButton.innerText = "Logging out..."; // 更新按钮文本
    loginButton.disabled = true; // 禁用按钮

    // 删除指定的 Cookie
    deleteCookie('access_token');
    deleteCookie('refresh_token');
    deleteCookie('work_name');

    // 发送登出请求
    fetch(document.getElementById("submitLogOutForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // 从 Cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.message || '网络响应有误'); // 抛出具体的错误信息
            });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message); // 提示操作结果
        if (data.success) {
            window.location.href = "/"; // 登出成功后重定向到首页或登录页
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("登出失败，请重试：" + error.message); // 显示具体的错误信息
    })
    .finally(() => {
        // 恢复按钮状态
        loginButton.innerText = "Logout"; // 恢复按钮文本
        loginButton.disabled = false; // 启用按钮
    });
}
