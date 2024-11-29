 $(document).ready(function() {
            $('#example1').DataTable({
                "pageLength": 10, // 每页显示 10 条记录
                "lengthChange": false, // 禁用页面长度变化
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