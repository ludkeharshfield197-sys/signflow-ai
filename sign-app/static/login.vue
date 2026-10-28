<template>
	<view class="login-container">
		<view class="login-header">
			<view class="login-logo">
				<image src="/static/logo.png" mode="aspectFit"></image>
			</view>
			<text class="login-title">手语识别系统</text>
			<text class="login-subtitle">欢迎登录您的账号</text>
		</view>
		
		<view class="login-form">
			<view class="form-item">
				<view class="input-icon">
					<text class="iconfont icon-user"></text>
				</view>
				<input 
					type="text" 
					v-model="loginForm.username" 
					placeholder="请输入账号" 
					@focus="inputFocus('username')" 
					@blur="inputBlur('username')"
					:class="{'input-focus': focusField === 'username'}"
				/>
			</view>
			<view class="form-item">
				<view class="input-icon">
					<text class="iconfont icon-lock"></text>
				</view>
				<input 
					:type="showPassword ? 'text' : 'password'" 
					v-model="loginForm.password" 
					placeholder="请输入密码" 
					@focus="inputFocus('password')" 
					@blur="inputBlur('password')"
					:class="{'input-focus': focusField === 'password'}"
				/>
				<view class="password-toggle" @tap="togglePasswordVisibility">
					<text class="iconfont" :class="showPassword ? 'icon-eye' : 'icon-eye-close'"></text>
				</view>
			</view>
			<view class="form-item code-item" v-if="needCaptcha">
				<view class="input-icon">
					<text class="iconfont icon-safetycertificate"></text>
				</view>
				<input 
					type="text" 
					v-model="loginForm.code" 
					placeholder="请输入验证码" 
					@focus="inputFocus('code')" 
					@blur="inputBlur('code')"
					:class="{'input-focus': focusField === 'code'}"
				/>
				<image class="captcha-img" :src="codeUrl" @tap="getCode"></image>
			</view>
			
			<view class="form-options">
				<view class="remember-me">
					<view class="checkbox-wrapper" @tap="loginForm.rememberMe = !loginForm.rememberMe">
						<view class="custom-checkbox" :class="{'checked': loginForm.rememberMe}">
							<text class="iconfont icon-check" v-if="loginForm.rememberMe"></text>
						</view>
						<text class="checkbox-label">记住密码</text>
					</view>
				</view>
			</view>
			
			<view class="form-item btn-item">
				<button 
					class="login-btn" 
					:class="{'btn-loading': isLoading}" 
					@tap="handleLogin"
				>
					<text class="btn-text" v-if="!isLoading">登 录</text>
					<view class="loader" v-else></view>
				</button>
			</view>
			
			<view class="register-link">
				<text>没有账号？</text>
				<text class="link" @tap="goToRegister">立即注册</text>
			</view>
		</view>
		
		<view class="login-footer">
			<text>Copyright © 2013-2025 鹿津愉 版权所有.</text>
		</view>
	</view>
</template>

<script>
import { get, post } from '@/utils/request';

