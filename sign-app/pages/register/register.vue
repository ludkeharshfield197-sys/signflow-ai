<template>
	<view class="register-container">
		<view class="register-header">
			<view class="register-logo">
				<uni-icons type="contact" size="30"></uni-icons>
			</view>
			<text class="register-title">手语识别系统</text>
			<text class="register-subtitle">创建新账号</text>
		</view>
		
		<view class="register-form">
			<view class="form-item">
				<view class="input-icon">
					<uni-icons type="person" size="30"></uni-icons>
				</view>
				<input 
					type="text" 
					v-model="registerForm.username" 
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
					v-model="registerForm.password" 
					placeholder="请输入密码" 
					@focus="inputFocus('password')" 
					@blur="inputBlur('password')"
					:class="{'input-focus': focusField === 'password'}"
				/>
				<view class="password-toggle" @tap="togglePasswordVisibility">
					<uni-icons :type="showPassword ? 'eye-filled' : 'eye-slash-filled'" size="24" color="#999"></uni-icons>
				</view>
			</view>
			<view class="form-item">
				<view class="input-icon">
					<uni-icons type="locked" size="30"></uni-icons>
				</view>
				<input 
					:type="showConfirmPassword ? 'text' : 'password'" 
					v-model="registerForm.confirmPassword" 
					placeholder="请确认密码" 
					@focus="inputFocus('confirmPassword')" 
					@blur="inputBlur('confirmPassword')"
					:class="{'input-focus': focusField === 'confirmPassword'}"
				/>
				<view class="password-toggle" @tap="toggleConfirmPasswordVisibility">
					<uni-icons :type="showConfirmPassword ? 'eye-filled' : 'eye-slash-filled'" size="24" color="#999"></uni-icons>
				</view>
			</view>
			
			<view class="form-item btn-item">
				<button 
					class="register-btn" 
					:class="{'btn-loading': loading}" 
					@tap="handleRegister"
				>
					<text class="btn-text" v-if="!loading">注 册</text>
					<view class="loader" v-else></view>
				</button>
			</view>
			
			<view class="login-link">
				<text>已有账号？</text>
				<text class="link" @tap="goToLogin">立即登录</text>
			</view>
		</view>
		
		<view class="register-footer">
			<text>Copyright © 2023-2025 鹿津愉 版权所有.</text>
		</view>
	</view>
</template>

<script>
import request from '../../utils/request.js';

export default {
	data() {
		return {
			registerForm: {
				username: '',
				password: '',
				confirmPassword: ''
			},
			loading: false,
			showPassword: false,
			showConfirmPassword: false,
			focusField: ''
		}
	},
	methods: {
		// 处理注册
		async handleRegister() {
			// 表单验证
			if (!this.registerForm.username.trim()) {
				uni.showToast({
					title: '请输入账号',
					icon: 'none'
				});
				return;
			}
			if (!this.registerForm.password) {
				uni.showToast({
					title: '请输入密码',
					icon: 'none'
				});
				return;
			}
			if (this.registerForm.password.length < 6) {
				uni.showToast({
					title: '密码长度不能少于6位',
					icon: 'none'
				});
				return;
			}
			if (!this.registerForm.confirmPassword) {
				uni.showToast({
					title: '请确认密码',
					icon: 'none'
				});
				return;
			}
			if (this.registerForm.password !== this.registerForm.confirmPassword) {
				uni.showToast({
					title: '两次输入的密码不一致',
					icon: 'none'
				});
				return;
			}
			
			this.loading = true;
			try {
				const result = await request.post('user/register', {
					username: this.registerForm.username.trim(),
					password: this.registerForm.password,
					confirmPassword: this.registerForm.confirmPassword
				});
				
				if (result.code === 200) {
					uni.showToast({
						title: '注册成功',
						icon: 'success'
					});
					
					setTimeout(() => {
						// 将注册的账号密码作为参数传递给登录页面
						uni.redirectTo({
							url: `/pages/login/login?username=${encodeURIComponent(this.registerForm.username.trim())}&password=${encodeURIComponent(this.registerForm.password)}`
						});
					}, 1500);
				} else {
					uni.showToast({
						title: result.info || '注册失败',
						icon: 'none'
					});
				}
			} catch (error) {
				console.error('注册错误:', error);
				uni.showToast({
					title: '注册失败，请稍后再试',
					icon: 'none'
				});
			} finally {
				this.loading = false;
			}
		},
		
		// 切换密码显示状态
		togglePasswordVisibility() {
			this.showPassword = !this.showPassword;
		},
		
		// 切换确认密码显示状态
		toggleConfirmPasswordVisibility() {
			this.showConfirmPassword = !this.showConfirmPassword;
		},
		
		// 输入框获取焦点
		inputFocus(field) {
			this.focusField = field;
		},
		
		// 输入框失去焦点
		inputBlur() {
			this.focusField = '';
		},
		
		// 跳转到登录页面
		goToLogin() {
			uni.navigateTo({
				url: '/pages/login/login'
			});
		}
	}
}
</script>

<style>
.register-container {
	display: flex;
	flex-direction: column;
	min-height: 100vh;
	padding: 30rpx;
	background: linear-gradient(135deg, #3a7bd5, #00d2ff);
	position: relative;
}

.register-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 0;
}

.register-logo {
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

.register-title {
	font-size: 42rpx;
	font-weight: bold;
	color: #ffffff;
	margin-bottom: 16rpx;
}

.register-subtitle {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
}

.register-form {
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

.input-icon {
	width: 80rpx;
	height: 80rpx;
	display: flex;
	justify-content: center;
	align-items: center;
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

.btn-item {
	margin-top: 40rpx;
}

.register-btn {
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

.register-btn.btn-loading {
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

.login-link {
	text-align: center;
	font-size: 28rpx;
	color: #606266;
	margin-top: 20rpx;
}

.link {
	color: #409eff;
	margin-left: 8rpx;
}

.register-footer {
	position: absolute;
	bottom: 40rpx;
	left: 0;
	right: 0;
	text-align: center;
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}
</style>