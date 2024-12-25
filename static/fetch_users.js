// static/js/fetch_users.js
fetch('/admin/api/users')
  .then(response => response.json())
  .then(data => {
    layui.use('table', function(){
      var table = layui.table;
      table.render({
        elem: '#test',
        data: data.rows.item,
        toolbar: '#toolbarDemo',
        defaultToolbar: ['filter', 'exports', 'print', {
          title: '提示',
          layEvent: 'LAYTABLE_TIPS',
          icon: 'layui-icon-tips',
          onClick: function(obj) {
            layer.alert('自定义工具栏图标按钮');
          }
        }],
        height: 'full-35',
        cellMinWidth: 240,
        totalRow: true,
        page: true,
        cols: [[
          {type: 'checkbox', fixed: 'left'},
          {field: 'id', fixed: 'left', width: 80, title: 'ID', sort: true, totalRow: '合计：'},
          {field: 'username', title: '用户名'},
          // 其他字段
        ]]
      });
    });
  })
  .catch(error => console.error('Error fetching user data:', error));