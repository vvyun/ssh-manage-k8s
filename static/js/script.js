// 当前选中的集群
let currentCluster = null;

// 分页配置
const pagination = {
    deployments: { currentPage: 1, pageSize: 10, totalPages: 0, allData: [], filteredData: [] },
    services: { currentPage: 1, pageSize: 10, totalPages: 0, allData: [], filteredData: [] },
    pods: { currentPage: 1, pageSize: 10, totalPages: 0, allData: [], filteredData: [] }
};

// Toast通知功能
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // 图标
    const icons = {
        success: '✓',
        error: '✖',
        warning: '⚠',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type] || icons.info}</span>
        <span class="toast-content">${message}</span>
        <span class="toast-close">×</span>
    `;
    
    container.appendChild(toast);
    
    // 关闭按钮事件
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
        removeToast(toast);
    });
    
    // 自动关闭
    if (duration > 0) {
        setTimeout(() => {
            removeToast(toast);
        }, duration);
    }
}

function removeToast(toast) {
    toast.classList.add('hiding');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 加载集群列表
    loadClusters();
    
    // 绑定事件监听器
    bindEventListeners();
});

// 绑定事件监听器
function bindEventListeners() {
    // 添加集群按钮
    document.getElementById('add-cluster-btn').addEventListener('click', showAddClusterModal);
    
    // 关闭模态框
    document.querySelector('.close').addEventListener('click', closeAddClusterModal);
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('add-cluster-modal');
        if (event.target === modal) {
            closeAddClusterModal();
        }
    });
    
    // 提交集群表单
    document.getElementById('add-cluster-form').addEventListener('submit', addCluster);
    
    // Tab切换
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
    
    // 命名空间选择变化
    document.getElementById('namespace-select').addEventListener('change', function() {
        if (currentCluster) {
            loadCurrentTabData();
        }
    });
    
    // 筛选器输入事件
    document.getElementById('deployments-filter').addEventListener('input', function() {
        filterTable('deployments');
    });
    
    document.getElementById('services-filter').addEventListener('input', function() {
        filterTable('services');
    });
    
    document.getElementById('pods-filter').addEventListener('input', function() {
        filterTable('pods');
    });
    
    // 更新镜像模态框事件
    document.getElementById('cancel-update').addEventListener('click', closeUpdateImageModal);
    document.querySelector('#update-image-modal .close').addEventListener('click', closeUpdateImageModal);
    document.getElementById('update-image-form').addEventListener('submit', updateDeploymentImage);
    
    // 删除Pod模态框事件
    document.getElementById('cancel-delete').addEventListener('click', closeDeletePodModal);
    document.querySelector('#delete-pod-modal .close').addEventListener('click', closeDeletePodModal);
    document.getElementById('confirm-delete').addEventListener('click', confirmDeletePod);
    
    // 查看日志模态框事件
    document.getElementById('close-logs').addEventListener('click', closeViewLogsModal);
    document.querySelector('#view-logs-modal .close').addEventListener('click', closeViewLogsModal);
    document.getElementById('refresh-logs').addEventListener('click', refreshLogs);
    document.getElementById('download-logs').addEventListener('click', downloadLogs);
    document.getElementById('log-lines').addEventListener('change', refreshLogs);
    
    // 批量更新镜像模态框事件
    document.getElementById('batch-update-image-btn').addEventListener('click', showBatchUpdateImageModal);
    document.getElementById('close-batch-update').addEventListener('click', closeBatchUpdateImageModal);
    document.querySelector('#batch-update-image-modal .close').addEventListener('click', closeBatchUpdateImageModal);
    document.getElementById('search-deployments-btn').addEventListener('click', searchDeploymentsByImage);
    
    // 容器伸缩模态框事件
    document.getElementById('cancel-scale').addEventListener('click', closeScaleDeploymentModal);
    document.querySelector('#scale-deployment-modal .close').addEventListener('click', closeScaleDeploymentModal);
    document.getElementById('scale-deployment-form').addEventListener('submit', scaleDeployment);
    
    // 删除集群模态框事件
    document.getElementById('cancel-delete-cluster').addEventListener('click', closeDeleteClusterModal);
    document.querySelector('#delete-cluster-modal .close').addEventListener('click', closeDeleteClusterModal);
    document.getElementById('confirm-delete-cluster').addEventListener('click', confirmDeleteCluster);
}

// 加载集群列表
function loadClusters() {
    fetch('/api/clusters')
        .then(response => response.json())
        .then(clusters => {
            const clusterList = document.getElementById('cluster-list');
            clusterList.innerHTML = '';
            
            clusters.forEach(cluster => {
                const li = document.createElement('li');
                li.className = 'cluster-item';
                li.dataset.clusterId = cluster.name.toLowerCase().replace(' ', '-');
                
                // 创建集群名称显示元素
                const nameSpan = document.createElement('span');
                nameSpan.className = 'cluster-name';
                nameSpan.textContent = cluster.name;
                
                // 创建操作按钮
                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'cluster-actions';
                
                // 创建操作按钮
                const actionsBtn = document.createElement('button');
                actionsBtn.className = 'actions-btn';
                actionsBtn.innerHTML = '⋯';
                actionsBtn.title = '操作';
                
                // 创建下拉菜单
                const dropdown = document.createElement('div');
                dropdown.className = 'dropdown-menu';
                dropdown.style.display = 'none';
                
                // 重命名选项
                const renameOption = document.createElement('div');
                renameOption.className = 'dropdown-option';
                renameOption.textContent = '重命名';
                renameOption.onclick = function(e) {
                    e.stopPropagation();
                    hideAllDropdowns();
                    editClusterName(cluster.name, li);
                };
                
                // 删除选项
                const deleteOption = document.createElement('div');
                deleteOption.className = 'dropdown-option';
                deleteOption.textContent = '删除';
                deleteOption.onclick = function(e) {
                    e.stopPropagation();
                    hideAllDropdowns();
                    showDeleteClusterModal(cluster.name);
                };
                
                dropdown.appendChild(renameOption);
                dropdown.appendChild(deleteOption);
                
                // 切换下拉菜单显示
                actionsBtn.onclick = function(e) {
                    e.stopPropagation();
                    // 隐藏其他下拉菜单
                    hideAllDropdowns();
                    // 切换当前菜单
                    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
                };
                
                actionsDiv.appendChild(actionsBtn);
                actionsDiv.appendChild(dropdown);
                
                li.appendChild(nameSpan);
                li.appendChild(actionsDiv);
                
                li.addEventListener('click', function() {
                    selectCluster(li.dataset.clusterId);
                });
                clusterList.appendChild(li);
            });
            
            // 默认选中第一个集群
            if (clusters.length > 0) {
                selectCluster(clusters[0].name.toLowerCase().replace(' ', '-'));
            }
        })
        .catch(error => {
            console.error('加载集群列表失败:', error);
            showToast('加载集群列表失败', 'error');
        });
}

// 选择集群
function selectCluster(clusterId) {
    // 更新UI选中状态
    document.querySelectorAll('.cluster-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`.cluster-item[data-cluster-id="${clusterId}"]`).classList.add('active');
    
    currentCluster = clusterId;
    
    // 加载命名空间
    loadNamespaces(clusterId);
}

// 加载命名空间
function loadNamespaces(clusterId) {
    fetch(`/api/clusters/${clusterId}/namespaces`)
        .then(response => response.json())
        .then(namespaces => {
            const namespaceSelect = document.getElementById('namespace-select');
            namespaceSelect.innerHTML = '';
            select_name = ''
            namespaces.forEach(ns => {
                const option = document.createElement('option');
                option.value = ns.NAME;
                option.textContent = ns.NAME;
                namespaceSelect.appendChild(option);
                if (ns.SELECT) {
                    select_name = ns.NAME
                }
            });
            namespaceSelect.value = select_name;
            
            // 加载当前tab数据
            loadCurrentTabData();
        })
        .catch(error => {
            console.error('加载命名空间失败:', error);
            showToast('加载命名空间失败', 'error');
        });
}

// 显示添加集群模态框
function showAddClusterModal() {
    // 清空表单
    document.getElementById('add-cluster-form').reset();
    document.getElementById('add-cluster-modal').style.display = 'block';
}

// 关闭添加集群模态框
function closeAddClusterModal() {
    document.getElementById('add-cluster-modal').style.display = 'none';
    // 清空表单
    document.getElementById('add-cluster-form').reset();
}

// 添加集群
function addCluster(event) {
    event.preventDefault();
    const addclusterform = document.getElementById('add-cluster-form')
    const formData = new FormData(addclusterform);
    const clusterData = {
        name: formData.get('cluster-name'),
        namespace: formData.get('cluster-namespace'),
        ssh_config: {
            hostname: formData.get('ssh-hostname'),
            username: formData.get('ssh-username'),
            password: formData.get('ssh-password') || '',
            port: parseInt(formData.get('ssh-port')) || 22,
            key_path: formData.get('ssh-key-path') || ''
        }
    };
    
    fetch('/api/clusters', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(clusterData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeAddClusterModal();
            loadClusters(); // 重新加载集群列表
            showToast('集群添加成功', 'success');
        } else {
            showToast('集群添加失败: ' + (result.error || ''), 'error');
        }
    })
    .catch(error => {
        console.error('添加集群失败:', error);
        showToast('添加集群失败', 'error');
    });
}

// 切换Tab
function switchTab(tabName) {
    // 更新Tab按钮状态
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelector(`.tab-btn[data-tab="${tabName}"]`).classList.add('active');
    
    // 更新内容显示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-content`).classList.add('active');
    
    // 加载数据
    loadTabData(tabName);
}

