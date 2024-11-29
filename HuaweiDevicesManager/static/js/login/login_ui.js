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
function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString(); // 计算过期时间
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/auth/'; // 设置 cookie
}

function login_submit(event) {
    event.preventDefault(); // 阻止默认提交行为
    const work_name = document.getElementById("work_name").value.trim();
    const work_password = document.getElementById("work_password").value.trim();

    // 检查账号是否为空
    if (work_name === "") {
        alert("请输入账号！");
        document.getElementById("work_name").focus();  // 将焦点移到账号输入框
        return false;  // 阻止表单提交并保持在当前页面
    }

    // 检查密码是否为空
    if (work_password === "") {
        alert("请输入密码");
        document.getElementById("work_password").focus();  // 将焦点移到密码输入框
        return false;
    }

    // 加密账号和密码
    const combinedString = work_name + work_password;
    const hashed_combined = CryptoJS.SHA256(combinedString).toString();
    // 显示加载指示器
    const loginButton = document.getElementById("submitLoginInfoForm").querySelector("button[type='submit']");
    loginButton.innerText = "登录中...";
    loginButton.disabled = true; // 禁用按钮，防止重复提交

    // 发送数据到后端
    fetch(document.getElementById("submitLoginInfoForm").action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'), // 从 cookie 中获取 CSRF token
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            work_name: work_name,
            work_password: hashed_combined // 发送加密后的密码
        })
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
            // 登录成功，保存 token 到 cookie
            setCookie('access_token', data.access_token, 7); // 过期时间设为 7 天
            setCookie('refresh_token', data.refresh_token, 30); // 过期时间设为 30 天
            setCookie('work_name', work_name, 7); // 过期时间设为 7 天
            window.location.href = "/auth/";
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("登录失败，请重试：" + error.message); // 显示具体的错误信息
    })
    .finally(() => {
        // 恢复按钮状态
        loginButton.innerText = "登录";
        loginButton.disabled = false;
    });
}
