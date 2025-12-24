# K8s 可视化管理平台

基于 Vue 3 + Element Plus + Flask 的 Kubernetes 集群管理平台。

## 项目结构

```
k8s-manage/
├── api/                    # 后端代码
│   ├── app.py             # Flask 应用主文件
│   ├── crypto_utils.py    # 加密工具
│   ├── k8s_client_svc.py  # K8s 客户端服务
│   └── ssh_client.py      # SSH 客户端
├── app/                    # 前端代码
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面视图
│   │   ├── api/           # API 接口
│   │   ├── router/        # 路由配置
│   │   ├── store/         # Vuex 状态管理
│   │   ├── App.vue        # 根组件
│   │   └── main.js        # 入口文件
│   ├── package.json       # 前端依赖
│   └── vite.config.js     # Vite 配置
├── run.py                  # 启动文件
└── requirements.txt       # Python 依赖
```

## 功能特性

- ✅ 支持 SSH 和 KUBE (kubeconfig) 两种连接方式
- ✅ 集群管理（添加、删除、重命名）
- ✅ 命名空间管理
- ✅ 工作负载（Deployments）管理
- ✅ 服务（Services）查看
- ✅ Pods 管理（查看日志、删除）
- ✅ 镜像更新
- ✅ 容器伸缩
- ✅ 批量镜像更新

## 安装和运行

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
cd app
npm install
```

### 3. 开发模式运行

**方式一：分别启动前后端（推荐开发时使用）**

终端1 - 启动后端：
```bash
python run.py
```

终端2 - 启动前端开发服务器：
```bash
cd app
npm run dev
```

访问：http://localhost:3000

**方式二：仅启动后端（生产模式）**

先构建前端：
```bash
cd app
npm run build
```

然后启动后端（会自动服务前端静态文件）：
```bash
python run.py
```

访问：http://localhost:5000

## 使用说明

### 添加集群

1. 点击侧边栏的 "+" 按钮
2. 选择连接方式：
   - **SSH**: 通过跳板机连接，需要填写 SSH 配置
   - **KUBE**: 直接使用 kubeconfig，可填写路径或留空使用默认 `~/.kube/config`
3. 填写集群名称和默认命名空间
4. 根据连接方式填写相应配置
5. 点击确定保存

### 管理资源

- **工作负载**: 查看、更新镜像、容器伸缩
- **服务**: 查看服务列表
- **Pods**: 查看、查看日志、删除

## 技术栈

- **前端**: Vue 3, Element Plus, Vite, Vue Router, Vuex, Axios
- **后端**: Flask, Flask-CORS
- **K8s**: kubernetes Python SDK, paramiko (SSH)

## 注意事项

- 配置文件 `.clusters.yaml` 和加密密钥 `.crypto.key` 会保存在项目根目录
- SSH 密码会被加密存储
- 确保有相应的 K8s 集群访问权限

