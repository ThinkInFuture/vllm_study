// vLLM Ascend 项目文档导航脚本

// 页面配置
const pages = {
    'index': { title: '架构总览', name: '架构总览' },
    'core': { title: '核心模块', name: '核心模块' },
    'models': { title: '模型定义', name: '模型定义' },
    'attention': { title: '注意力机制', name: '注意力机制' },
    'ops': { title: '自定义算子', name: '自定义算子' },
    'worker': { title: '工作节点', name: '工作节点' },
    'distributed': { title: '分布式', name: '分布式' },
    'quantization': { title: '量化', name: '量化' },
    'patch': { title: '补丁模块', name: '补丁模块' }
};

// 获取当前页面标识
function getCurrentPage() {
    const path = window.location.pathname;
    const filename = path.split('/').pop();
    return filename.replace('.html', '') || 'index';
}

// 生成导航栏HTML
function generateNavbar() {
    const currentPage = getCurrentPage();
    
    let navHTML = `
    <nav class="navbar">
        <a href="index.html" class="navbar-brand">vLLM Ascend 文档</a>
        <ul class="navbar-nav">
    `;
    
    for (const [key, value] of Object.entries(pages)) {
        const isActive = key === currentPage ? 'active' : '';
        navHTML += `<li><a href="${key}.html" class="${isActive}">${value.name}</a></li>`;
    }
    
    navHTML += `
        </ul>
    </nav>
    `;
    
    return navHTML;
}

// 插入导航栏
function insertNavbar() {
    const container = document.querySelector('.container');
    if (container) {
        const navbarHTML = generateNavbar();
        container.insertAdjacentHTML('afterbegin', navbarHTML);
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    insertNavbar();
    
    // 添加当前页面标题
    const currentPage = getCurrentPage();
    const pageInfo = pages[currentPage];
    if (pageInfo) {
        document.title = `${pageInfo.title} - vLLM Ascend 文档`;
    }
});

// 导出工具函数
window.VllmDocs = {
    pages,
    getCurrentPage,
    generateNavbar
};