export default {
	data() {
		return {
			loginForm: {
				username: '',
				password: '',
				code: '',
				uuid: '',
				rememberMe: false
			},
			codeUrl: '',
			focusField: '',
			showPassword: false,
			isLoading: false,
			needCaptcha: true // 是否需要验证码，根据实际需求设置
		}
	},
	onLoad() {
		// 检查是否有记住的用户名和密码
		this.getSavedCredentials();
		// 获取验证码
		if (this.needCaptcha) {
			this.getCode();
		}
	},
	methods: {
		// 获取保存的凭证
		getSavedCredentials() {
			try {
				const savedUsername = uni.getStorageSync('savedUsername');
				const savedPassword = uni.getStorageSync('savedPassword');
				if (savedUsername && savedPassword) {
					this.loginForm.username = savedUsername;
					this.loginForm.password = savedPassword;
					this.loginForm.rememberMe = true;
				}
			} catch (e) {
				console.error('获取保存的登录信息失败:', e);
			}
		},
		
		// 保存凭证
		saveCredentials() {
			if (this.loginForm.rememberMe) {
				try {
					uni.setStorageSync('savedUsername', this.loginForm.username);
					uni.setStorageSync('savedPassword', this.loginForm.password);
				} catch (e) {
					console.error('保存登录信息失败:', e);
				}
			} else {
				// 清除保存的信息
				try {
					uni.removeStorageSync('savedUsername');
					uni.removeStorageSync('savedPassword');
				} catch (e) {
					console.error('清除登录信息失败:', e);
				}
			}
		},
		
		// 获取验证码
		async getCode() {
			try {
				const result = await get('/user/captcha');
				console.log('验证码结果:', result);
				if (result.data && result.data.base64str) {
					this.loginForm.uuid = result.data.uuid;
					this.codeUrl = result.data.base64str;
				} else {
					uni.showToast({
						title: '获取验证码失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('获取验证码异常:', error);
				uni.showToast({
					title: '获取验证码失败',
					icon: 'none'
				});
			}
		},
		
		// 处理登录
		async handleLogin() {
			// 表单验证
			if (!this.loginForm.username) {
				uni.showToast({
					title: '请输入用户名',
					icon: 'none'
				});
				return;
			}
			
			if (!this.loginForm.password) {
				uni.showToast({
					title: '请输入密码',
					icon: 'none'
				});
				return;
			}
			
			if (this.needCaptcha && !this.loginForm.code) {
				uni.showToast({
					title: '请输入验证码',
					icon: 'none'
				});
				return;
			}
			
			this.isLoading = true;
			uni.showLoading({
				title: '登录中...',
				mask: true
			});
			
			try {
				// 构建登录参数
				const loginParams = {
					username: this.loginForm.username,
					password: this.loginForm.password
				};
				
				if (this.needCaptcha) {
					loginParams.code = this.loginForm.code;
					loginParams.uuid = this.loginForm.uuid;
				}
				
				console.log('发送登录请求参数:', loginParams);
				
				// 发送登录请求
				const result = await post('user/login', loginParams);
				console.log('登录响应结果:', result);
				
				const data = result.data;
				if (data.code === 200) {
					// 登录成功
					uni.showToast({
						title: data.info || '登录成功',
						icon: 'success'
					});
					
					// 保存token和用户信息
					if (data.token) {
						uni.setStorageSync('token', data.token);
					}
					
					// 保存用户信息
					if (data.user) {
						const currentUser = data.user;
						if (data.roles) {
							currentUser.roles = data.roles;
						}
						uni.setStorageSync('currentUser', JSON.stringify(currentUser));
					}
					
					// 保存菜单列表
					if (data.menuList) {
						uni.setStorageSync('menuList', JSON.stringify(data.menuList));
					}
					
					// 记住密码处理
					this.saveCredentials();
					
					// 登录成功后跳转到首页
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/index/index'
						});
					}, 1500);
				} else {
					// 登录失败
					uni.showToast({
						title: data.msg || data.info || '登录失败',
						icon: 'none',
						duration: 2000
					});
					
					// 刷新验证码
					if (this.needCaptcha) {
						this.getCode();
					}
				}
			} catch (error) {
				console.error('登录异常:', error);
				
				let errorMsg = '登录失败，请稍后再试';
				if (error.response && error.response.data) {
					errorMsg = error.response.data.msg || error.response.data.info || errorMsg;
				}
				
				uni.showToast({
					title: errorMsg,
					icon: 'none',
					duration: 2000
				});
				
				// 刷新验证码
				if (this.needCaptcha) {
					this.getCode();
				}
			} finally {
				this.isLoading = false;
				uni.hideLoading();
			}
		},
		
		// 跳转到注册页面
		goToRegister() {
			uni.navigateTo({
				url: '/pages/register/register'
			});
		},
		
		// 输入框获取焦点
		inputFocus(field) {
			this.focusField = field;
		},
		
		// 输入框失去焦点
		inputBlur(field) {
			if (this.focusField === field) {
				this.focusField = '';
			}
		},
		
		// 切换密码可见性
		togglePasswordVisibility() {
			this.showPassword = !this.showPassword;
		}
	}
}
</script>