// 获取当前激活的Tab
function getCurrentTab() {
    const activeTab = document.querySelector('.tab-btn.active');
    return activeTab ? activeTab.dataset.tab : 'deployments';
}

// 加载当前Tab数据
function loadCurrentTabData() {
    const currentTab = getCurrentTab();
    loadTabData(currentTab);
}

// 加载指定Tab的数据
function loadTabData(tabName) {
    if (!currentCluster) return;
    
    const namespace = document.getElementById('namespace-select').value;
    
    let apiUrl = '';
    let tableId = '';
    
    switch (tabName) {
        case 'deployments':
            apiUrl = `/api/clusters/${currentCluster}/deployments?namespace=${namespace}`;
            tableId = 'deployments-table';
            break;
        case 'services':
            apiUrl = `/api/clusters/${currentCluster}/services?namespace=${namespace}`;
            tableId = 'services-table';
            break;
        case 'pods':
            apiUrl = `/api/clusters/${currentCluster}/pods?namespace=${namespace}`;
            tableId = 'pods-table';
            break;
        default:
            return;
    }
    
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            populateTable(tableId, data, tabName);
        })
        .catch(error => {
            // console.error(`加载${tabName}数据失败:`, error);
            showToast(`命名空间【${namespace}】没有 ${tabName} 数据`, 'info');
        });
}

