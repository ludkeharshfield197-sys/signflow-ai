<template>
	<view class="login-container">
		<view class="login-header">
			<view class="login-logo">
				<uni-icons type="contact" size="30"></uni-icons>
			</view>
			<text class="login-title">手语识别系统</text>
			<text class="login-subtitle">欢迎登录您的账号</text>
		</view>
		
		<view class="login-form">
			<view class="form-item">
				<view class="input-icon">
					<uni-icons type="person" size="30"></uni-icons>
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
					<uni-icons type="locked" size="30"></uni-icons>
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


			
	<!-- 		<view class="form-options">
				<view class="remember-me" @tap="toggleRememberMe">
					<view class="custom-checkbox" :class="{'checked': loginForm.rememberMe}">
						<uni-icons v-if="loginForm.rememberMe" type="checkbox-filled" size="18" color="#3a7bd5"></uni-icons>
						<uni-icons v-else type="circle" size="18" color="#999"></uni-icons>
					</view>
					<text class="checkbox-label">记住密码</text>
				</view>
			</view> -->
			
			<view class="form-item btn-item">
				<button 
					class="login-btn" 
					:class="{'btn-loading': loading}" 
					@tap="handleLogin"
				>
					<text class="btn-text" v-if="!loading">登 录</text>
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
import request from '../../utils/request.js';