<style>
/* 登录页样式 */
.login-container {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	padding: 30rpx;
	background: linear-gradient(135deg, #3a7bd5, #00d2ff);
	position: relative;
}

.login-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 0;
}

.login-logo {
	width: 160rpx;
	height: 160rpx;
	border-radius: 80rpx;
	background-color: #ffffff;
	display: flex;
	justify-content: center;
	align-items: center;
	box-shadow: 0 8rpx 16rpx rgba(0, 0, 0, 0.1);
	margin-bottom: 30rpx;
}

.login-logo image {
	width: 120rpx;
	height: 120rpx;
}

.login-title {
	font-size: 42rpx;
	font-weight: bold;
	color: #ffffff;
	margin-bottom: 16rpx;
}

.login-subtitle {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
}

.login-form {
	background-color: #ffffff;
	border-radius: 20rpx;
	padding: 40rpx 30rpx;
	margin-bottom: 40rpx;
	box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.form-item {
	position: relative;
	display: flex;
	align-items: center;
	margin-bottom: 30rpx;
	border-bottom: 1px solid #f0f0f0;
	padding: 16rpx 0;
}

.input-icon {
	width: 60rpx;
	display: flex;
	justify-content: center;
}

.form-item input {
	flex: 1;
	height: 80rpx;
	font-size: 30rpx;
	color: #333;
}

.input-focus {
	border-color: #3a7bd5;
}

.password-toggle {
	width: 60rpx;
	display: flex;
	justify-content: center;
	align-items: center;
}

.code-item {
	display: flex;
}

.captcha-img {
	width: 200rpx;
	height: 80rpx;
	margin-left: 20rpx;
	border-radius: 8rpx;
}

.form-options {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 40rpx;
}

.remember-me {
	display: flex;
	align-items: center;
}

.checkbox-wrapper {
	display: flex;
	align-items: center;
}

.custom-checkbox {
	width: 36rpx;
	height: 36rpx;
	border: 1px solid #ddd;
	border-radius: 6rpx;
	margin-right: 16rpx;
	display: flex;
	justify-content: center;
	align-items: center;
}

.custom-checkbox.checked {
	background-color: #3a7bd5;
	border-color: #3a7bd5;
}

.checkbox-label {
	font-size: 28rpx;
	color: #666;
}

.btn-item {
	border-bottom: none;
	margin-top: 20rpx;
}

.login-btn {
	width: 100%;
	height: 90rpx;
	line-height: 90rpx;
	text-align: center;
	background: linear-gradient(to right, #3a7bd5, #00d2ff);
	color: #ffffff;
	font-size: 32rpx;
	border-radius: 45rpx;
	box-shadow: 0 8rpx 16rpx rgba(58, 123, 213, 0.3);
	transition: all 0.3s;
}

.btn-loading {
	opacity: 0.8;
}

.loader {
	width: 36rpx;
	height: 36rpx;
	border: 4rpx solid rgba(255, 255, 255, 0.3);
	border-radius: 50%;
	border-top-color: #ffffff;
	animation: spin 1s linear infinite;
	margin: 0 auto;
	margin-top: 27rpx;
}

@keyframes spin {
	100% {
		transform: rotate(360deg);
	}
}

.register-link {
	text-align: center;
	margin-top: 30rpx;
	font-size: 28rpx;
	color: #666;
}

.link {
	color: #3a7bd5;
	margin-left: 10rpx;
}

.login-footer {
	text-align: center;
	margin-top: auto;
	padding: 30rpx 0;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.7);
}

/* 自定义图标字体样式 */
@font-face {
	font-family: "iconfont";
	src: url('data:application/x-font-woff2;charset=utf-8;base64,d09GMgABAAAAAAO0AAsAAAAACFwAAANoAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHEIGVgCDHAqDaIM0ATYCJAMQCwoABCAFhG0HQhtZB8gOJa3AwABgYFBgPPy3X7vvzczqJtGkmURNJDGdRCONkCCRTqJREiHS7P/Npv0keGh6V0fij5R70AVSzLyYvVTCpbK+l/Mf/zh2el1gednZXFKLoLVGG43HAxrQqPcjyA70H8auvIjVEJDJoI3Izrn5xaAx/OYJILat8UShMRMNhoJRCY4FYxPSDUQVVVkVXgTQFn5ffCIWNJJY8BsXbMzdQMq38DfPwlhYthgrgHw8G4B1CBigETCAHBqdaYdhTRsGmXwvoxuQyUjwLZz96u/XZznyK4GIKWFZor/yQMAjOAWnJtNEnAJvGkjeNJAiAd/CkUDAtzCTCeRlrIjpDfIDGQCUAn3ArAV6f3Lqh1ixl6+j5+5cvnbt5o0bd69dj1r09ZvRs9LhgGOoee7O+JcGKO/OVNGbfLwJSPf1LbfLmL6+/Kh+b2JqBfC1a5dI7qVLl75rRRHduX6d+MllyVfubJuxNW2zcPDRrVu/6Lcf7z+e8u9k++asPkQcFVMk8NvCxa8O/9x8MpY6N/nEn7fnXOHa/f4p1AJqptO+0m3H0wZ7o+PmtW7zy1Wz3WcCF03u+SBj5IHJyxIPJJ6VwUdvvT7y8tCJoS8HD0uNXLdz37Z1kW3H/4y8jRk6+EZCQkLWe/4+6WkVvqZmYbMd9Q8Uf/Hzl1Hx33vSN1LTLr6trJv8Wbb7xJp2rUgobTd4U07ysYTWE9Xl2+VL+iD/3RubMsoW5c5u2e7Z/+o+YPPxVvNa3Jq/bdEiUqrD3mLFBqxKSXrRr/8vNn8x6H+rffS1yksfuiLrQO9efyTWqP37K9+6jTu2atyIYODf7+sHQO5RsgGQ5wpZGoGCSPz9jrwJf5B1h2Ekvzgq9aODVgL83zzSogAveIHB7P81LCkSrEpSsZIqCkQ5v+wbBTL5K0eykNvVpW+RETuCkSQDSeoMYKTU8DvaCGRyGoKjzDDI1LPz9Jx+iIh2AHVlA4RCp0AqdBmYQnf4Hb0HslJ0BUehabBWGLeXnCMYfqQpDEJ9QhUiJY0yvUG2n8Q4F/XJmKsEQ0W4hiEilihWA02iW3iMc+JWFGKDsBDlMW3OzE6h7vCYcGfQ0JrTzOAoaVnTUBRHGYRBQHoJUgGRJA0l8wZi85MwHC9qbX4mgeF0JFqNQkRppQZoJVK36DJOS7mpFLnbhQVBeSE1xyw5FkndkMcSnZOgQdMs5x4DiZRZ1SBR4pYVGOlp2Xyj+j32AmR4lSlJspSiKqlVTNV5D5kVt7hWlnP3HqgFZdwZJw2tYdLQJEpJZ5RsLpINAAAA') format('woff2');
}

.iconfont {
	font-family: "iconfont" !important;
	font-size: 32rpx;
	font-style: normal;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #999;
}

.icon-user:before {
	content: "\e7ae";
}

.icon-lock:before {
	content: "\e7c9";
}

.icon-safetycertificate:before {
	content: "\e7c3";
}

.icon-check:before {
	content: "\e7fc";
}

.icon-eye:before {
	content: "\e78f";
}

.icon-eye-close:before {
	content: "\e8ff";
}
</style>