// 填充表格数据
function populateTable(tableId, data, tabType) {
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    
    if (!data || data.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = table.querySelectorAll('thead th').length;
        cell.textContent = '暂无数据';
        cell.style.textAlign = 'center';
        
        // 清空分页
        pagination[tabType].allData = [];
        pagination[tabType].filteredData = [];
        pagination[tabType].totalPages = 0;
        pagination[tabType].currentPage = 1;
        renderPagination(tabType);
        return;
    }
    
    // 保存所有数据
    pagination[tabType].allData = data;
    pagination[tabType].filteredData = data; // 初始时筛选数据就是全部数据
    pagination[tabType].currentPage = 1; // 重置到第一页
    pagination[tabType].totalPages = Math.ceil(data.length / pagination[tabType].pageSize);
    
    // 渲染当前页数据
    renderCurrentPage(tabType);
    
    // 渲染分页按钮
    renderPagination(tabType);
}

// 筛选表格数据
function filterTable(tabType) {
    let filterInputId = '';
    
    switch (tabType) {
        case 'deployments':
            filterInputId = 'deployments-filter';
            break;
        case 'services':
            filterInputId = 'services-filter';
            break;
        case 'pods':
            filterInputId = 'pods-filter';
            break;
        default:
            return;
    }
    
    const filterValue = document.getElementById(filterInputId).value.toLowerCase();
    const pageData = pagination[tabType];
    
    if (!filterValue) {
        // 无筛选，显示所有数据
        pageData.filteredData = pageData.allData;
    } else {
        // 有筛选，从所有数据中筛选
        pageData.filteredData = pageData.allData.filter(item => {
            const name = (item.NAME || '').toLowerCase();
            return name.includes(filterValue);
        });
    }
    
    // 重新计算总页数
    pageData.totalPages = Math.ceil(pageData.filteredData.length / pageData.pageSize);
    
    // 如果当前页超过总页数，重置到第一页
    if (pageData.currentPage > pageData.totalPages && pageData.totalPages > 0) {
        pageData.currentPage = 1;
    } else if (pageData.totalPages === 0) {
        pageData.currentPage = 1;
    }
    
    // 重新渲染当前页
    renderCurrentPage(tabType);
    
    // 重新渲染分页
    renderPagination(tabType);
}

