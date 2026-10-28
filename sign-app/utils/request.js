// request.js

// 环境配置，根据你的实际需求修改
const baseUrl = 'http://127.0.0.1:8000/';
const wsBaseUrl = 'ws://127.0.0.1:8002/';

// 修改 baseUrl 导出
export function getServerUrl() {
    return baseUrl;
}

// 获取WebSocket URL
export function getWebSocketUrl() {
    return wsBaseUrl;
}

// 创建请求方法
const httpService = {
  interceptors: {
    request: null,
    response: null
  },
  request(config) {
    const defaultConfig = {
      url: '',
      method: 'GET',
      data: {},
      header: {
        'Content-Type': 'application/json'
      }
    };

    // 合并配置
    const finalConfig = {
      ...defaultConfig,
      ...config,
      url: baseUrl + config.url
    };

    // 添加token到header
    const token = uni.getStorageSync('token');
    if (token) {
      finalConfig.header.AUTHORIZATION = token;
    }

    return new Promise((resolve, reject) => {
      uni.request({
        ...finalConfig,
        success: (response) => {
          resolve(response.data);
        },
        fail: (error) => {
          reject(error);
        }
      });
    });
  },

  get(url, params = {}) {
    return this.request({
      url,
      method: 'GET',
      data: params
    });
  },

  login(url, data = {}) {
    // 将data转换为查询字符串
    const queryString = Object.keys(data)
      .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(data[key])}`)
      .join('&');

    return this.request({
      url: queryString ? `${url}?${queryString}` : url,
      method: 'POST'
    });
  },

  post(url, data = {}) {
    return this.request({
      url,
      method: 'POST',
      data: data
    });
  },

  del(url, data = {}, config = {}) {
    return this.request(Object.assign({}, config, {
      url,
      method: 'DELETE',
      data
    }));
  },

  put(url, data = {}, config = {}) {
    return this.request(Object.assign({}, config, {
      url,
      method: 'PUT',
      data
    }));
  },

  // 文件上传
  uploadFile(url, filePath, name = 'file', data = {}, header = {}) {
    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: baseUrl + url,
        filePath,
        name,
        formData: data,
        header: Object.assign({
          'Authorization': `Bearer ${uni.getStorageSync('token')}`
        }, header),
        success: (res) => {
          try {
            const response = JSON.parse(res.data);
            resolve(response);
          } catch (e) {
            reject(new Error('上传文件响应解析失败'));
          }
        },
        fail: (err) => {
          reject(err);
        }
      });
    });
  }
};

// 设置请求和响应拦截器
httpService.interceptors.request = function(config) {
  // 在发送请求之前做些什么，比如显示加载提示
  uni.showLoading({
    title: '加载中'
  });
  return config;
};

httpService.interceptors.response = function(response) {
  // 对响应数据做点什么，比如隐藏加载提示
  uni.hideLoading();
  // 处理401未授权状态
  if (response.statusCode === 401) {
    uni.showToast({
      title: '未授权，请重新登录',
      icon: 'none'
    });
    setTimeout(() => {
      uni.navigateTo({
        url: '/pages/login/login'
      });
    }, 1000);
  }
  return response;
};

export default httpService;