export default {
	data() {
		return {
			loginForm: {
				username: '',
				password: '',
				rememberMe: false
			},
			loading: false,
			showPassword: false,
			focusField: '',
			needCaptcha: false, // 是否需要验证码
			codeUrl: '', // 验证码图片URL
		}
	},
	onLoad(options) {
		// 加载保存的登录信息
		this.loadSavedLoginInfo();
		
		// 处理从注册页面传递来的参数
		if (options.username && options.password) {
			this.loginForm.username = decodeURIComponent(options.username);
			this.loginForm.password = decodeURIComponent(options.password);
			// 自动设置记住密码
			this.loginForm.rememberMe = true;
		}
	},
	methods: {
		// 加载保存的登录信息
		loadSavedLoginInfo() {
			try {
				console.log('尝试加载保存的登录信息...');
				const savedLoginInfo = uni.getStorageSync('savedLoginInfo');
				console.log('读取到的存储信息:', savedLoginInfo);
				
				if (savedLoginInfo) {
					const loginInfo = JSON.parse(savedLoginInfo);
					console.log('解析后的登录信息:', loginInfo);
					
					if (loginInfo && loginInfo.username) {
						this.loginForm.username = loginInfo.username;
						this.loginForm.password = loginInfo.password || '';
						this.loginForm.rememberMe = true;
						console.log('已加载保存的登录信息，用户名:', loginInfo.username);
					}
				} else {
					console.log('没有找到保存的登录信息');
				}
			} catch (e) {
				console.error('读取保存的登录信息失败:', e);
				// 出错时清除可能损坏的数据
				uni.removeStorageSync('savedLoginInfo');
			}
		},
		
		// 保存登录信息
		saveLoginInfo() {
			console.log('准备保存登录信息, 记住密码状态:', this.loginForm.rememberMe);
			
			try {
				if (this.loginForm.rememberMe) {
					// 只有当用户名和密码都有值时才保存
					if (this.loginForm.username && this.loginForm.password) {
						const loginInfo = {
							username: this.loginForm.username,
							password: this.loginForm.password
						};
						
						console.log('将保存登录信息:', JSON.stringify(loginInfo));
						
						// 先尝试清除旧数据
						uni.removeStorageSync('savedLoginInfo');
						// 然后保存新数据
						uni.setStorageSync('savedLoginInfo', JSON.stringify(loginInfo));
						
						// 验证数据是否成功保存
						const savedData = uni.getStorageSync('savedLoginInfo');
						console.log('验证保存的数据:', savedData);
						
						if (savedData) {
							console.log('登录信息保存成功');
						} else {
							console.error('登录信息保存失败，存储可能未成功写入');
						}
					} else {
						console.warn('用户名或密码为空，不保存登录信息');
					}
				} else {
					// 如果不记住密码，则清除保存的信息
					console.log('不记住密码，清除已保存的登录信息');
					uni.removeStorageSync('savedLoginInfo');
				}
			} catch (e) {
				console.error('保存/清除登录信息失败:', e);
				// 尝试使用替代方法
				try {
					if (this.loginForm.rememberMe) {
						uni.setStorage({
							key: 'savedLoginInfo',
							data: JSON.stringify({
								username: this.loginForm.username,
								password: this.loginForm.password
							}),
							success: function() {
								console.log('使用异步方法保存登录信息成功');
							},
							fail: function(err) {
								console.error('使用异步方法保存失败:', err);
							}
						});
					} else {
						uni.removeStorage({
							key: 'savedLoginInfo',
							success: function() {
								console.log('使用异步方法清除登录信息成功');
							}
						});
					}
				} catch (err) {
					console.error('尝试使用异步方法也失败:', err);
				}
			}
		},
		
		// 处理记住密码选项变化
		toggleRememberMe() {
			this.loginForm.rememberMe = !this.loginForm.rememberMe;
			console.log('记住密码设置为:', this.loginForm.rememberMe);
		},
		
		async handleLogin() {
			if(!this.loginForm.username || !this.loginForm.password) {
				uni.showToast({
					title: '请输入账号和密码',
					icon: 'none'
				});
				return;
			}

			this.loading = true;
			try {
				// 直接传入参数对象
				const res = await request.login('user/login', {
					username: this.loginForm.username,
					password: this.loginForm.password
				});

				if(res.code === 200) {
					console.log('登录成功，处理记住密码...');
					
					// 保存登录信息（如果选择了记住密码）
					this.saveLoginInfo();
					
					// 保存token和用户信息
					uni.setStorageSync('token', res.token);
					uni.setStorageSync('currentUser', JSON.stringify(res.user));
					// 保存角色和菜单信息
					if(res.roles) {
						uni.setStorageSync('roles', res.roles);
					}
					if(res.menuList) {
						uni.setStorageSync('menuList', JSON.stringify(res.menuList));
					}
					
					uni.showToast({
						title: '登录成功',
						icon: 'success',
						duration: 1500
					});
					
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/index/index'
						});
					}, 1500);
				} else {
					uni.showToast({
						title: res.info || '登录失败',
						icon: 'none'
					});
				}
			} catch(err) {
				console.error('登录错误:', err);
				uni.showToast({
					title: '登录失败，请稍后重试',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		},

	

		togglePasswordVisibility() {
			this.showPassword = !this.showPassword;
		},

		inputFocus(field) {
			this.focusField = field;
		},

		inputBlur() {
			this.focusField = '';
		},

		goToRegister() {
			uni.navigateTo({
				url: '/pages/register/register'
			});
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
	background-color: #f5f7fa;
	border-radius: 12rpx;
	padding: 4rpx;
	transition: all 0.3s ease;
}

.form-item.code-item {
	margin-bottom: 40rpx;
}

.input-icon {
	width: 80rpx;
	height: 80rpx;
	display: flex;
	justify-content: center;
	align-items: center;
}

.input-icon .iconfont {
	font-size: 36rpx;
	color: #909399;
}

input {
	flex: 1;
	height: 80rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #303133;
	background: transparent;
}

input.input-focus {
	background-color: #ffffff;
	box-shadow: 0 0 0 2rpx #409eff;
	border-radius: 12rpx;
}

.password-toggle {
	width: 80rpx;
	height: 80rpx;
	display: flex;
	justify-content: center;
	align-items: center;
}

.password-toggle .iconfont {
	font-size: 36rpx;
	color: #909399;
}

.captcha-img {
	width: 200rpx;
	height: 80rpx;
	border-radius: 8rpx;
	margin-right: 4rpx;
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

.custom-checkbox {
	width: 36rpx;
	height: 36rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 8rpx;
}

.checkbox-label {
	font-size: 26rpx;
	color: #606266;
}

.btn-item {
	margin-bottom: 30rpx;
}

.login-btn {
	width: 100%;
	height: 88rpx;
	background: linear-gradient(135deg, #3a7bd5, #00d2ff);
	border-radius: 44rpx;
	display: flex;
	justify-content: center;
	align-items: center;
	color: #ffffff;
	font-size: 32rpx;
	font-weight: 500;
	transition: all 0.3s ease;
}

.login-btn.btn-loading {
	opacity: 0.8;
}

.btn-text {
	color: #ffffff;
}

.loader {
	width: 36rpx;
	height: 36rpx;
	border: 4rpx solid #ffffff;
	border-top-color: transparent;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
}

@keyframes spin {
	0% { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}

.register-link {
	display: flex;
	justify-content: center;
	align-items: center;
	font-size: 26rpx;
	color: #606266;
}

.register-link .link {
	color: #409eff;
	margin-left: 8rpx;
}

.login-footer {
	position: absolute;
	bottom: 40rpx;
	left: 0;
	right: 0;
	display: flex;
	justify-content: center;
	align-items: center;
}

.login-footer text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}
</style>