// 显示更新镜像模态框
function showUpdateImageModal(deploymentName) {
    document.getElementById('deployment-name').value = deploymentName;
    document.getElementById('image-name').value = '';
    document.getElementById('update-image-modal').style.display = 'block';
}

// 关闭更新镜像模态框
function closeUpdateImageModal() {
    document.getElementById('update-image-modal').style.display = 'none';
}

// 更新部署镜像
function updateDeploymentImage(event) {
    event.preventDefault();
    
    const deploymentName = document.getElementById('deployment-name').value;
    const imageName = document.getElementById('image-name').value;
    
    if (!currentCluster) {
        showToast('未选择集群', 'warning');
        return;
    }
    
    if (!imageName) {
        showToast('请输入镜像名称', 'warning');
        return;
    }
    
    const namespace = document.getElementById('namespace-select').value;
    
    fetch(`/api/clusters/${currentCluster}/deployments/${deploymentName}/update-image?namespace=${namespace}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageName })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeUpdateImageModal();
            showToast('镜像更新成功', 'success');
            // 重新加载工作负载数据
            loadTabData('deployments');
        } else {
            showToast('镜像更新失败: ' + result.error, 'error');
        }
    })
    .catch(error => {
        console.error('更新镜像失败:', error);
        showToast('更新镜像失败', 'error');
    });
}

// 渲染当前页数据
function renderCurrentPage(tabType) {
    const tableId = `${tabType}-table`;
    const table = document.getElementById(tableId);
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    
    const pageData = pagination[tabType];
    
    // 使用筛选后的数据而不是全部数据
    const dataToDisplay = pageData.filteredData || pageData.allData;
    
    if (!dataToDisplay || dataToDisplay.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = table.querySelectorAll('thead th').length;
        cell.textContent = '暂无数据';
        cell.style.textAlign = 'center';
        return;
    }
    
    const startIndex = (pageData.currentPage - 1) * pageData.pageSize;
    const endIndex = Math.min(startIndex + pageData.pageSize, dataToDisplay.length);
    const currentPageData = dataToDisplay.slice(startIndex, endIndex);
    
    currentPageData.forEach(item => {
        const row = tbody.insertRow();
        
        // 为每行添加数据属性，便于后续筛选
        row.dataset.name = item.NAME || '';
        
        switch (tabType) {
            case 'deployments':
                row.insertCell().textContent = item.NAME || '';
                row.insertCell().textContent = item.READY || '';
                row.insertCell().textContent = item.UP_TO_DATE || '';
                row.insertCell().textContent = item.AVAILABLE || '';
                row.insertCell().textContent = item.AGE || '';
                
                // 添加操作按钮
                const actionCell = row.insertCell();
                
                // 更新镜像按钮
                const updateBtn = document.createElement('button');
                updateBtn.textContent = '更新镜像';
                updateBtn.className = 'update-btn';
                updateBtn.onclick = function() {
                    showUpdateImageModal(item.NAME || '');
                };
                actionCell.appendChild(updateBtn);
                
                // 容器伸缩按钮
                const scaleBtn = document.createElement('button');
                scaleBtn.textContent = '容器伸缩';
                scaleBtn.className = 'scale-btn';
                scaleBtn.onclick = function() {
                    showScaleDeploymentModal(item.NAME || '', item.READY || '');
                };
                actionCell.appendChild(scaleBtn);
                break;
            case 'services':
                row.insertCell().textContent = item.NAME || '';
                row.insertCell().textContent = item.TYPE || '';
                row.insertCell().textContent = item.CLUSTER_IP || '';
                row.insertCell().textContent = item.PORTS || '';
                row.insertCell().textContent = item.AGE || '';
                break;
            case 'pods':
                row.insertCell().textContent = item.NAME || '';
                row.insertCell().textContent = item.READY || '';
                row.insertCell().textContent = item.STATUS || '';
                row.insertCell().textContent = item.RESTARTS || '';
                row.insertCell().textContent = item.AGE || '';
                
                // 添加操作按钮
                const podActionCell = row.insertCell();
                
                // 日志按钮
                const logBtn = document.createElement('button');
                logBtn.textContent = '日志';
                logBtn.className = 'log-btn';
                logBtn.onclick = function() {
                    showViewLogsModal(item.NAME || '');
                };
                podActionCell.appendChild(logBtn);
                
                // 删除按钮
                const deleteBtn = document.createElement('button');
                deleteBtn.textContent = '删除';
                deleteBtn.className = 'delete-btn';
                deleteBtn.onclick = function() {
                    showDeletePodModal(item.NAME || '');
                };
                podActionCell.appendChild(deleteBtn);
                break;
        }
    });
}

// 渲染分页按钮
function renderPagination(tabType) {
    const paginationId = `${tabType}-pagination`;
    const paginationDiv = document.getElementById(paginationId);
    paginationDiv.innerHTML = '';
    
    const pageData = pagination[tabType];
    
    if (pageData.totalPages <= 1) {
        // 不需要分页，但显示总数
        if (pageData.filteredData && pageData.filteredData.length > 0) {
            const pageInfo = document.createElement('span');
            pageInfo.className = 'page-info';
            pageInfo.textContent = `共 ${pageData.filteredData.length} 条`;
            paginationDiv.appendChild(pageInfo);
        }
        return;
    }
    
    // 上一页按钮
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = pageData.currentPage === 1;
    prevBtn.onclick = () => changePage(tabType, pageData.currentPage - 1);
    paginationDiv.appendChild(prevBtn);
    
    // 页码按钮
    const maxVisiblePages = 5;
    let startPage = Math.max(1, pageData.currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(pageData.totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    if (startPage > 1) {
        const firstBtn = document.createElement('button');
        firstBtn.textContent = '1';
        firstBtn.onclick = () => changePage(tabType, 1);
        paginationDiv.appendChild(firstBtn);
        
        if (startPage > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'page-info';
            paginationDiv.appendChild(ellipsis);
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        if (i === pageData.currentPage) {
            pageBtn.className = 'active';
        }
        pageBtn.onclick = () => changePage(tabType, i);
        paginationDiv.appendChild(pageBtn);
    }
    
    if (endPage < pageData.totalPages) {
        if (endPage < pageData.totalPages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'page-info';
            paginationDiv.appendChild(ellipsis);
        }
        
        const lastBtn = document.createElement('button');
        lastBtn.textContent = pageData.totalPages;
        lastBtn.onclick = () => changePage(tabType, pageData.totalPages);
        paginationDiv.appendChild(lastBtn);
    }
    
    // 下一页按钮
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = pageData.currentPage === pageData.totalPages;
    nextBtn.onclick = () => changePage(tabType, pageData.currentPage + 1);
    paginationDiv.appendChild(nextBtn);
    
    // 页面信息（显示筛选后的数据量）
    const pageInfo = document.createElement('span');
    pageInfo.className = 'page-info';
    const totalData = pageData.filteredData ? pageData.filteredData.length : pageData.allData.length;
    pageInfo.textContent = `第 ${pageData.currentPage} / ${pageData.totalPages} 页，共 ${totalData} 条`;
    paginationDiv.appendChild(pageInfo);
}

// 切换页码
function changePage(tabType, newPage) {
    const pageData = pagination[tabType];
    
    if (newPage < 1 || newPage > pageData.totalPages) {
        return;
    }
    
    pageData.currentPage = newPage;
    renderCurrentPage(tabType);
    renderPagination(tabType);
}

// 删除Pod相关功能
let podToDelete = null;

// 显示删除Pod模态框
function showDeletePodModal(podName) {
    podToDelete = podName;
    document.getElementById('delete-pod-name').textContent = podName;
    document.getElementById('delete-pod-modal').style.display = 'block';
}

// 关闭删除Pod模态框
function closeDeletePodModal() {
    podToDelete = null;
    document.getElementById('delete-pod-modal').style.display = 'none';
}

// 确认删除Pod
function confirmDeletePod() {
    if (!podToDelete || !currentCluster) {
        showToast('无效的操作', 'error');
        return;
    }
    
    const namespace = document.getElementById('namespace-select').value;
    
    fetch(`/api/clusters/${currentCluster}/pods/${podToDelete}?namespace=${namespace}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeDeletePodModal();
            showToast(`Pod ${podToDelete} 已成功删除`, 'success');
            // 重新加载Pods数据
            loadTabData('pods');
        } else {
            showToast('删除Pod失败: ' + result.error, 'error');
        }
    })
    .catch(error => {
        console.error('删除Pod失败:', error);
        showToast('删除Pod失败', 'error');
    });
}

// 查看日志相关功能
let currentLogPod = null;

// 显示查看日志模态框
function showViewLogsModal(podName) {
    currentLogPod = podName;
    document.getElementById('log-pod-name').textContent = podName;
    document.getElementById('view-logs-modal').style.display = 'block';
    // 加载日志
    loadPodLogs();
}

// 关闭查看日志模态框
function closeViewLogsModal() {
    currentLogPod = null;
    document.getElementById('view-logs-modal').style.display = 'none';
}

// 加载Pod日志
function loadPodLogs() {
    if (!currentLogPod || !currentCluster) {
        showToast('无效的操作', 'error');
        return;
    }
    
    const namespace = document.getElementById('namespace-select').value;
    const lines = document.getElementById('log-lines').value;
    const logOutput = document.getElementById('log-output');
    
    logOutput.textContent = '加载中...';
    
    let url = `/api/clusters/${currentCluster}/pods/${currentLogPod}/logs?namespace=${namespace}`;
    if (lines) {
        url += `&lines=${lines}`;
    }
    
    fetch(url)
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            logOutput.textContent = result.logs || '无日志输出';
        } else {
            logOutput.textContent = '加载日志失败: ' + result.error;
            showToast('加载日志失败', 'error');
        }
    })
    .catch(error => {
        console.error('加载日志失败:', error);
        logOutput.textContent = '加载日志失败: ' + error.message;
        showToast('加载日志失败', 'error');
    });
}

// 刷新日志
function refreshLogs() {
    loadPodLogs();
}

// 下载日志
function downloadLogs() {
    const logContent = document.getElementById('log-output').textContent;
    
    if (!logContent || logContent === '加载中...' || logContent === '无日志输出') {
        showToast('无可下载的日志', 'warning');
        return;
    }
    
    // 创建Blob对象
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    // 创建下载链接
    const a = document.createElement('a');
    a.href = url;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    a.download = `${currentLogPod}_${timestamp}.log`;
    document.body.appendChild(a);
    a.click();
    
    // 清理
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('日志下载成功', 'success');
}

// 批量更新镜像相关功能
// 显示批量更新镜像模态框
function showBatchUpdateImageModal() {
    document.getElementById('batch-update-image-modal').style.display = 'block';
    document.getElementById('search-image-name').value = '';
    document.getElementById('deployments-result').innerHTML = '<p class="hint-text">请输入镜像名称并点击查询</p>';
}

// 关闭批量更新镜像模态框
function closeBatchUpdateImageModal() {
    document.getElementById('batch-update-image-modal').style.display = 'none';
}

// 根据镜像名称查询工作负载
function searchDeploymentsByImage() {
    const imageName = document.getElementById('search-image-name').value.trim();
    
    if (!imageName) {
        showToast('请输入镜像名称', 'warning');
        return;
    }
    
    if (!currentCluster) {
        showToast('未选择集群', 'error');
        return;
    }
    
    const namespace = document.getElementById('namespace-select').value;
    const resultDiv = document.getElementById('deployments-result');
    
    resultDiv.innerHTML = '<p class="hint-text">加载中...</p>';
    
    fetch(`/api/clusters/${currentCluster}/search-deployments-by-image?namespace=${namespace}&image=${encodeURIComponent(imageName)}`)
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            displayDeploymentResults(result.deployments, imageName);
        } else {
            resultDiv.innerHTML = `<p class="hint-text">查询失败: ${result.error}</p>`;
            showToast('查询失败', 'error');
        }
    })
    .catch(error => {
        console.error('查询失败:', error);
        resultDiv.innerHTML = '<p class="hint-text">查询失败</p>';
        showToast('查询失败', 'error');
    });
}

// 显示查询结果
function displayDeploymentResults(deployments, imageName) {
    const resultDiv = document.getElementById('deployments-result');
    
    if (!deployments || deployments.length === 0) {
        resultDiv.innerHTML = '<p class="hint-text">未找到匹配的工作负载</p>';
        return;
    }
    
    let html = '';
    deployments.forEach(dep => {
        html += `
            <div class="deployment-item">
                <div class="deployment-info">
                    <h4>${dep.name}</h4>
                    <p>命名空间: ${dep.namespace} | 当前镜像: ${dep.image}</p>
                </div>
                <div class="deployment-actions">
                    <button class="update-btn" onclick="updateDeploymentImageFromBatch('${dep.name}', '${imageName}')">更新</button>
                </div>
            </div>
        `;
    });
    
    resultDiv.innerHTML = html;
}

// 从批量更新中更新单个部署的镜像
function updateDeploymentImageFromBatch(deploymentName, imageName) {
    if (!currentCluster) {
        showToast('未选择集群', 'error');
        return;
    }

    const namespace = document.getElementById('namespace-select').value;

    fetch(`/api/clusters/${currentCluster}/deployments/${deploymentName}/update-image?namespace=${namespace}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: imageName })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeUpdateImageModal();
            showToast('镜像更新成功', 'success');
            // 重新加载工作负载数据
            loadTabData('deployments');
        } else {
            showToast('镜像更新失败: ' + result.error, 'error');
        }
    })
    .catch(error => {
        console.error('更新镜像失败:', error);
        showToast('更新镜像失败', 'error');
    });
}

// 容器伸缩相关功能
// 显示容器伸缩模态框
function showScaleDeploymentModal(deploymentName, readyStatus) {
    document.getElementById('scale-deployment-name').value = deploymentName;
    
    // 从 READY 状态中解析当前副本数 (例如 "2/3" 表示当前 2 个，期望 3 个)
    let currentReplicas = 0;
    if (readyStatus && readyStatus.includes('/')) {
        currentReplicas = parseInt(readyStatus.split('/')[1]) || 0;
    }
    
    document.getElementById('current-replicas').value = currentReplicas;
    document.getElementById('target-replicas').value = currentReplicas;
    document.getElementById('scale-deployment-modal').style.display = 'block';
}

// 关闭容器伸缩模态框
function closeScaleDeploymentModal() {
    document.getElementById('scale-deployment-modal').style.display = 'none';
}

// 执行容器伸缩
function scaleDeployment(event) {
    event.preventDefault();
    
    const deploymentName = document.getElementById('scale-deployment-name').value;
    const targetReplicas = parseInt(document.getElementById('target-replicas').value);
    
    if (!currentCluster) {
        showToast('未选择集群', 'warning');
        return;
    }
    
    if (isNaN(targetReplicas) || targetReplicas < 0) {
        showToast('请输入有效的副本数', 'warning');
        return;
    }
    
    const namespace = document.getElementById('namespace-select').value;
    
    fetch(`/api/clusters/${currentCluster}/deployments/${deploymentName}/scale?namespace=${namespace}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ replicas: targetReplicas })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeScaleDeploymentModal();
            showToast(`容器伸缩成功，目标副本数: ${targetReplicas}`, 'success');
            // 重新加载工作负载数据
            loadTabData('deployments');
        } else {
            showToast('容器伸缩失败: ' + result.error, 'error');
        }
    })
    .catch(error => {
        console.error('容器伸缩失败:', error);
        showToast('容器伸缩失败', 'error');
    });
}

// 编辑集群名称相关功能
function editClusterName(clusterName, listItem) {
    // 获取集群名称元素和编辑图标
    const nameSpan = listItem.querySelector('.cluster-name');
    const editIcon = listItem.querySelector('.edit-icon');
    
    // 保存原始名称
    const originalName = nameSpan.textContent;
    
    // 创建输入框
    const input = document.createElement('input');
    input.type = 'text';
    input.value = originalName;
    input.className = 'cluster-name-input';
    
    // 创建保存按钮
    const saveBtn = document.createElement('button');
    saveBtn.textContent = '保存';
    saveBtn.className = 'save-btn';
    
    // 替换显示元素为输入框和保存按钮
    listItem.replaceChild(input, nameSpan);
    listItem.insertBefore(saveBtn, editIcon);
    
    // 隐藏编辑图标
    editIcon.style.display = 'none';
    
    // 聚焦到输入框
    input.focus();
    
    // 绑定保存事件
    saveBtn.onclick = function() {
        const newName = input.value.trim();
        
        if (!newName) {
            showToast('集群名称不能为空', 'warning');
            return;
        }
        
        if (newName === originalName) {
            // 名称未改变，直接取消编辑
            cancelEditClusterName(listItem, originalName, editIcon);
            return;
        }
        
        // 调用API更新集群名称
        updateClusterName(originalName, newName, listItem, editIcon);
    };
    
    // 绑定回车键事件
    input.onkeypress = function(e) {
        if (e.key === 'Enter') {
            saveBtn.click();
        }
    };
    
    // 绑定失去焦点事件（可选，用户可以根据需要决定是否启用）
    /*
    input.onblur = function() {
        // 延迟执行，确保点击保存按钮的事件先触发
        setTimeout(() => {
            if (document.contains(listItem)) {
                cancelEditClusterName(listItem, originalName, editIcon);
            }
        }, 200);
    };
    */
}

function cancelEditClusterName(listItem, originalName, editIcon) {
    // 恢复原始显示
    const nameSpan = document.createElement('span');
    nameSpan.className = 'cluster-name';
    nameSpan.textContent = originalName;
    
    // 移除输入框和保存按钮
    const input = listItem.querySelector('input');
    const saveBtn = listItem.querySelector('.save-btn');
    
    if (input) listItem.removeChild(input);
    if (saveBtn) listItem.removeChild(saveBtn);
    
    // 恢复编辑图标
    editIcon.style.display = '';
    
    // 插入名称显示元素
    listItem.insertBefore(nameSpan, editIcon);
}

function updateClusterName(oldName, newName, listItem, editIcon) {
    // 构造集群ID（与后端保持一致）
    const clusterId = oldName.toLowerCase().replace(' ', '-');
    
    fetch(`/api/clusters/${clusterId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: newName })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showToast('集群名称更新成功', 'success');
            
            // 更新显示
            const nameSpan = document.createElement('span');
            nameSpan.className = 'cluster-name';
            nameSpan.textContent = newName;
            
            // 移除输入框和保存按钮
            const input = listItem.querySelector('input');
            const saveBtn = listItem.querySelector('.save-btn');
            
            if (input) listItem.removeChild(input);
            if (saveBtn) listItem.removeChild(saveBtn);
            
            // 恢复编辑图标
            editIcon.style.display = '';
            
            // 插入新名称
            listItem.insertBefore(nameSpan, editIcon);
            
            // 更新data属性
            listItem.dataset.clusterId = newName.toLowerCase().replace(' ', '-');
            
            // 如果当前选中的集群是这个集群，更新currentCluster变量
            if (currentCluster === clusterId) {
                currentCluster = newName.toLowerCase().replace(' ', '-');
            }
            
            // 重新加载集群列表以确保一致性
            loadClusters();
        } else {
            showToast('集群名称更新失败: ' + (result.error || ''), 'error');
            cancelEditClusterName(listItem, oldName, editIcon);
        }
    })
    .catch(error => {
        console.error('更新集群名称失败:', error);
        showToast('更新集群名称失败', 'error');
        cancelEditClusterName(listItem, oldName, editIcon);
    });
}

// 隐藏所有下拉菜单
function hideAllDropdowns() {
    document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.style.display = 'none';
    });
}

// 点击页面其他地方隐藏下拉菜单
document.addEventListener('click', function() {
    hideAllDropdowns();
});

// 删除集群相关功能
let clusterToDelete = null;

function showDeleteClusterModal(clusterName) {
    clusterToDelete = clusterName;
    document.getElementById('delete-cluster-name').textContent = clusterName;
    document.getElementById('delete-cluster-modal').style.display = 'block';
}

function closeDeleteClusterModal() {
    clusterToDelete = null;
    document.getElementById('delete-cluster-modal').style.display = 'none';
}

function confirmDeleteCluster() {
    if (!clusterToDelete) {
        showToast('无效的操作', 'error');
        return;
    }
    
    const clusterId = clusterToDelete.toLowerCase().replace(' ', '-');
    
    fetch(`/api/clusters/${clusterId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            closeDeleteClusterModal();
            showToast(`集群 ${clusterToDelete} 已成功删除`, 'success');
            // 重新加载集群列表
            loadClusters();
        } else {
            showToast('删除集群失败: ' + (result.error || ''), 'error');
        }
    })
    .catch(error => {
        console.error('删除集群失败:', error);
        showToast('删除集群失败', 'error');
    });
}